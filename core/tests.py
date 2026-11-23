from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import PortfolioSettings
from portfolio.models import Profile, SkillCategory, Skill, Experience, Project, Certification, SocialLink
from lab.models import NetworkKnowledgeTopic, SecurityTool, SecurityConcept
from journal.models import BlogPost, BlogCategory
from contact.models import ContactMessage


class PortfolioViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.profile = Profile.load()
        self.settings = PortfolioSettings.load()

    def test_homepage_status_code_and_content(self):
        """Verify the homepage returns 200 and contains Abhiram's identity."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Abhiram Anil")
        self.assertContains(response, "Connecting systems.")
        self.assertContains(response, "Securing infrastructure.")
        self.assertContains(response, "9656537160")
        self.assertContains(response, "A.P.J Abdul Kalam Technological University")
        self.assertContains(response, "https://abhiramportfolio.pythonanywhere.com/")
        self.assertTemplateUsed(response, 'core/index.html')

    def test_pythonanywhere_host_and_csrf_configuration(self):
        """Verify production host and CSRF settings for abhiramportfolio."""
        from django.conf import settings
        self.assertIn('abhiramportfolio.pythonanywhere.com', settings.ALLOWED_HOSTS)
        self.assertIn('https://abhiramportfolio.pythonanywhere.com', settings.CSRF_TRUSTED_ORIGINS)

    def test_resume_download_fallback(self):
        """Verify resume download provides a valid attachment even if no file was uploaded."""
        response = self.client.get(reverse('download_resume'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.has_header('Content-Disposition'))
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn(b"ABHIRAM ANIL", response.content)
        self.assertIn(b"9656537160", response.content)
        self.assertIn(b"A.P.J ABDUL KALAM TECHNOLOGICAL UNIVERSITY", response.content)

    def test_custom_404_view(self):
        """Verify requesting a non-existent URL renders custom 404 NOC template."""
        response = self.client.get('/non-existent-packet-route/')
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Host Unreachable", status_code=404)
        self.assertContains(response, "404", status_code=404)

    def test_seeded_projects_and_certifications(self):
        """Verify seeded database contains newly added projects and certifications."""
        from django.core.management import call_command
        call_command('seed_portfolio')

        # Check projects count and specific items
        self.assertEqual(Project.objects.count(), 8)
        self.assertTrue(Project.objects.filter(slug='administrative-portal').exists())
        self.assertTrue(Project.objects.filter(slug='production-tracking-system').exists())
        self.assertTrue(Project.objects.filter(slug='remo-document-reminder-app').exists())
        self.assertTrue(Project.objects.filter(slug='6overnews-sports-news-website').exists())
        self.assertTrue(Project.objects.filter(slug='real-estate-website').exists())
        self.assertTrue(Project.objects.filter(slug='easefood-web-application').exists())

        # Check certifications count and specific items
        self.assertEqual(Certification.objects.count(), 11)
        self.assertTrue(Certification.objects.filter(title__icontains="Android Malware Analysis").exists())
        self.assertTrue(Certification.objects.filter(title__icontains="Microsoft Excel").exists())
        self.assertTrue(Certification.objects.filter(issuer__icontains="Accenture").exists())
        self.assertTrue(Certification.objects.filter(issuer__icontains="JPMorgan").exists())

        # Check project API endpoint
        res = self.client.get(reverse('portfolio:project_detail_api', kwargs={'slug': 'administrative-portal'}))
        self.assertEqual(res.status_code, 200)
        self.assertIn("Automated attendance engine", res.json()['features'][1])

    def test_journal_views(self):
        """Verify journal listing and detail views."""
        cat = BlogCategory.objects.create(name="Networking", slug="networking")
        post = BlogPost.objects.create(
            title="Test Post",
            slug="test-post",
            category=cat,
            summary="Test Summary",
            content="Test Content",
            read_time_minutes=4
        )
        # List view
        res_list = self.client.get(reverse('journal:list'))
        self.assertEqual(res_list.status_code, 200)
        self.assertContains(res_list, "Test Post")

        # Detail view
        res_detail = self.client.get(reverse('journal:detail', kwargs={'slug': 'test-post'}))
        self.assertEqual(res_detail.status_code, 200)
        self.assertContains(res_detail, "Test Content")

    def test_lab_views(self):
        """Verify lab portal view."""
        response = self.client.get(reverse('lab:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Network & Cybersecurity Lab")


class SubnetCalculatorApiTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_subnet_calc_valid_slash24(self):
        """Verify /24 subnet calculation."""
        response = self.client.get(reverse('lab:api_subnet_calc'), {'ip': '192.168.10.0', 'cidr': '24'})
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')
        data = json_data['data']
        self.assertEqual(data['network_address'], '192.168.10.0')
        self.assertEqual(data['netmask'], '255.255.255.0')
        self.assertEqual(data['broadcast_address'], '192.168.10.255')
        self.assertEqual(data['usable_hosts'], 254)
        self.assertEqual(data['first_usable'], '192.168.10.1')
        self.assertEqual(data['last_usable'], '192.168.10.254')
        self.assertEqual(data['ip_class'], 'Class C')

    def test_subnet_calc_point_to_point_slash30(self):
        """Verify /30 point-to-point link calculation."""
        response = self.client.get(reverse('lab:api_subnet_calc'), {'ip': '10.0.0.4', 'cidr': '30'})
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')
        data = json_data['data']
        self.assertEqual(data['usable_hosts'], 2)
        self.assertEqual(data['network_address'], '10.0.0.4')
        self.assertEqual(data['broadcast_address'], '10.0.0.7')

    def test_subnet_calc_invalid_ip(self):
        """Verify invalid IP returns 400 error."""
        response = self.client.get(reverse('lab:api_subnet_calc'), {'ip': '999.999.999.999', 'cidr': '24'})
        self.assertEqual(response.status_code, 400)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'error')


class ContactFormSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_valid_contact_submission(self):
        """Verify legitimate message payload is accepted and persisted."""
        payload = {
            'name': 'Alice Engineer',
            'email': 'alice@enterprise.org',
            'subject': 'Infrastructure Architecture Consultation',
            'message': 'Hello Abhiram, we would like to review our enterprise VLAN segmentation.',
            'website_url': '',  # Honeypot empty
        }
        response = self.client.post(reverse('contact:submit'), payload)
        self.assertEqual(response.status_code, 302)  # Redirects to /#contact
        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.name, 'Alice Engineer')
        self.assertFalse(msg.is_read)

    def test_honeypot_rejection(self):
        """Verify automated bots filling honeypot field are rejected."""
        payload = {
            'name': 'Bot Spammer',
            'email': 'bot@spam.com',
            'subject': 'Spam subject',
            'message': 'Spam message content here.',
            'website_url': 'http://malicious-bot.xyz',  # Honeypot filled
        }
        response = self.client.post(reverse('contact:submit'), payload)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_xss_script_injection_rejection(self):
        """Verify script tags in form fields are rejected by clean methods."""
        payload = {
            'name': '<script>alert(1)</script>',
            'email': 'attacker@target.com',
            'subject': 'XSS Probe',
            'message': '<script>stealCookies()</script>',
            'website_url': '',
        }
        response = self.client.post(reverse('contact:submit'), payload)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_ajax_contact_submission(self):
        """Verify AJAX submission returns JSON response."""
        payload = {
            'name': 'Bob SysAdmin',
            'email': 'bob@noc.local',
            'subject': 'pfSense Rule Hardening',
            'message': 'Inquiring about best practices for state table optimization.',
            'website_url': '',
        }
        response = self.client.post(
            reverse('contact:submit'),
            payload,
            headers={'x-requested-with': 'XMLHttpRequest'}
        )
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')


class AdminSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='ComplexPassword123!'
        )

    def test_admin_requires_authentication(self):
        """Verify unauthorized users cannot access admin panel."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirects to login

    def test_admin_authenticated_access(self):
        """Verify authenticated admin can access panel."""
        self.client.login(username='admin_test', password='ComplexPassword123!')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "NOC Operations Portal")

    def test_section_order_between_field_notes_and_contact(self):
        """Verify Defensive Security and Infrastructure Lab appear strictly between Field Notes and Contact."""
        from django.core.management import call_command
        call_command('seed_portfolio')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        idx_field_notes = html.find('id="field-notes"')
        idx_security = html.find('id="security"')
        idx_lab = html.find('id="lab"')
        idx_contact = html.find('id="contact"')

        # All 4 sections must exist
        self.assertNotEqual(idx_field_notes, -1)
        self.assertNotEqual(idx_security, -1)
        self.assertNotEqual(idx_lab, -1)
        self.assertNotEqual(idx_contact, -1)

        # Order must be: field-notes < security < lab < contact
        self.assertTrue(idx_field_notes < idx_security, "Field notes must appear before security")
        self.assertTrue(idx_security < idx_lab, "Security must appear before lab")
        self.assertTrue(idx_lab < idx_contact, "Lab must appear before contact")

        # Verify internal category sequence in security & lab
        idx_concepts = html.find("Defensive Security Concepts Module")
        idx_sec_tools = html.find("Defensive Engineering & Vulnerability Assessment")
        idx_osi = html.find("OSI 7-Layer Visual Diagnostic Stack")
        idx_knowledge = html.find("Networking Knowledge Explorer")
        idx_topo = html.find("Interactive Network & Infrastructure Lab")

        self.assertTrue(idx_field_notes < idx_concepts, "Concepts module must appear after field notes")
        self.assertTrue(idx_concepts < idx_sec_tools, "Concepts module must appear before toolchain")
        self.assertTrue(idx_sec_tools < idx_osi, "Security tools must appear before OSI stack")
        self.assertTrue(idx_osi < idx_knowledge, "OSI stack must appear before knowledge explorer")
        self.assertTrue(idx_knowledge < idx_topo, "Knowledge explorer must appear before topology lab")
        self.assertTrue(idx_topo < idx_contact, "Topology lab must appear before contact")

    def test_deployed_apps_and_github_urls(self):
        """Verify deployed projects display Deployed App buttons and toolramo repo."""
        from django.core.management import call_command
        call_command('seed_portfolio')
        
        # Verify database model
        net_sim = Project.objects.filter(slug='network-simulation-platform').first()
        self.assertIsNotNone(net_sim)
        self.assertEqual(net_sim.github_url, "https://github.com/im-Abhiram/toolramo")
        self.assertEqual(net_sim.demo_url, "https://ramonet.pythonanywhere.com/")

        # Verify rendered page
        response = self.client.get(reverse('home'))
        self.assertContains(response, "Deployed App")
        self.assertContains(response, "DEPLOYED WEBAPP")
        self.assertContains(response, "https://github.com/im-Abhiram/toolramo")
        self.assertContains(response, "Launch Deployed Webapp")

    def test_navbar_infra_lab_and_no_field_notes(self):
        """Verify navbar displays 'Infra Lab' and does not include 'Field Notes'."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf-8')

        # Find the navbar <ul class="nav-links">
        start_nav = html.find('<ul class="nav-links">')
        end_nav = html.find('</ul>', start_nav)
        nav_html = html[start_nav:end_nav]

        self.assertIn("Infra Lab", nav_html)
        self.assertNotIn("Infrastructure Lab", nav_html)
        self.assertNotIn("Field Notes", nav_html)

    def test_social_links_configured(self):
        """Verify LinkedIn, Instagram, and GitHub accounts are active and present."""
        from django.core.management import call_command
        call_command('seed_portfolio')

        # Model check
        self.assertTrue(SocialLink.objects.filter(url="https://github.com/im-Abhiram").exists())
        self.assertTrue(SocialLink.objects.filter(url="https://www.linkedin.com/in/imabhiram/").exists())
        self.assertTrue(SocialLink.objects.filter(url="https://www.instagram.com/im_abhiram__/").exists())

        # Page render check
        response = self.client.get(reverse('home'))
        self.assertContains(response, "https://github.com/im-Abhiram")
        self.assertContains(response, "https://www.linkedin.com/in/imabhiram/")
        self.assertContains(response, "https://www.instagram.com/im_abhiram__/")


class SecurityHardeningTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_security_headers_present(self):
        """Verify strict CSP, Permissions-Policy, nosniff, and clickjacking headers are emitted."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

        # Content-Security-Policy
        self.assertTrue(response.has_header('Content-Security-Policy'))
        csp = response['Content-Security-Policy']
        self.assertIn("default-src 'self'", csp)
        self.assertIn("frame-ancestors 'none'", csp)

        # Feature / Permissions Policy
        self.assertTrue(response.has_header('Permissions-Policy'))
        self.assertIn("camera=()", response['Permissions-Policy'])

        # MIME sniffing & framing defense
        self.assertEqual(response.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.get('X-Frame-Options'), 'DENY')
        self.assertEqual(response.get('Referrer-Policy'), 'strict-origin-when-cross-origin')

    def test_subnet_api_slash_8_dos_protection(self):
        """Verify /8 calculation (16.7 million hosts) executes in O(1) time without OOM."""
        import time
        start = time.time()
        response = self.client.get(reverse('lab:api_subnet_calc'), {'ip': '10.0.0.0', 'cidr': '8'})
        duration = time.time() - start

        self.assertEqual(response.status_code, 200)
        data = response.json()['data']
        self.assertEqual(data['total_hosts'], 16777216)
        self.assertEqual(data['usable_hosts'], 16777214)
        self.assertEqual(data['first_usable'], '10.0.0.1')
        self.assertEqual(data['last_usable'], '10.255.255.254')
        self.assertLess(duration, 0.15, "Calculation must finish in sub-150ms without memory bloat")

    def test_subnet_api_bounds_validation(self):
        """Verify out-of-bounds CIDR and invalid IPs are rejected safely with 400."""
        # CIDR > 32
        res1 = self.client.get(reverse('lab:api_subnet_calc'), {'ip': '192.168.1.0', 'cidr': '33'})
        self.assertEqual(res1.status_code, 400)

        # CIDR < 0
        res2 = self.client.get(reverse('lab:api_subnet_calc'), {'ip': '192.168.1.0', 'cidr': '-1'})
        self.assertEqual(res2.status_code, 400)

        # Malformed IP string
        res3 = self.client.get(reverse('lab:api_subnet_calc'), {'ip': '192.168.1.999', 'cidr': '24'})
        self.assertEqual(res3.status_code, 400)

        # Injection probe in IP
        res4 = self.client.get(reverse('lab:api_subnet_calc'), {'ip': '192.168.1.1; DROP TABLE', 'cidr': '24'})
        self.assertEqual(res4.status_code, 400)

    def test_contact_header_injection_rejection(self):
        """Verify email and subject header injection attempts (\r\n) are blocked."""
        # Header injection in subject
        payload = {
            'name': 'Valid User',
            'email': 'valid@user.com',
            'subject': 'Inquiry\r\nBcc: victim@target.com',
            'message': 'Testing header injection protection.',
            'website_url': '',
        }
        response = self.client.post(reverse('contact:submit'), payload)
        self.assertEqual(ContactMessage.objects.count(), 0)

        # Header injection in email
        payload['subject'] = 'Valid Subject'
        payload['email'] = 'valid@user.com\r\nInjected-Header: evil'
        response = self.client.post(reverse('contact:submit'), payload)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_contact_rapid_submission_protection(self):
        """Verify rapid repeated submissions are rate limited."""
        payload = {
            'name': 'Rapid Sender',
            'email': 'sender@noc.local',
            'subject': 'Fast packet stream',
            'message': 'First message payload with sufficient length.',
            'website_url': '',
        }
        res1 = self.client.post(reverse('contact:submit'), payload)
        self.assertEqual(res1.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)

        # Immediate follow-up from same session
        res2 = self.client.post(reverse('contact:submit'), payload)
        # Should be blocked by rapid flood defense
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_project_api_slug_injection_defense(self):
        """Verify project API rejects malformed slugs."""
        res = self.client.get('/portfolio/api/project/../../etc/passwd/')
        self.assertEqual(res.status_code, 404)
