import time
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from contact.models import ContactMessage
from portfolio.models import Profile, Project, Skill, SkillCategory, Certification, Experience
from core.models import PortfolioSettings


class PortalAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='operator_abhiram',
            password='SecurePassword123!',
            is_staff=True,
            is_active=True
        )
        self.regular_user = User.objects.create_user(
            username='visitor_bob',
            password='BobPassword123!',
            is_staff=False,
            is_active=True
        )
        self.profile = Profile.load()
        self.settings = PortfolioSettings.load()

    def test_unauthenticated_access_redirects_to_login(self):
        """Unauthenticated user accessing protected portal pages gets redirected to login."""
        protected_urls = [
            reverse('portal:dashboard'),
            reverse('portal:messages'),
            reverse('portal:profile_edit'),
            reverse('portal:settings_edit'),
            reverse('portal:projects_list'),
        ]
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn(reverse('portal:login'), response.url)

    def test_login_page_renders_cleanly(self):
        """Operator login page renders with 200 OK and contains login form fields and CAPTCHA challenge."""
        response = self.client.get(reverse('portal:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OPERATOR ACCESS")
        self.assertContains(response, "username")
        self.assertContains(response, "password")
        self.assertContains(response, "Security Verification Challenge")
        self.assertContains(response, "data:image/png;base64,")

    def test_admin_login_blocked_and_redirected_to_custom_gui(self):
        """Standard /admin/login/ is intercepted, blocking default Django login and serving custom GUI."""
        response = self.client.get('/admin/login/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "OPERATOR ACCESS")
        self.assertContains(response, "Security Verification Challenge")

    def test_captcha_refresh_endpoint(self):
        """The /portal/captcha/refresh/ endpoint returns a valid base64 image challenge."""
        response = self.client.get(reverse('portal:captcha_refresh'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'ok')
        self.assertTrue(data['image'].startswith('data:image/png;base64,'))

    def test_failed_login_invalid_captcha(self):
        """Failing CAPTCHA challenge blocks login attempt before credential check."""
        # Set session captcha
        session = self.client.session
        session['portal_captcha_code'] = 'VALID'
        session['portal_captcha_ts'] = time.time()
        session.save()

        response = self.client.post(reverse('portal:login'), {
            'username': 'operator_abhiram',
            'password': 'SecurePassword123!',
            'captcha': 'WRONG_CODE',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Security challenge verification failed")

    def test_successful_staff_login(self):
        """Valid staff credentials with correct CAPTCHA successfully authenticate."""
        session = self.client.session
        session['portal_captcha_code'] = 'SEC99'
        session['portal_captcha_ts'] = time.time()
        session.save()

        response = self.client.post(reverse('portal:login'), {
            'username': 'operator_abhiram',
            'password': 'SecurePassword123!',
            'captcha': 'SEC99',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('portal:dashboard'))

    def test_failed_login_invalid_password(self):
        """Wrong password with valid CAPTCHA fails with invalid credentials message."""
        session = self.client.session
        session['portal_captcha_code'] = 'SEC99'
        session['portal_captcha_ts'] = time.time()
        session.save()

        response = self.client.post(reverse('portal:login'), {
            'username': 'operator_abhiram',
            'password': 'WrongPassword!',
            'captcha': 'SEC99',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid operator credentials")

    def test_regular_user_denied_staff_clearance(self):
        """Non-staff user cannot authenticate into operator portal."""
        session = self.client.session
        session['portal_captcha_code'] = 'SEC99'
        session['portal_captcha_ts'] = time.time()
        session.save()

        response = self.client.post(reverse('portal:login'), {
            'username': 'visitor_bob',
            'password': 'BobPassword123!',
            'captcha': 'SEC99',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Staff privilege clearance required")

    def test_operator_logout(self):
        """Logging out via POST purges session and redirects to login page."""
        self.client.login(username='operator_abhiram', password='SecurePassword123!')
        response = self.client.post(reverse('portal:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('portal:login'))


class PortalManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='abhiram_admin',
            password='AdminPassword123!',
            is_staff=True,
            is_active=True
        )
        self.client.login(username='abhiram_admin', password='AdminPassword123!')
        self.profile = Profile.load()
        self.settings = PortfolioSettings.load()

    def test_dashboard_metrics(self):
        """Dashboard displays correct telemetry metrics."""
        ContactMessage.objects.create(
            name="Alice",
            email="alice@example.com",
            subject="Security Audit Inquiry",
            message="We would like to discuss infrastructure auditing.",
            is_read=False
        )
        ContactMessage.objects.create(
            name="Charlie",
            email="charlie@example.com",
            subject="Network Consulting",
            message="pfSense setup query.",
            is_read=True
        )

        response = self.client.get(reverse('portal:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Operations HUD")
        self.assertContains(response, "Security Audit Inquiry")
        self.assertEqual(response.context['total_messages'], 2)
        self.assertEqual(response.context['unread_messages'], 1)

    def test_contact_messages_inbox_and_actions(self):
        """Verify message filtering, toggling read status, and deletion."""
        msg = ContactMessage.objects.create(
            name="David",
            email="david@example.com",
            subject="Project Inquiry",
            message="Hello Abhiram, great work on the network simulator.",
            is_read=False
        )

        # 1. Inbox listing
        res = self.client.get(reverse('portal:messages'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "David")
        self.assertContains(res, "Project Inquiry")

        # 2. Toggle read status (POST)
        res_toggle = self.client.post(reverse('portal:message_toggle_read', kwargs={'pk': msg.pk}))
        self.assertEqual(res_toggle.status_code, 302)
        msg.refresh_from_db()
        self.assertTrue(msg.is_read)

        # 3. Message detail AJAX view (GET read-only)
        res_detail = self.client.get(
            reverse('portal:message_detail', kwargs={'pk': msg.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(res_detail.status_code, 200)
        self.assertEqual(res_detail.json()['subject'], "Project Inquiry")

        # 4. Message deletion (POST)
        res_del = self.client.post(reverse('portal:message_delete', kwargs={'pk': msg.pk}))
        self.assertEqual(res_del.status_code, 302)
        self.assertFalse(ContactMessage.objects.filter(pk=msg.pk).exists())

    def test_profile_edit(self):
        """Updating profile via portal updates the main page content."""
        post_data = {
            'full_name': 'Abhiram Anil Updated',
            'title': 'Senior IT Infrastructure & Cybersecurity Specialist',
            'hero_badge_label': 'NOC ARCHITECT / SECURITY AUDIT',
            'headline': 'Next-gen enterprise networking and resilient security.',
            'secondary_statement': 'Updated secondary statement.',
            'about_text': 'Updated about narrative with new achievements.',
            'location': 'Kerala, India',
            'email': 'abhiramanil74@gmail.com',
            'phone': '+91 9656537160',
            'education_summary': 'B.Tech CSE',
        }
        response = self.client.post(reverse('portal:profile_edit'), post_data)
        self.assertEqual(response.status_code, 302)
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, 'Abhiram Anil Updated')
        self.assertEqual(self.profile.title, 'Senior IT Infrastructure & Cybersecurity Specialist')

        # Verify change appears on public homepage
        home_res = self.client.get(reverse('home'))
        self.assertContains(home_res, 'Abhiram Anil Updated')
        self.assertContains(home_res, 'Next-gen enterprise networking and resilient security.')

    def test_settings_edit(self):
        """Updating site settings via portal updates global toggles and titles."""
        post_data = {
            'site_title': 'Abhiram Anil | Advanced NOC Portal',
            'brand_tagline': 'Engineered for high-availability infrastructure.',
            'noc_status_text': 'STATUS: ALL SYSTEMS NOMINAL',
            'location_label': 'Kerala, IN',
            'resume_download_name': 'Abhiram_Anil_CV_2026.pdf',
            'show_lab_section': 'on',
            'show_journal_section': 'on',
            'show_terminal_feature': 'on',
            'show_certifications': 'on',
            'show_activity_wall': 'on',
        }
        response = self.client.post(reverse('portal:settings_edit'), post_data)
        self.assertEqual(response.status_code, 302)

        self.settings.refresh_from_db()
        self.assertEqual(self.settings.site_title, 'Abhiram Anil | Advanced NOC Portal')
        self.assertEqual(self.settings.noc_status_text, 'STATUS: ALL SYSTEMS NOMINAL')

    def test_project_crud(self):
        """Adding, editing, and deleting a project via portal."""
        # Create
        res_create = self.client.post(reverse('portal:project_create'), {
            'title': 'Automated Firewall Telemetry',
            'slug': 'automated-firewall-telemetry',
            'category': 'Cybersecurity / Infrastructure',
            'badge_label': 'NEW LAB DEPLOYMENT',
            'summary': 'Automated log analyzer for pfSense.',
            'architecture': 'Event-driven architecture with Python.',
            'key_features': 'Real-time alerting\nIP geo-lookup\nSyslog aggregation',
            'challenges_and_solutions': 'Handled high throughput using batch processing.',
            'technologies': 'Python, pfSense, SQLite',
            'order': 1,
            'is_featured': 'on',
        })
        self.assertEqual(res_create.status_code, 302)
        project = Project.objects.get(slug='automated-firewall-telemetry')
        self.assertEqual(project.title, 'Automated Firewall Telemetry')

        # Edit
        res_edit = self.client.post(reverse('portal:project_edit', kwargs={'pk': project.pk}), {
            'title': 'Automated Firewall Telemetry v2',
            'slug': 'automated-firewall-telemetry',
            'category': 'Cybersecurity / Infrastructure',
            'badge_label': 'UPDATED',
            'summary': 'Enhanced version with AI threat scoring.',
            'architecture': 'Event-driven architecture with Python.',
            'key_features': 'Real-time alerting\nIP geo-lookup',
            'challenges_and_solutions': 'Handled high throughput.',
            'technologies': 'Python, pfSense, SQLite',
            'order': 1,
        })
        self.assertEqual(res_edit.status_code, 302)
        project.refresh_from_db()
        self.assertEqual(project.title, 'Automated Firewall Telemetry v2')

        # Delete (POST)
        res_del = self.client.post(reverse('portal:project_delete', kwargs={'pk': project.pk}))
        self.assertEqual(res_del.status_code, 302)
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())
