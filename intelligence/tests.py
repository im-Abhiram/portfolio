import json
import os
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from intelligence.generator import (
    ArticleValidationError,
    DuplicateArticleError,
    generate_daily_article,
    import_article_from_json_payload,
    validate_article_payload,
)
from intelligence.models import AISettings, ArticleGenerationLog, DailyArticle


SAMPLE_VALID_ARTICLE_JSON = {
    "title": "VLAN Architecture and Network Segmentation Explained",
    "subtitle": "How Layer 2 segmentation isolates broadcast domains and reduces lateral movement.",
    "category": "Networking",
    "tags": ["VLAN", "Segmentation", "Switching", "Network Security"],
    "reading_time": 6,
    "introduction": "Virtual Local Area Networks allow engineers to partition physical switches into isolated broadcast domains.",
    "what_is_it": "A VLAN logically divides a Layer 2 broadcast domain without buying separate switch hardware.",
    "how_it_works": "Switch ports tag frames using IEEE 802.1Q identifiers on trunk links between switches.",
    "technical_explanation": "Inter-VLAN traffic must traverse a Layer 3 gateway or firewall, enabling stateful inspection.",
    "practical_example": "Separating Corporate Workstations on VLAN 20 from Guest Wi-Fi on VLAN 40.",
    "commands_and_configs": [
        {
            "explanation": "In a lab switch environment, inspect currently configured VLANs first.",
            "command": "show vlan brief",
            "environment_note": "Lab Switch Example"
        }
    ],
    "security_implications": "Without VLAN separation and firewall ACLs, a compromised host can probe every asset.",
    "common_mistakes": ["Leaving native VLAN 1 active on trunk links", "Permitting any-to-any inter-VLAN traffic"],
    "prevention_best_practices": ["Move management interfaces to a dedicated VLAN", "Shut unused access ports"],
    "key_takeaways": ["VLANs limit broadcast domains", "Use firewall ACLs between VLANs"],
    "further_learning": ["Dynamic ARP Inspection", "IEEE 802.1Q frame header fields"],
}


class DailyArticleGeneratorTests(TestCase):
    def setUp(self):
        self.ai_cfg = AISettings.load()
        self.ai_cfg.article_publish_mode = 'review'
        self.ai_cfg.save()

    @patch('ai_services.gemini.requests.post')
    def test_article_generation_and_same_day_idempotency(self, mock_post):
        """Calling generation twice on the same date creates only ONE article and skips second run."""
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': json.dumps(SAMPLE_VALID_ARTICLE_JSON)}]}}],
            'usageMetadata': {'totalTokenCount': 450},
        }
        mock_post.return_value = resp

        target = date(2026, 11, 25)
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'valid-key'}, clear=False):
            first = generate_daily_article(target_date=target)
            self.assertEqual(first['status'], 'success')
            self.assertEqual(DailyArticle.objects.count(), 1)
            article = first['article']
            self.assertEqual(article.status, 'pending_review')

            # Second run same day -> skipped (idempotent)
            second = generate_daily_article(target_date=target)
            self.assertEqual(second['status'], 'skipped')
            self.assertEqual(DailyArticle.objects.count(), 1)
            self.assertEqual(ArticleGenerationLog.objects.filter(status='skipped').count(), 1)

    @patch('ai_services.gemini.requests.post')
    def test_management_command_idempotency(self, mock_post):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': json.dumps(SAMPLE_VALID_ARTICLE_JSON)}]}}],
            'usageMetadata': {'totalTokenCount': 300},
        }
        mock_post.return_value = resp

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'valid-key'}, clear=False):
            call_command('generate_daily_article', '--date', '2026-11-24')
            call_command('generate_daily_article', '--date', '2026-11-24')
            self.assertEqual(DailyArticle.objects.filter(scheduled_date=date(2026, 11, 24)).count(), 1)

    @patch('ai_services.gemini.requests.post')
    def test_invalid_gemini_json_logged_gracefully(self, mock_post):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': '{broken json output...'}]}}],
        }
        mock_post.return_value = resp

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'valid-key'}, clear=False):
            result = generate_daily_article(target_date=date(2026, 11, 23))
            self.assertEqual(result['status'], 'failed')
            self.assertEqual(DailyArticle.objects.count(), 0)
            self.assertTrue(ArticleGenerationLog.objects.filter(status='failed').exists())

    def test_article_content_validation_and_sanitization(self):
        # Missing fields rejected
        with self.assertRaises(ArticleValidationError):
            validate_article_payload({'title': 'Too short'})

        # Raw script tags stripped from prose safely
        dirty = dict(SAMPLE_VALID_ARTICLE_JSON)
        dirty['title'] = "XSS Defense <script>alert(1)</script> Overview Explained"
        cleaned = validate_article_payload(dirty)
        self.assertNotIn('<script>', cleaned['title'])

    @patch('ai_services.gemini.requests.post')
    def test_duplicate_article_prevention_across_days(self, mock_post):
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            'candidates': [{'content': {'parts': [{'text': json.dumps(SAMPLE_VALID_ARTICLE_JSON)}]}}],
        }
        mock_post.return_value = resp

        with patch.dict(os.environ, {'GEMINI_API_KEY': 'valid-key'}, clear=False):
            res1 = generate_daily_article(target_date=date(2026, 11, 20))
            self.assertEqual(res1['status'], 'success')

            # Different day, same generated article content -> blocked!
            res2 = generate_daily_article(target_date=date(2026, 11, 21))
            self.assertEqual(res2['status'], 'duplicate_blocked')
            self.assertEqual(DailyArticle.objects.count(), 1)

    def test_json_import_fallback(self):
        art = import_article_from_json_payload(SAMPLE_VALID_ARTICLE_JSON, scheduled_date=date(2026, 11, 19), status='published')
        self.assertEqual(art.status, 'published')
        with self.assertRaises(DuplicateArticleError):
            import_article_from_json_payload(SAMPLE_VALID_ARTICLE_JSON, scheduled_date=date(2026, 11, 18))


class IntelligenceViewsAndAdminPortalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin_op',
            password='AdminPass123!',
            is_staff=True,
            is_active=True
        )
        self.art1 = import_article_from_json_payload(
            SAMPLE_VALID_ARTICLE_JSON,
            scheduled_date=date(2026, 11, 20),
            status='published'
        )
        art2_data = dict(SAMPLE_VALID_ARTICLE_JSON)
        art2_data['title'] = "SQL Injection Prevention in Django Applications"
        art2_data['subtitle'] = "Using parameterized ORM queries cleanly."
        art2_data['category'] = "Web Application Security"
        art2_data['introduction'] = "SQL injection happens when untrusted user input alters query structure."
        self.art2 = import_article_from_json_payload(
            art2_data,
            scheduled_date=date(2026, 11, 21),
            status='pending_review'
        )

    def test_public_search_and_category_filtering(self):
        # Archive displays published art1, hides pending_review art2
        res = self.client.get(reverse('intelligence:list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.art1.title)
        self.assertNotContains(res, self.art2.title)

        # Category filter
        res_cat = self.client.get(reverse('intelligence:list') + '?category=Networking')
        self.assertContains(res_cat, self.art1.title)

        res_empty = self.client.get(reverse('intelligence:list') + '?category=Cybersecurity')
        self.assertNotContains(res_empty, self.art1.title)

        # Search
        res_q = self.client.get(reverse('intelligence:list') + '?q=VLAN')
        self.assertContains(res_q, self.art1.title)

    def test_admin_portal_approval_edit_publish_unpublish(self):
        self.client.login(username='admin_op', password='AdminPass123!')

        # Preview pending_review article works for staff
        res_preview = self.client.get(reverse('intelligence:detail', kwargs={'slug': self.art2.slug}) + '?preview=1')
        self.assertEqual(res_preview.status_code, 200)
        self.assertContains(res_preview, "ADMIN PREVIEW MODE")

        # Edit article in Admin Portal
        edit_url = reverse('portal:intelligence_edit', kwargs={'pk': self.art2.pk})
        post_data = {
            'title': 'SQL Injection Prevention Updated',
            'slug': self.art2.slug,
            'subtitle': self.art2.subtitle,
            'category': 'Web Application Security',
            'status': 'pending_review',
            'reading_time': 7,
            'tags': 'SQLi, Django, Security',
            'introduction': self.art2.introduction,
            'what_is_it': 'Updated explanation of SQL injection.',
            'how_it_works': 'Database drivers bind parameters separately from SQL code.',
            'technical_explanation': 'Django QuerySet API parameterizes arguments safely.',
            'practical_example': 'Using User.objects.filter(username=input_val).',
            'commands_json': json.dumps(self.art2.content['commands_and_configs']),
            'security_implications': 'Prevents arbitrary data extraction.',
            'common_mistakes_text': 'Using string interpolation in cursor.execute',
            'best_practices_text': 'Always use ORM or bound parameters',
            'key_takeaways_text': 'Never concatenate SQL strings',
            'further_learning_text': 'OWASP Injection Prevention Cheat Sheet',
        }
        res_edit = self.client.post(edit_url, post_data)
        self.assertEqual(res_edit.status_code, 302)
        self.art2.refresh_from_db()
        self.assertEqual(self.art2.title, 'SQL Injection Prevention Updated')

        # Approve & Publish
        res_pub = self.client.post(reverse('portal:intelligence_publish', kwargs={'pk': self.art2.pk}))
        self.assertEqual(res_pub.status_code, 302)
        self.art2.refresh_from_db()
        self.assertEqual(self.art2.status, 'published')

        # Now visible publicly on detail & homepage
        res_pub_detail = self.client.get(reverse('intelligence:detail', kwargs={'slug': self.art2.slug}))
        self.assertEqual(res_pub_detail.status_code, 200)
        self.assertContains(res_pub_detail, 'SQL Injection Prevention Updated')

        # Unpublish back to Draft
        res_unpub = self.client.post(reverse('portal:intelligence_unpublish', kwargs={'pk': self.art2.pk}))
        self.assertEqual(res_unpub.status_code, 302)
        self.art2.refresh_from_db()
        self.assertEqual(self.art2.status, 'draft')

    def test_deployment_configs_and_mobile_css(self):
        from django.conf import settings
        self.assertIn('abhiramportfolio.pythonanywhere.com', settings.ALLOWED_HOSTS)
        self.assertIn('intelligence.apps.IntelligenceConfig', settings.INSTALLED_APPS)
        self.assertIn('nexus.apps.NexusConfig', settings.INSTALLED_APPS)

        css_path = os.path.join(settings.BASE_DIR, 'static', 'css', 'ai-modules.css')
        with open(css_path, 'r', encoding='utf-8') as f:
            css = f.read()
        self.assertIn('@media (max-width: 640px)', css)
        self.assertIn('.nexus-chat-panel', css)
