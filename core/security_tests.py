import io
import os
import tempfile
import time
import zipfile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from ai_services.gemini import GeminiClient, ModelUnavailableError
from contact.models import ContactMessage
from core.models import PortfolioSettings
from core.security import _sanitize_log_text, get_client_ip
from core.validators import (
    SafeUploadPath,
    validate_image_file,
    validate_resume_file,
    validate_safe_url,
)
from intelligence.models import DailyArticle
from portal.forms import AISettingsForm
from portal.models import LoginAttemptLog
from portfolio.models import Certification, Experience, Project, Skill, SkillCategory


class SecurityRegressionTests(TestCase):
    """Comprehensive OWASP Top 10 & Django hardening security verification suite."""

    def setUp(self):
        self.client = Client()
        self.rf = RequestFactory()
        self.staff_user = User.objects.create_user(
            username='sec_operator',
            password='Str0ng!Operator#2026',
            is_staff=True,
            is_active=True,
        )
        self.normal_user = User.objects.create_user(
            username='sec_visitor',
            password='Visitor!Password#2026',
            is_staff=False,
            is_active=True,
        )
        self.msg = ContactMessage.objects.create(
            name='Security Tester',
            email='tester@example.com',
            subject='Test Subject',
            message='Test payload.',
            is_read=False,
        )
        self.cat = SkillCategory.objects.create(name='SecCat', slug='sec-cat', order=1)
        self.skill = Skill.objects.create(
            category=self.cat,
            name='Firewalling',
            description='Firewall traffic filtering',
            order=1,
        )
        self.cert = Certification.objects.create(title='CEH', issuer='EC-Council', issue_date='2025', order=1)
        self.exp = Experience.objects.create(
            role='Analyst',
            company='NetCorp',
            duration='2024 - Present',
            summary='Security operations and firewall hardening.',
            responsibilities='SIEM monitoring\nFirewall ACL audit',
            technologies='pfSense, Linux',
            order=1,
        )
        self.project = Project.objects.create(
            title='Zero Trust Proxy',
            slug='zero-trust-proxy',
            category='Security',
            badge_label='LAB',
            summary='Summary text',
            architecture='Arch',
            key_features='Feat1',
            challenges_and_solutions='Chall',
            technologies='Django',
            order=1,
        )
        self.article = DailyArticle.objects.create(
            title='Zero Trust Telemetry',
            slug='zero-trust-telemetry',
            subtitle='Defense in depth telemetry overview',
            introduction='Introduction paragraph.',
            content={'what_is_it': 'Telemetry concept.', 'technical_explanation': 'Content body.'},
            category='Cybersecurity',
            status='pending_review',
        )

    # 1. Broken Access Control
    def test_anonymous_and_non_staff_blocked_from_portal_and_admin_endpoints(self):
        protected_gets = [
            reverse('portal:dashboard'),
            reverse('portal:messages'),
            reverse('portal:profile_edit'),
            reverse('portal:settings_edit'),
            reverse('portal:projects_list'),
            reverse('portal:intelligence_list'),
            reverse('portal:ai_settings'),
            reverse('portal:journal_list'),
            '/sys-admin/',
        ]
        # Anonymous context
        for url in protected_gets:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 302, f"Expected redirect for anonymous on {url}")

        # Normal non-staff user context
        self.client.login(username='sec_visitor', password='Visitor!Password#2026')
        for url in protected_gets:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 302, f"Expected non-staff block on {url}")

        # Non-staff cannot invoke admin POST mutations
        protected_posts = [
            reverse('portal:intelligence_generate'),
            reverse('portal:intelligence_publish', kwargs={'pk': self.article.pk}),
            reverse('portal:intelligence_delete', kwargs={'pk': self.article.pk}),
            reverse('portal:message_delete', kwargs={'pk': self.msg.pk}),
            reverse('portal:project_delete', kwargs={'pk': self.project.pk}),
        ]
        for url in protected_posts:
            resp = self.client.post(url)
            self.assertEqual(resp.status_code, 302)

        self.assertTrue(ContactMessage.objects.filter(pk=self.msg.pk).exists())
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())
        self.assertEqual(DailyArticle.objects.get(pk=self.article.pk).status, 'pending_review')

    # 2. CAPTCHA Enforcement on /sys-admin/login/ and /admin/login/
    def test_sys_admin_login_enforces_captcha_gui(self):
        for path in ('/admin/login/', '/sys-admin/login/'):
            resp = self.client.get(path)
            self.assertEqual(resp.status_code, 200)
            self.assertContains(resp, 'OPERATOR ACCESS')
            self.assertContains(resp, 'Security Verification Challenge')

            # Attempting login without valid CAPTCHA must fail even with valid password
            fail_resp = self.client.post(path, {
                'username': 'sec_operator',
                'password': 'Str0ng!Operator#2026',
                'captcha': 'WRONG',
            })
            self.assertEqual(fail_resp.status_code, 200)
            self.assertNotIn('_auth_user_id', self.client.session)

    # 3. Open Redirect Prevention
    def test_open_redirect_blocked_on_login_and_toggle_read(self):
        session = self.client.session
        session['portal_captcha_code'] = 'ABCD12'
        session['portal_captcha_ts'] = time.time()
        session.save()

        # External redirect target must be discarded in favor of dashboard
        resp = self.client.post(
            reverse('portal:login') + '?next=https://evil.example/phish',
            {
                'username': 'sec_operator',
                'password': 'Str0ng!Operator#2026',
                'captcha': 'ABCD12',
                'next': '//evil.example/phish',
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], reverse('portal:dashboard'))

        # Safe internal next URL still works
        self.client.post(reverse('portal:logout'))
        self.client.get(reverse('portal:login'))
        session = self.client.session
        session['portal_captcha_code'] = 'EFGH34'
        session['portal_captcha_ts'] = time.time()
        session.save()
        safe_resp = self.client.post(
            reverse('portal:login'),
            {
                'username': 'sec_operator',
                'password': 'Str0ng!Operator#2026',
                'captcha': 'EFGH34',
                'next': reverse('portal:messages'),
            },
        )
        self.assertEqual(safe_resp.status_code, 302)
        self.assertEqual(safe_resp['Location'], reverse('portal:messages'))

        # Malicious HTTP_REFERER on toggle-read must fall back safely
        ref_resp = self.client.post(
            reverse('portal:message_toggle_read', kwargs={'pk': self.msg.pk}),
            HTTP_REFERER='https://attacker.example/steal',
        )
        self.assertEqual(ref_resp.status_code, 302)
        self.assertEqual(ref_resp['Location'], reverse('portal:messages'))

    # 4. CSRF & POST Method Enforcement
    def test_state_changing_endpoints_reject_get_and_enforce_csrf(self):
        self.client.login(username='sec_operator', password='Str0ng!Operator#2026')
        post_only_urls = [
            reverse('portal:logout'),
            reverse('portal:message_toggle_read', kwargs={'pk': self.msg.pk}),
            reverse('portal:message_delete', kwargs={'pk': self.msg.pk}),
            reverse('portal:project_delete', kwargs={'pk': self.project.pk}),
            reverse('portal:skill_delete', kwargs={'pk': self.skill.pk}),
            reverse('portal:certification_delete', kwargs={'pk': self.cert.pk}),
            reverse('portal:experience_delete', kwargs={'pk': self.exp.pk}),
        ]
        for url in post_only_urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 405, f"Expected 405 Method Not Allowed on GET {url}")

        # Message detail GET must remain read-only (not mark message read)
        get_detail = self.client.get(
            reverse('portal:message_detail', kwargs={'pk': self.msg.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(get_detail.status_code, 200)
        self.msg.refresh_from_db()
        self.assertFalse(self.msg.is_read)

        # POST marks message read cleanly
        post_detail = self.client.post(
            reverse('portal:message_detail', kwargs={'pk': self.msg.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(post_detail.status_code, 200)
        self.msg.refresh_from_db()
        self.assertTrue(self.msg.is_read)

        # Verify CsrfViewMiddleware rejects forged POSTs without CSRF token
        csrf_client = Client(enforce_csrf_checks=True)
        forged = csrf_client.post(reverse('contact:submit'), {'name': 'X'})
        self.assertEqual(forged.status_code, 403)
        forged_chat = csrf_client.post(reverse('nexus:chat'), {'message': 'hi'})
        self.assertEqual(forged_chat.status_code, 403)

    # 5. Brute-Force Lockout & CAPTCHA Expiration
    def test_login_brute_force_lockout_and_captcha_expiry(self):
        # Expired CAPTCHA (>180s) must fail even if characters match
        session = self.client.session
        session['portal_captcha_code'] = 'OLD99'
        session['portal_captcha_ts'] = time.time() - 250
        session.save()

        expired_resp = self.client.post(reverse('portal:login'), {
            'username': 'sec_operator',
            'password': 'Str0ng!Operator#2026',
            'captcha': 'OLD99',
        })
        self.assertEqual(expired_resp.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

        # Trigger 5 failed attempts total (1 already recorded above + 4 more)
        for _ in range(4):
            s = self.client.session
            s['portal_captcha_code'] = 'TRY12'
            s['portal_captcha_ts'] = time.time()
            s.save()
            self.client.post(reverse('portal:login'), {
                'username': 'sec_operator',
                'password': 'WrongPassword!',
                'captcha': 'TRY12',
            })

        self.assertEqual(LoginAttemptLog.objects.filter(succeeded=False).count(), 5)

        # 6th attempt must be blocked with HTTP 429 even if credentials & CAPTCHA are valid
        s = self.client.session
        s['portal_captcha_code'] = 'GOOD9'
        s['portal_captcha_ts'] = time.time()
        s.save()
        locked_resp = self.client.post(reverse('portal:login'), {
            'username': 'sec_operator',
            'password': 'Str0ng!Operator#2026',
            'captcha': 'GOOD9',
        })
        self.assertEqual(locked_resp.status_code, 429)
        self.assertNotIn('_auth_user_id', self.client.session)

    # 6. IP Extraction & Log Sanitization
    def test_ip_spoofing_protection_and_log_sanitization(self):
        req = self.rf.get(
            '/',
            REMOTE_ADDR='198.51.100.10',
            HTTP_X_FORWARDED_FOR='8.8.8.8, 203.0.113.55',
        )
        with override_settings(TRUST_PROXY_HEADERS=False):
            self.assertEqual(get_client_ip(req), '198.51.100.10')

        with override_settings(TRUST_PROXY_HEADERS=True):
            self.assertEqual(get_client_ip(req), '203.0.113.55')

        sanitized = _sanitize_log_text("bad\r\nFAKE LOG ENTRY key=AQ.Ab8AbCdEfGhIjKlMnOpQrStUvWxYz")
        self.assertNotIn('\r', sanitized)
        self.assertNotIn('\n', sanitized)
        self.assertIn('[REDACTED_KEY]', sanitized)

    # 7. Upload Validators, SafeUploadPath, Safe URLs & Path Traversal Containment
    def test_upload_validators_and_url_scheme_validation(self):
        path_gen = SafeUploadPath('resumes')
        generated = path_gen(None, '../../etc/passwd.pdf')
        self.assertTrue(generated.startswith('resumes/'))
        self.assertTrue(generated.endswith('.pdf'))
        self.assertNotIn('..', generated)

        # Valid in-memory PNG
        buf = io.BytesIO()
        Image.new('RGB', (32, 32), color='lime').save(buf, format='PNG')
        valid_png = SimpleUploadedFile('avatar.png', buf.getvalue(), content_type='image/png')
        validate_image_file(valid_png)  # Should not raise

        # Malicious SVG & disguised PNG must raise ValidationError
        svg_file = SimpleUploadedFile('xss.svg', b'<svg onload=alert(1)>', content_type='image/svg+xml')
        with self.assertRaises(ValidationError):
            validate_image_file(svg_file)

        fake_png = SimpleUploadedFile('evil.png', b'<html><script>alert(1)</script></html>', content_type='image/png')
        with self.assertRaises(ValidationError):
            validate_image_file(fake_png)

        # Valid PDF magic bytes
        valid_pdf = SimpleUploadedFile('cv.pdf', b'%PDF-1.7\n%EOF', content_type='application/pdf')
        validate_resume_file(valid_pdf)

        # Disguised PDF missing %PDF- header must fail
        fake_pdf = SimpleUploadedFile('fake.pdf', b'MZ\x90\x00notapdf', content_type='application/pdf')
        with self.assertRaises(ValidationError):
            validate_resume_file(fake_pdf)

        # Valid minimal DOCX archive
        docx_buf = io.BytesIO()
        with zipfile.ZipFile(docx_buf, 'w') as zf:
            zf.writestr('[Content_Types].xml', '<Types/>')
            zf.writestr('word/document.xml', '<w:document/>')
        valid_docx = SimpleUploadedFile('cv.docx', docx_buf.getvalue(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        validate_resume_file(valid_docx)

        # ZIP masquerading as DOCX without word/document.xml must fail
        bad_zip_buf = io.BytesIO()
        with zipfile.ZipFile(bad_zip_buf, 'w') as zf:
            zf.writestr('evil.sh', 'rm -rf /')
        bad_docx = SimpleUploadedFile('bad.docx', bad_zip_buf.getvalue(), content_type='application/octet-stream')
        with self.assertRaises(ValidationError):
            validate_resume_file(bad_docx)

        # Safe URL validator
        validate_safe_url('https://github.com/im-Abhiram')
        validate_safe_url('mailto:abhiramanil74@gmail.com')
        for bad_url in ('javascript:alert(1)', 'data:text/html,<script>1</script>', 'https://ok.com/\r\nSet-Cookie:a=b'):
            with self.assertRaises(ValidationError):
                validate_safe_url(bad_url)

    def test_resume_download_blocks_traversal_outside_media_root(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'SECRET_OUTSIDE_MEDIA')
            outside_path = tmp.name

        try:
            with patch('core.views.PortfolioSettings.load') as mock_load:
                fake_settings = PortfolioSettings(resume_download_name='cv.pdf')
                mock_file = type('FakeFile', (), {'path': outside_path, 'name': 'cv.pdf'})()
                fake_settings.resume_file = mock_file
                mock_load.return_value = fake_settings

                resp = self.client.get(reverse('download_resume'))
                # Falls back to safe text resume rather than leaking outside_path
                self.assertEqual(resp.status_code, 200)
                self.assertNotIn(b'SECRET_OUTSIDE_MEDIA', resp.content)
        finally:
            if os.path.exists(outside_path):
                os.remove(outside_path)

    # 8. Gemini SSRF / Model Name Guard
    @patch('ai_services.gemini.requests.post')
    def test_gemini_client_rejects_malicious_model_name_before_http(self, mock_post):
        client = GeminiClient(api_key='AQ.DummyKey123456', model='../../v1/otherEndpoint?x=1')
        with self.assertRaises(ModelUnavailableError):
            client.generate_chat_reply('System instruction', [], 'Hello')
        mock_post.assert_not_called()

        bad_form = AISettingsForm({
            'chat_enabled': True,
            'daily_article_enabled': True,
            'article_publish_mode': 'auto',
            'chat_daily_limit_per_visitor': 20,
            'chat_rate_limit_per_minute': 6,
            'article_generation_timezone': 'Asia/Kolkata',
            'preferred_model': '../bad/model',
        })
        self.assertFalse(bad_form.is_valid())
        self.assertIn('preferred_model', bad_form.errors)

    # 9. XSS JSON-Script Escaping, robots.txt & Security Headers
    def test_json_script_xss_escaping_robots_and_headers(self):
        Project.objects.create(
            title='</script><script>alert("XSS")</script>',
            slug='xss-probe-project',
            category='Security',
            badge_label='TEST',
            summary='<b>Summary</b>',
            architecture='Arch',
            key_features='Feat',
            challenges_and_solutions='Chall',
            technologies='Django',
            order=2,
        )
        home_resp = self.client.get(reverse('home'))
        self.assertEqual(home_resp.status_code, 200)
        body = home_resp.content.decode('utf-8')
        self.assertNotIn('</script><script>alert("XSS")</script>', body)
        self.assertIn(r'\u003C/script\u003E', body)
        self.assertIn("object-src 'none'", home_resp['Content-Security-Policy'])
        self.assertEqual(home_resp['X-Frame-Options'], 'DENY')
        self.assertEqual(home_resp['X-Content-Type-Options'], 'nosniff')

        # Sensitive routes must disable caching
        login_resp = self.client.get(reverse('portal:login'))
        self.assertIn('no-store', login_resp.get('Cache-Control', ''))

        status_resp = self.client.get(reverse('nexus:status'))
        self.assertIn('no-store', status_resp.get('Cache-Control', ''))

        # robots.txt blocks admin & portal crawling
        robots_resp = self.client.get('/robots.txt')
        self.assertEqual(robots_resp.status_code, 200)
        self.assertIn('Disallow: /portal/', robots_resp.content.decode('utf-8'))
        self.assertIn('Disallow: /sys-admin/', robots_resp.content.decode('utf-8'))
