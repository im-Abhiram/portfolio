from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import PortfolioSettings
from portfolio.models import (
    Profile, Education, SkillCategory, Skill, Experience, Project,
    Certification, SocialLink
)
from lab.models import NetworkKnowledgeTopic, SecurityTool, SecurityConcept
from journal.models import BlogCategory, BlogPost, SecurityNote


class Command(BaseCommand):
    help = "Seeds the database with Abhiram Anil's resume data and portfolio content."

    def handle(self, *args, **options):
        self.stdout.write("Initializing database with Abhiram Anil portfolio data...")

        # 1. Portfolio Settings
        settings, _ = PortfolioSettings.objects.get_or_create(pk=1)
        settings.site_title = "Abhiram Anil | IT Infrastructure & Cybersecurity Portfolio"
        settings.brand_tagline = "Building, connecting and securing digital infrastructure."
        settings.noc_status_text = "SYS_OPERATIONAL // NOC TELEMETRY ACTIVE"
        settings.location_label = "Kerala, India [UTC+05:30]"
        settings.resume_download_name = "Abhiram_Anil_Resume.pdf"
        settings.show_lab_section = True
        settings.show_journal_section = True
        settings.show_terminal_feature = True
        settings.show_certifications = True
        settings.show_activity_wall = True
        settings.save()
        self.stdout.write("  [+] PortfolioSettings initialized.")

        # 2. Profile
        profile, _ = Profile.objects.get_or_create(pk=1)
        profile.full_name = "Abhiram Anil"
        profile.title = "IT Executive | Network Infrastructure | Cybersecurity | System Administration"
        profile.headline = "Building, connecting and securing digital infrastructure."
        profile.secondary_statement = (
            "I work across IT operations, networking, cybersecurity and software development — "
            "connecting systems, solving infrastructure problems and strengthening security."
        )
        profile.about_text = (
            "Cybersecurity-driven B.Tech (CSE) graduate. Currently serving as an IT Executive, managing enterprise-level systems while "
            "pursuing specialized training in cybersecurity (threat intelligence, incident response, and network security). "
            "Proven ability to bridge the gap between core IT operations and security compliance, with a focus on mitigating vulnerabilities "
            "and hardening system architecture.\n\n"
            "I work with networking infrastructure, Cisco switches, pfSense firewalls, VLAN segmentation, "
            "Active Directory, endpoint troubleshooting and streaming infrastructure.\n\n"
            "Alongside operational IT work, I have developed practical experience in vulnerability assessment, "
            "network auditing and web application security analysis."
        )
        profile.location = "Kerala, India"
        profile.email = "abhiramanil74@gmail.com"
        profile.phone = "+91 9656537160"
        profile.education_summary = "B.Tech in Computer Science and Engineering — A.P.J Abdul Kalam Technological University (April 2025)"
        profile.profile_image = "profile/abhiram_anil.jpg"
        profile.hero_badge_label = "IT OPERATIONS / NETWORKING / SECURITY"
        profile.save()
        self.stdout.write("  [+] Profile initialized.")

        # 2.1 Education
        Education.objects.all().delete()
        Education.objects.create(
            degree="Bachelor of Technology in Computer Science and Engineering",
            institution="A.P.J Abdul Kalam Technological University",
            location="Kerala, IN",
            completion_date="April 2025",
            description=(
                "Graduated in Computer Science and Engineering with focused coursework in "
                "computer networks, operating systems, database management systems, cryptography, "
                "and cybersecurity engineering."
            ),
            order=1
        )
        self.stdout.write("  [+] Education records initialized.")

        # 3. Social Links
        SocialLink.objects.all().delete()
        SocialLink.objects.create(name="GitHub", url="https://github.com/im-Abhiram", icon="bi-github", order=1)
        SocialLink.objects.create(name="LinkedIn", url="https://www.linkedin.com/in/imabhiram/", icon="bi-linkedin", order=2)
        SocialLink.objects.create(name="Instagram", url="https://www.instagram.com/im_abhiram__/", icon="bi-instagram", order=3)
        SocialLink.objects.create(name="Email", url="mailto:abhiramanil74@gmail.com", icon="bi-envelope-at", order=4)
        self.stdout.write("  [+] Social links created.")

        # 4. Skill Categories & Skills
        SkillCategory.objects.all().delete()
        Skill.objects.all().delete()

        cat_net = SkillCategory.objects.create(
            name="Network Infrastructure",
            slug="network-infrastructure",
            icon="bi-diagram-3",
            description="Core routing, switching, VLAN segmentation, and perimeter firewall security.",
            order=1
        )
        cat_sys = SkillCategory.objects.create(
            name="System Administration",
            slug="system-administration",
            icon="bi-hdd-rack",
            description="Active Directory domain architecture, endpoint operations, and systems troubleshooting.",
            order=2
        )
        cat_sec = SkillCategory.objects.create(
            name="Cybersecurity",
            slug="cybersecurity",
            icon="bi-shield-check",
            description="Vulnerability auditing, reconnaissance, packet inspection, and web application assessments.",
            order=3
        )
        cat_dev = SkillCategory.objects.create(
            name="Development",
            slug="development",
            icon="bi-code-slash",
            description="Backend engineering, database querying, and infrastructure automation tooling.",
            order=4
        )
        cat_stream = SkillCategory.objects.create(
            name="Streaming Infrastructure",
            slug="streaming-infrastructure",
            icon="bi-broadcast-pin",
            description="Low-latency video ingest, hardware encoding, and live video broadcast operations.",
            order=5
        )

        # Network Infrastructure Skills
        Skill.objects.create(
            category=cat_net,
            name="Cisco Switching",
            proficiency_tag="Operational",
            icon="bi-hdd-network",
            description="VLAN trunking (802.1Q), interface configuration, port security, STP diagnostics, and enterprise switch management.",
            order=1
        )
        Skill.objects.create(
            category=cat_net,
            name="VLAN Configuration",
            proficiency_tag="Core Competency",
            icon="bi-layers-half",
            description="Departmental segmentation, broadcast domain isolation, inter-VLAN routing controls, and network traffic security.",
            order=2
        )
        Skill.objects.create(
            category=cat_net,
            name="pfSense",
            proficiency_tag="Firewall Security",
            icon="bi-shield-lock",
            description="Stateful packet inspection firewall rules, NAT translation, alias management, WAN failover, and perimeter hardening.",
            order=3
        )
        Skill.objects.create(
            category=cat_net,
            name="TCP/IP",
            proficiency_tag="Core Protocol",
            icon="bi-arrow-left-right",
            description="Three-way handshake mechanics, packet flags, windowing, congestion control, and subnet addressing architecture.",
            order=4
        )
        Skill.objects.create(
            category=cat_net,
            name="Network Troubleshooting",
            proficiency_tag="Diagnostics",
            icon="bi-activity",
            description="Systematic fault isolation using ping, traceroute, ARP inspection, MTU debugging, and packet capture triage.",
            order=5
        )

        # System Administration Skills
        Skill.objects.create(
            category=cat_sys,
            name="Windows Administration",
            proficiency_tag="SysAdmin",
            icon="bi-windows",
            description="Windows Server role configuration, service management, filesystem NTFS permissions, and system maintenance.",
            order=1
        )
        Skill.objects.create(
            category=cat_sys,
            name="Active Directory",
            proficiency_tag="Core Competency",
            icon="bi-diagram-2",
            description="Centralized domain management, Organizational Units (OUs), domain controller maintenance, and authentication policies.",
            order=2
        )
        Skill.objects.create(
            category=cat_sys,
            name="Domain & Group Management",
            proficiency_tag="Identity & Access",
            icon="bi-people",
            description="Security group hierarchies, resource delegation, Group Policy Object (GPO) deployment, and access governance.",
            order=3
        )
        Skill.objects.create(
            category=cat_sys,
            name="User Administration",
            proficiency_tag="Access Control",
            icon="bi-person-check",
            description="User lifecycle provisioning, credential resets, RBAC assignments, and multi-user environment support.",
            order=4
        )
        Skill.objects.create(
            category=cat_sys,
            name="Hardware Troubleshooting",
            proficiency_tag="Infrastructure",
            icon="bi-motherboard",
            description="Server component triage, power supply testing, structured CAT6 cabling, patch panel punchdowns, and hardware repairs.",
            order=5
        )
        Skill.objects.create(
            category=cat_sys,
            name="Proactive Monitoring",
            proficiency_tag="Reliability & Ops",
            icon="bi-activity",
            description="Continuous endpoint & server diagnostics, TCP/IP networking checks, proactive resource tracking, and hardware/software reliability assurance.",
            order=6
        )

        # Cybersecurity Skills
        Skill.objects.create(
            category=cat_sec,
            name="Nmap",
            proficiency_tag="Recon & Audit",
            icon="bi-radar",
            description="Host discovery, SYN stealth scanning, service version fingerprinting, OS detection, and NSE vulnerability scripts.",
            order=1
        )
        Skill.objects.create(
            category=cat_sec,
            name="Wireshark",
            proficiency_tag="Packet Analysis",
            icon="bi-file-earmark-binary",
            description="Deep packet inspection, protocol dissection, TCP stream reconstruction, and malicious beaconing identification.",
            order=2
        )
        Skill.objects.create(
            category=cat_sec,
            name="Burp Suite",
            proficiency_tag="Web App Security",
            icon="bi-bug",
            description="HTTP proxy traffic interception, request repeater analysis, intruder payload fuzzing, and web vulnerability analysis.",
            order=3
        )
        Skill.objects.create(
            category=cat_sec,
            name="Metasploit",
            proficiency_tag="Exploit Testing",
            icon="bi-terminal-dash",
            description="Controlled vulnerability verification in lab environments, payload generation, and proof-of-concept auditing.",
            order=4
        )
        Skill.objects.create(
            category=cat_sec,
            name="Splunk",
            proficiency_tag="SIEM / Logging",
            icon="bi-search",
            description="Log ingestion, SPL queries, correlation search definitions, authentication anomaly alerts, and security dashboards.",
            order=5
        )
        Skill.objects.create(
            category=cat_sec,
            name="Gobuster",
            proficiency_tag="Enumeration",
            icon="bi-folder2-open",
            description="High-speed directory, file, and DNS subdomain enumeration to discover unlinked assets and hidden endpoints.",
            order=6
        )
        Skill.objects.create(
            category=cat_sec,
            name="Netdiscover",
            proficiency_tag="ARP Recon",
            icon="bi-broadcast",
            description="Active and passive ARP reconnaissance for discovering live hosts and MAC addresses across localized network segments.",
            order=7
        )
        Skill.objects.create(
            category=cat_sec,
            name="Hydra",
            proficiency_tag="Audit Tool",
            icon="bi-key",
            description="Authentication resilience testing, network service password auditing, and dictionary defense validation.",
            order=8
        )
        Skill.objects.create(
            category=cat_sec,
            name="Vulnerability Assessment",
            proficiency_tag="Defensive Practice",
            icon="bi-shield-shaded",
            description="Systematic weakness identification, risk ranking, attack surface mapping, and actionable remediation reporting.",
            order=9
        )

        # Development Skills
        Skill.objects.create(
            category=cat_dev,
            name="Python",
            proficiency_tag="Core Language",
            icon="bi-filetype-py",
            description="Infrastructure automation, network diagnostic tooling, socket communication, and web application backends.",
            order=1
        )
        Skill.objects.create(
            category=cat_dev,
            name="Django",
            proficiency_tag="Full-Stack Web",
            icon="bi-window-stack",
            description="Model-View-Template architecture, ORM query optimization, secure authentication, CSRF/XSS defense, and admin customization.",
            order=2
        )
        Skill.objects.create(
            category=cat_dev,
            name="SQL",
            proficiency_tag="Database Querying",
            icon="bi-database",
            description="Relational database schemas, SQLite/PostgreSQL queries, table joins, index optimization, and parameterized queries.",
            order=3
        )
        Skill.objects.create(
            category=cat_dev,
            name="JavaScript",
            proficiency_tag="Frontend Logic",
            icon="bi-filetype-js",
            description="Vanilla DOM scripting, Canvas graphics programming, asynchronous fetch pipelines, and interactive client tools.",
            order=4
        )
        Skill.objects.create(
            category=cat_dev,
            name="C",
            proficiency_tag="Systems Programming",
            icon="bi-cpu",
            description="Pointers, manual memory allocation, low-level data structures, and foundational computer systems architecture.",
            order=5
        )

        # Streaming Infrastructure Skills
        Skill.objects.create(
            category=cat_stream,
            name="OBS",
            proficiency_tag="Broadcast Engine",
            icon="bi-camera-video",
            description="Broadcast scene construction, multi-source video switching, audio routing, bitrate tuning, and hardware encoder configuration.",
            order=1
        )
        Skill.objects.create(
            category=cat_stream,
            name="Wirecast",
            proficiency_tag="Live Production",
            icon="bi-cast",
            description="Multi-channel live video switching, lower-third graphic overlays, stream output redundancy, and studio production workflows.",
            order=2
        )
        self.stdout.write("  [+] SkillCategories and Skills created.")

        # 5. Experience
        Experience.objects.all().delete()
        Experience.objects.create(
            company="JAIHIND TV",
            role="IT Executive",
            employment_type="Full-time",
            duration="November 2025 – Present",
            location="Thiruvananthapuram, India",
            is_current=True,
            summary="Administering enterprise broadcast network infrastructure, perimeter security firewalls, directory services, and high-reliability live video ingest systems.",
            responsibilities=(
                "Administered network infrastructure using Cisco switches and pfSense firewalls.\n"
                "Implemented VLANs for departmental isolation and threat mitigation.\n"
                "Managed users and shared resources through Active Directory domains and groups.\n"
                "Configured live streaming ingest through OBS and Wirecast.\n"
                "Supported live video broadcasts to internal and social media platforms."
            ),
            technologies="Cisco Switches, pfSense Firewall, VLANs, Active Directory, Windows Server, OBS Studio, Wirecast",
            order=1
        )

        Experience.objects.create(
            company="OFFENSO HACKERS ACADEMY",
            role="Cybersecurity Intern",
            employment_type="Internship",
            duration="August 2025 – February 2026",
            location="Thiruvananthapuram, India",
            is_current=False,
            summary="Completed rigorous hands-on cybersecurity training and operational exercises in network reconnaissance, vulnerability assessment, and web security auditing.",
            responsibilities=(
                "Conducted network reconnaissance and host discovery across target architectures.\n"
                "Executed vulnerability assessment, port scanning, and network auditing using Nmap.\n"
                "Identified network attack surfaces and evaluated open services for vulnerabilities.\n"
                "Performed controlled exploitation testing using Metasploit in isolated lab environments.\n"
                "Authored detailed technical findings documentation and remediation guidance.\n"
                "Conducted web application testing and HTTP traffic interception using Burp Suite.\n"
                "Analyzed application behaviors to identify Cross-Site Scripting (XSS) and SQL Injection vulnerabilities."
            ),
            technologies="Nmap, Burp Suite, Metasploit Framework, Wireshark, Gobuster, Netdiscover, Linux, Web Application Security, Network Auditing",
            order=2
        )
        self.stdout.write("  [+] Experience entries initialized.")

        # 6. Projects
        Project.objects.all().delete()
        Project.objects.create(
            title="Network Simulation Platform",
            slug="network-simulation-platform",
            category="IT Infrastructure & Network Simulation",
            badge_label="NETWORK SIMULATION",
            summary="An interactive browser-based network simulation and educational platform built with Python, Django, and Vanilla JavaScript for hands-on infrastructure training.",
            architecture=(
                "Built on Django's MVT architecture with an SQLite backend storing device profiles, network templates, and curriculum modules. "
                "The frontend features a custom-built HTML5 Canvas vector simulation engine running a high-performance tick loop that visualizes "
                "packet traversals, ARP resolutions, and link state transitions without heavy third-party 3D dependencies."
            ),
            key_features=(
                "Drag-and-drop network topology designer\n"
                "Rack layout planner\n"
                "Packet flow simulation engine\n"
                "Cisco IOS CLI simulation\n"
                "Linux shell simulation\n"
                "Windows CMD simulation\n"
                "CCNA learning modules\n"
                "Subnetting tools\n"
                "Interactive networking education"
            ),
            challenges_and_solutions=(
                "Challenge: Creating an authentic command-line parser and realistic packet animation loop entirely in Vanilla JavaScript without crashing the browser or requiring Node.js builds.\n"
                "Solution: Implemented an event-driven Canvas renderer using requestAnimationFrame with stateful packet coordinate interpolation, and wrote a lightweight client-side command syntax tree matching standard Cisco IOS privilege levels and commands."
            ),
            technologies="Python, Django, JavaScript, HTML5 Canvas, SQLite3, CSS3",
            demo_url="https://ramonet.pythonanywhere.com/",
            github_url="https://github.com/im-Abhiram/toolramo",
            has_interactive_preview=True,
            is_featured=True,
            order=1
        )

        Project.objects.create(
            title="Administrative Portal",
            slug="administrative-portal",
            category="Enterprise Systems / Workforce Management",
            badge_label="ENTERPRISE WORKFORCE ERP",
            summary="A production-ready Django workforce management system designed for complete employee lifecycle, shift scheduling, and document management.",
            architecture=(
                "Production-ready Django architecture featuring an automated attendance engine with live daily tracking, shift-based overtime calculator, and an enterprise payroll calculation engine supporting multi-cycle distributions. Implements immutable audit logging and strict role-based access control (RBAC)."
            ),
            key_features=(
                "Complete employee lifecycle and document management\n"
                "Automated attendance engine with live daily tracker\n"
                "One-click attendance marking\n"
                "Leave management with auto-absent syncing\n"
                "Shift-based overtime calculations\n"
                "Enterprise payroll engine supporting weekly, bi-weekly, and monthly pay cycles\n"
                "Immutable audit logging for financial and HR transactions\n"
                "Strict role-based access control for superadmins, accountants, and business owners"
            ),
            challenges_and_solutions=(
                "Challenge: Synchronizing multi-cycle payroll rules and shift overtime without race conditions during simultaneous employee attendance marking.\n"
                "Solution: Engineered atomic database transactions, normalized attendance ledger models, and background auto-absent sync routines with immutable audit logging."
            ),
            technologies="Python, Django, SQLite3, Role-Based Access Control, Audit Logging, Bootstrap, JavaScript",
            demo_url="https://thamara.pythonanywhere.com/",
            github_url="https://github.com/im-Abhiram/tempsite1",
            has_interactive_preview=False,
            is_featured=True,
            order=2
        )

        Project.objects.create(
            title="Production Tracking System",
            slug="production-tracking-system",
            category="Industrial ERP / Manufacturing",
            badge_label="MANUFACTURING & INVENTORY ERP",
            summary="A lightweight, responsive Django and SQLite3 web application built specifically for brick manufacturing and construction material companies to manage end-to-end business operations.",
            architecture=(
                "Architected with Django MVT and SQLite3, featuring live inventory mathematical formulas, multi-site material dispatch tracking, shift-based factory production logging, and real-time analytical business dashboards optimized for zero-cost PythonAnywhere hosting."
            ),
            key_features=(
                "Factory production shift automation\n"
                "Live inventory calculation formulas\n"
                "Client construction site material usage tracking\n"
                "Truck dispatch and logistics tracking\n"
                "Worker attendance and payroll management\n"
                "Financial credit and payment tracking ledger\n"
                "Role-based security for Super Admin, Accountant, and Owner\n"
                "Real-time business analytics dashboards"
            ),
            challenges_and_solutions=(
                "Challenge: Managing dynamic inventory recalculations when materials are consumed across multiple construction sites and variable kiln shifts.\n"
                "Solution: Implemented event-driven inventory reconciliation formulas and structured credit ledgers optimized for low-latency queries on SQLite3."
            ),
            technologies="Python, Django, SQLite3, Analytics Dashboard, PythonAnywhere, JavaScript, Bootstrap",
            demo_url="https://thamarayyathproduction.pythonanywhere.com/",
            github_url="https://github.com/im-Abhiram/inventory",
            has_interactive_preview=False,
            is_featured=True,
            order=3
        )

        Project.objects.create(
            title="Remo",
            slug="remo-document-reminder-app",
            category="Mobile Application / Asset Management",
            badge_label="OFFLINE FLUTTER APP",
            summary="A premium offline Flutter application for intelligent receipt management, OCR scanning, warranty tracking, EMI reminders, document organization, vehicle expenses, medical records, and personal asset management.",
            architecture=(
                "Built using Flutter and Dart with an offline-first architecture. Utilizes embedded SQLite for local-only private storage, on-device machine learning OCR algorithms for document/receipt scanning, and background notification schedulers for warranty and EMI expiries."
            ),
            key_features=(
                "On-device intelligent receipt & document OCR scanning\n"
                "Warranty tracking with proactive expiration alerts\n"
                "EMI & recurring payment reminders\n"
                "Structured document categorization & encrypted local vault\n"
                "Vehicle maintenance, fuel, and service expense tracking\n"
                "Medical prescription and health record management\n"
                "Personal asset inventory & valuation tracking\n"
                "100% offline-first privacy architecture (zero cloud leakage)"
            ),
            challenges_and_solutions=(
                "Challenge: Ensuring accurate text extraction from varied crumpled receipts and invoices while maintaining strict zero-cloud offline user privacy.\n"
                "Solution: Integrated on-device OCR processing pipelines combined with regex heuristic parsers that identify dates, totals, and merchant names locally in SQLite."
            ),
            technologies="Flutter, Dart, SQLite, On-Device OCR, Local Notifications, Offline-First Architecture",
            demo_url="",
            github_url="https://github.com/im-Abhiram/reme-doccument-remainder-app",
            has_interactive_preview=False,
            is_featured=True,
            order=4
        )

        Project.objects.create(
            title="6overnews",
            slug="6overnews-sports-news-website",
            category="Django Web Application / Media Platform",
            badge_label="SPORTS MEDIA PLATFORM",
            summary="A modern Django-powered sports news website delivering the latest sports journalism, live fixtures, league standings, trending stories, and interactive widgets with a clean, responsive UI inspired by leading sports media platforms.",
            architecture=(
                "Engineered using Django's Model-View-Template pattern, featuring relational schemas for sports categories, match schedules, league tables, and breaking news tickers. Optimized for high concurrency and fast page rendering with responsive media widgets."
            ),
            key_features=(
                "Real-time sports news publishing and category taxonomy\n"
                "Live match fixtures and schedule tracking\n"
                "Dynamic league standings and score tables\n"
                "Trending stories and editorial spotlights\n"
                "Interactive multimedia widgets and video embed support\n"
                "Editorial CMS dashboard with article draft workflows\n"
                "Responsive mobile-first media UI"
            ),
            challenges_and_solutions=(
                "Challenge: Rendering heavy dynamic fixture boards and live standings efficiently across varying viewport sizes.\n"
                "Solution: Structured normalized database relationships with cached querysets and responsive CSS grid components inspired by leading sports media platforms."
            ),
            technologies="Python, Django, SQLite3, Bootstrap, JavaScript, HTML5, CSS3",
            demo_url="",
            github_url="https://github.com/im-Abhiram/6overnews-sports-news-website",
            has_interactive_preview=False,
            is_featured=True,
            order=5
        )

        Project.objects.create(
            title="Real Estate Web Application",
            slug="real-estate-website",
            category="Full-Stack Web Application / PropTech",
            badge_label="REAL ESTATE PORTAL",
            summary="A modern and responsive real estate web application built with Django, featuring property listings, advanced search filters, and an agent contact system.",
            architecture=(
                "Full-stack Django application with relational models for property assets, photo galleries, agent profiles, and inquiries. Features multi-parameter database queries for precise property filtering by location, price, and amenities."
            ),
            key_features=(
                "Filtered property search by price, location, bedrooms, and property type\n"
                "High-resolution property image galleries and amenity highlights\n"
                "Direct agent inquiry and lead dispatch system\n"
                "Secure Django admin portal for broker listing management\n"
                "Map coordinates and neighborhood data integration\n"
                "Responsive mobile layout for on-the-go home buyers"
            ),
            challenges_and_solutions=(
                "Challenge: Building complex multi-parameter database filter queries that remain snappy on SQLite without slowing down property searches.\n"
                "Solution: Used Django Q objects for dynamic filter chaining and indexed key search columns such as price, bedrooms, and city."
            ),
            technologies="Python, Django, SQLite3, HTML5, CSS3, JavaScript, Bootstrap",
            demo_url="",
            github_url="https://github.com/im-Abhiram/real-estate-website",
            has_interactive_preview=False,
            is_featured=True,
            order=6
        )

        Project.objects.create(
            title="EASEFOOD",
            slug="easefood-web-application",
            category="E-Commerce / Food Ordering",
            badge_label="FOOD COMMERCE ENGINE",
            summary="A dynamic food ordering solution built with Python and Django, featuring real-time order tracking, secure payment integration to optimize transaction handling, and a comprehensive admin management dashboard.",
            architecture=(
                "Architected with Django MVT and SQLite, implementing transactional shopping cart sessions, real-time order state lifecycles (Placed, Cooking, Out for Delivery, Delivered), and secure payment gateway handling with automated invoice generation."
            ),
            key_features=(
                "Interactive digital restaurant menu with category filtering\n"
                "Real-time order status tracking pipeline\n"
                "Secure payment processing and transaction verification\n"
                "Comprehensive administrative dashboard for menu customization\n"
                "Live order dispatch and fulfillment monitoring\n"
                "Minimalist, performance-optimized responsive user interface"
            ),
            challenges_and_solutions=(
                "Challenge: Preventing race conditions during peak concurrent dinner order rushes and maintaining order state consistency.\n"
                "Solution: Enforced atomic database transactions on checkout and implemented structured status transition state machines."
            ),
            technologies="Python, Django, SQLite3, Payment Integration, HTML5, CSS3, JavaScript",
            demo_url="",
            github_url="",
            has_interactive_preview=False,
            is_featured=True,
            order=7
        )

        Project.objects.create(
            title="Pet World",
            slug="pet-world",
            category="Full-Stack Web Application",
            badge_label="PET CARE & ADOPTION",
            summary="A full-featured Django web application designed for comprehensive pet welfare, adoption, rescue dispatch, veterinary appointments, and an integrated marketplace.",
            architecture=(
                "Architected cleanly using Django's Model-View-Template pattern. Employs Django ORM with SQLite, session-based user authentication, "
                "strict permission decorators for veterinary staff and users, and automated CSRF token validation on all transactional forms."
            ),
            key_features=(
                "Pet adoption portal with filtered search\n"
                "Emergency pet rescue alert reporting system\n"
                "Vaccination booking and history tracking\n"
                "Veterinarian consultation scheduling\n"
                "Pet healthcare and nutrition product marketplace\n"
                "Secure Django authentication with role authorization\n"
                "Mobile-responsive user interface"
            ),
            challenges_and_solutions=(
                "Challenge: Managing overlapping calendar schedules between veterinary doctors and multi-stage adoption approvals while securing user uploads.\n"
                "Solution: Implemented normalized relational database models with timestamp collision checks, strict file extension allowlists, and server-side image processing."
            ),
            technologies="Python, Django, SQLite3, HTML5, CSS3, JavaScript",
            demo_url="",
            github_url="",
            has_interactive_preview=False,
            is_featured=True,
            order=8
        )
        self.stdout.write("  [+] Projects initialized.")

        # 7. Certifications
        Certification.objects.all().delete()
        certs_data = [
            {
                "title": "Offenso Certified Security Professional (OCSP)",
                "issuer": "Offenso Hackers Academy",
                "issue_date": "2026",
                "badge_icon": "bi-shield-check",
                "skills_covered": "Network Reconnaissance, Vulnerability Assessment, Controlled Exploitation, Web App Pentesting, Burp Suite, Metasploit",
                "description": "Comprehensive practical certification testing skills in enterprise network auditing, vulnerability discovery, traffic analysis, and ethical security testing.",
                "order": 1
            },
            {
                "title": "Google Cybersecurity Professional",
                "issuer": "Coursera",
                "issue_date": "2025",
                "badge_icon": "bi-google",
                "skills_covered": "Security Operations, Threat Intelligence, SIEM (Splunk), Python for Security, Network Security, Incident Response",
                "description": "Professional certification covering foundational cybersecurity frameworks, SIEM log monitoring, detection engineering, and incident response playbooks.",
                "order": 2
            },
            {
                "title": "Cisco Networking Basics",
                "issuer": "Cisco Networking Academy",
                "issue_date": "2024",
                "badge_icon": "bi-router",
                "skills_covered": "OSI & TCP/IP Models, IPv4 & IPv6 Subnetting, Ethernet Switching, Routing Fundamentals, Cisco IOS",
                "description": "Official Cisco curriculum covering fundamental network architecture, IP addressing schemas, protocol stacks, and device configuration.",
                "order": 3
            },
            {
                "title": "Introduction to Microsoft Excel",
                "issuer": "Coursera",
                "issue_date": "2024",
                "badge_icon": "bi-file-earmark-excel",
                "skills_covered": "Data Analysis, Formula Modeling, Pivot Tables, VLOOKUP, Data Visualization, Spreadsheet Automation",
                "description": "Comprehensive certification in quantitative data manipulation, advanced spreadsheet formulas, and business data modeling.",
                "order": 4
            },
            {
                "title": "Coding: Development & Advanced Engineering Job Simulation",
                "issuer": "Accenture (Forage)",
                "issue_date": "2024",
                "badge_icon": "bi-code-square",
                "skills_covered": "Software Engineering, Architecture Design, Code Refactoring, Debugging, Enterprise Best Practices",
                "description": "Virtual job simulation completing practical software engineering tasks, algorithm optimization, and enterprise architecture development.",
                "order": 5
            },
            {
                "title": "Excel Skills Job Simulation",
                "issuer": "JPMorgan Chase & Co. (Forage)",
                "issue_date": "2024",
                "badge_icon": "bi-graph-up-arrow",
                "skills_covered": "Financial Modeling, Data Cleaning, Macro Logic, Conditional Functions, Executive Reporting",
                "description": "Completed real-world investment banking financial modeling scenarios, data sanitization, and structured business reporting.",
                "order": 6
            },
            {
                "title": "Python for Data Science and Machine Learning",
                "issuer": "Udemy",
                "issue_date": "2025",
                "badge_icon": "bi-filetype-py",
                "skills_covered": "Python Scripting, Data Analysis, Algorithm Optimization, Mathematical Modeling, Automation",
                "description": "Hands-on mastery of Python data structures, automated analytical scripting, and software problem solving.",
                "order": 7
            },
            {
                "title": "Android Malware Analysis",
                "issuer": "Udemy",
                "issue_date": "2025",
                "badge_icon": "bi-android2",
                "skills_covered": "APK Reverse Engineering, Static & Dynamic Analysis, Permission Auditing, Smali Disassembly, Malware Triage",
                "description": "Specialized security course on decompiling Android packages, analyzing malicious payloads, and understanding mobile threat vectors.",
                "order": 8
            },
            {
                "title": "JavaScript for Beginners Complete Course",
                "issuer": "Udemy",
                "issue_date": "2024",
                "badge_icon": "bi-filetype-js",
                "skills_covered": "DOM Manipulation, Event Architecture, Async/Await, Fetch API, HTML5 Canvas Programming",
                "description": "In-depth foundation in modern JavaScript programming, browser APIs, and asynchronous client-side engineering.",
                "order": 9
            },
            {
                "title": "CSS Crash Course for Beginners",
                "issuer": "Udemy",
                "issue_date": "2024",
                "badge_icon": "bi-filetype-css",
                "skills_covered": "Flexbox, CSS Grid, Responsive Design, CSS Custom Properties, Transitions & Animation",
                "description": "Core mastery of modern layout architecture, cross-device media queries, and performant visual styling.",
                "order": 10
            },
            {
                "title": "Mastering C & C++ Programming: From Fundamentals to Advanced",
                "issuer": "Udemy",
                "issue_date": "2024",
                "badge_icon": "bi-cpu",
                "skills_covered": "Pointers, Manual Memory Allocation, Data Structures, OOP, Low-Level Systems Programming",
                "description": "Deep exploration of foundational computer science, memory management, pointers, and performance-critical systems code.",
                "order": 11
            },
        ]

        for cert in certs_data:
            Certification.objects.create(**cert)
        self.stdout.write(f"  [+] {len(certs_data)} Certifications initialized.")

        # 8. Networking Knowledge Topics
        NetworkKnowledgeTopic.objects.all().delete()
        topics_data = [
            {
                "title": "OSI Model",
                "slug": "osi-model",
                "category": "foundations",
                "badge_tag": "7-Layer Model",
                "short_explanation": "A conceptual framework standardizing network communication into seven distinct abstraction layers.",
                "how_it_works": "Data travels down from Layer 7 (Application) to Layer 1 (Physical) during encapsulation (Data → Segment → Packet → Frame → Bits), and traverses upward during decapsulation at the destination.",
                "practical_use": "Enables systematic fault isolation: by testing layer-by-layer (e.g. cable check -> IP ping -> port test), engineers quickly pinpoint failure points.",
                "troubleshooting_tip": "Always start troubleshooting at Layer 1 and Layer 3: check physical link lights and verify IP connectivity with ping before suspecting application bugs.",
                "relevant_tools": "Wireshark, ping, traceroute, Cable Tester",
                "order": 1
            },
            {
                "title": "TCP/IP Protocol Suite",
                "slug": "tcp-ip",
                "category": "foundations",
                "badge_tag": "Internet Architecture",
                "short_explanation": "The foundational communication model powering the global Internet, composed of Application, Transport, Internet, and Link layers.",
                "how_it_works": "TCP provides reliable, ordered stream delivery via SYN-SYN/ACK-ACK 3-way handshakes and sequence acknowledgments, while UDP provides fast, connectionless datagram delivery.",
                "practical_use": "Every enterprise service runs on TCP/IP: HTTP/S (TCP 80/443), SSH (TCP 22), and DNS (UDP 53).",
                "troubleshooting_tip": "Use netstat -ano or ss -tulpn to check whether a local daemon is listening on the expected TCP port and binding to 0.0.0.0 or 127.0.0.1.",
                "relevant_tools": "netstat, ss, tcpdump, Wireshark",
                "order": 2
            },
            {
                "title": "IPv4 Addressing",
                "slug": "ipv4",
                "category": "addressing",
                "badge_tag": "Layer 3 Addressing",
                "short_explanation": "32-bit numerical label divided into four 8-bit octets expressed in dotted-decimal format (e.g., 192.168.1.1).",
                "how_it_works": "Separates network ID and host ID using a subnet mask. Includes RFC 1918 private address ranges: 10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16.",
                "practical_use": "Internal LAN addressing, static server assignments, router gateway definitions, and firewall rules.",
                "troubleshooting_tip": "Watch for IP address conflicts: check ARP tables (arp -a) if two hosts claim the same IP and generate intermittent dropped connections.",
                "relevant_tools": "arp, ipconfig, ifconfig, ip route",
                "order": 3
            },
            {
                "title": "IPv6 Addressing",
                "slug": "ipv6",
                "category": "addressing",
                "badge_tag": "Next-Gen IP",
                "short_explanation": "128-bit hexadecimal addressing format engineered to overcome IPv4 exhaustion and eliminate mandatory NAT.",
                "how_it_works": "Uses 8 groups of four hexadecimal digits (e.g., 2001:0db8:85a3::8a2e:0370:7334). Eliminates broadcast; relies on multicast and Neighbor Discovery Protocol (NDP).",
                "practical_use": "Modern ISP backbones, mobile carriers, global enterprise edge connectivity, and dual-stack enterprise environments.",
                "troubleshooting_tip": "When troubleshooting IPv6, use ping -6 or ping6 and verify link-local addresses (fe80::/10) on local network interfaces.",
                "relevant_tools": "ping6, traceroute6, Wireshark, ndp",
                "order": 4
            },
            {
                "title": "Subnetting & VLSM",
                "slug": "subnetting",
                "category": "addressing",
                "badge_tag": "IP Allocation",
                "short_explanation": "The mathematical division of a large IP network into smaller, logically segmented subnetworks.",
                "how_it_works": "Borrowing host bits to create network bits. Calculates network address, first usable host, last usable host, and broadcast address.",
                "practical_use": "Prevents IPv4 address waste, reduces broadcast storm radius, and enforces administrative boundaries between teams.",
                "troubleshooting_tip": "Verify subnet masks match on both ends of a point-to-point link; mismatched masks (e.g. /24 vs /25) cause unidirectional routing failures.",
                "relevant_tools": "Subnet Calculator, ipcalc, Python ipaddress",
                "order": 5
            },
            {
                "title": "CIDR (Classless Inter-Domain Routing)",
                "slug": "cidr",
                "category": "addressing",
                "badge_tag": "Prefix Notation",
                "short_explanation": "A method of allocating IP addresses and IP routing using prefix notation (e.g. /24) instead of rigid Class A/B/C boundaries.",
                "how_it_works": "The slash followed by a number indicates how many leading bits constitute the network prefix (e.g., /24 = 255.255.255.0, /28 = 255.255.255.240).",
                "practical_use": "Route summarization (supernetting) to keep global and internal routing tables compact and efficient.",
                "troubleshooting_tip": "Remember: total hosts = 2^(32 - prefix); usable hosts = 2^(32 - prefix) - 2 for prefixes <= /30.",
                "relevant_tools": "Cisco CLI, pfSense Interfaces, ipcalc",
                "order": 6
            },
            {
                "title": "VLAN (Virtual Local Area Network)",
                "slug": "vlan",
                "category": "switching_routing",
                "badge_tag": "Layer 2 Segmentation",
                "short_explanation": "Logically divides a single physical switch into multiple isolated broadcast domains.",
                "how_it_works": "Switches maintain independent MAC address tables per VLAN. Traffic between different VLANs cannot cross at Layer 2 without a Layer 3 router or switch.",
                "practical_use": "Departmental isolation (e.g. VLAN 10 IT, VLAN 20 Admin, VLAN 30 Broadcast/Production, VLAN 40 Guest Wi-Fi) to limit malware lateral movement.",
                "troubleshooting_tip": "Check switchport access vlan <id> assignments. If a host cannot obtain a DHCP lease, confirm its switch port is assigned to the correct VLAN.",
                "relevant_tools": "Cisco show vlan brief, pfSense Interfaces",
                "order": 7
            },
            {
                "title": "802.1Q Trunking",
                "slug": "trunking",
                "category": "switching_routing",
                "badge_tag": "VLAN Tagging",
                "short_explanation": "A standard IEEE protocol that inserts a 4-byte VLAN tag into Ethernet frames to transport multiple VLANs across a single physical link.",
                "how_it_works": "Trunk links connect switches together or connect switches to firewalls (Router-on-a-Stick). Frames receive a 12-bit VLAN ID tag, stripped upon egress to access ports.",
                "practical_use": "Carries all departmental VLANs between core switches and the pfSense firewall over single 10GbE or aggregated fiber uplinks.",
                "troubleshooting_tip": "Verify native VLAN matches on both ends of the trunk; mismatched native VLANs create security vulnerabilities and bridge traffic across domains.",
                "relevant_tools": "Cisco show interfaces trunk, Wireshark",
                "order": 8
            },
            {
                "title": "Routing & Gateways",
                "slug": "routing",
                "category": "switching_routing",
                "badge_tag": "Layer 3 Forwarding",
                "short_explanation": "The process of selecting paths across multiple networks to forward packets toward their destination IP address.",
                "how_it_works": "Routers inspect destination IP headers against their routing table using Longest Prefix Match to determine the next-hop IP and egress interface.",
                "practical_use": "Static routing for internal subnets and default gateways (0.0.0.0/0) directing all non-local traffic to the perimeter firewall.",
                "troubleshooting_tip": "Run traceroute/tracert to locate exactly which router in the hop path is dropping or redirecting the packet.",
                "relevant_tools": "traceroute, tracert, mtr, ip route",
                "order": 9
            },
            {
                "title": "Switching & Spanning Tree (STP)",
                "slug": "switching",
                "category": "switching_routing",
                "badge_tag": "Layer 2 Forwarding",
                "short_explanation": "High-speed hardware frame forwarding based on MAC address tables, with Spanning Tree Protocol (STP) preventing switching loops.",
                "how_it_works": "Switches inspect source MACs to populate CAM tables and destination MACs to forward frames. STP blocks redundant links to prevent devastating broadcast storms.",
                "practical_use": "Enterprise core, distribution, and access layer topologies with redundant uplinks that failover automatically.",
                "troubleshooting_tip": "If network lights blink rapidly and utilization spikes to 100%, check for switching loops and inspect show spanning-tree for topology changes.",
                "relevant_tools": "Cisco show mac address-table, show spanning-tree",
                "order": 10
            },
            {
                "title": "DHCP (Dynamic Host Configuration Protocol)",
                "slug": "dhcp",
                "category": "services_security",
                "badge_tag": "Automated Addressing",
                "short_explanation": "Client-server network management protocol that dynamically assigns IP addresses and network parameters to devices.",
                "how_it_works": "Operates via the 4-step DORA handshake: Discover (broadcast), Offer (unicast/broadcast), Request, Acknowledge over UDP ports 67 (server) and 68 (client).",
                "practical_use": "Automating client IP provisioning across multiple VLANs using DHCP relay agents (IP helper-address) pointing to central servers or pfSense.",
                "troubleshooting_tip": "If a host gets an APIPA address (169.254.x.x), DHCP DORA failed: check DHCP pool exhaustion, relay configuration, or rogue DHCP servers.",
                "relevant_tools": "Wireshark (bootp filter), pfSense DHCP Leases",
                "order": 11
            },
            {
                "title": "DNS (Domain Name System)",
                "slug": "dns",
                "category": "services_security",
                "badge_tag": "Name Resolution",
                "short_explanation": "The hierarchical naming system that translates human-readable domain names (e.g. portfolio.local) into machine-readable IP addresses.",
                "how_it_works": "Queries proceed from client stub resolvers through recursive resolvers, root servers, TLD servers, and authoritative nameservers, utilizing A, AAAA, CNAME, and MX records.",
                "practical_use": "Internal Active Directory DNS integration (.corp/.internal resolution) and secure external recursive DNS with DNSSEC.",
                "troubleshooting_tip": "Test resolution directly with nslookup or dig @<server-ip> domain.com to isolate local cache issues from upstream server failures.",
                "relevant_tools": "dig, nslookup, drill, pfSense DNS Resolver (Unbound)",
                "order": 12
            },
            {
                "title": "NAT (Network Address Translation)",
                "slug": "nat",
                "category": "services_security",
                "badge_tag": "Address Translation",
                "short_explanation": "Maps private RFC 1918 IP addresses in internal networks to public IPv4 addresses for Internet communication.",
                "how_it_works": "Port Address Translation (PAT / NAT Overload) modifies source IP and source port in outbound IP headers, maintaining a state translation table.",
                "practical_use": "Allows thousands of corporate devices across multiple VLANs to share one or more public IP addresses on the WAN.",
                "troubleshooting_tip": "If port forwarding fails, check both the NAT Port Forward rule and the corresponding WAN Firewall Rule in pfSense; both must permit traffic.",
                "relevant_tools": "pfSense NAT Diagnostics, conntrack, tcpdump",
                "order": 13
            },
            {
                "title": "ACL (Access Control Lists)",
                "slug": "acl",
                "category": "services_security",
                "badge_tag": "Traffic Filtering",
                "short_explanation": "Sequential rule sets applied to router or switch interfaces to permit or deny packets based on source/dest IP, port, and protocol.",
                "how_it_works": "Rules are evaluated top-down with First Match semantics; an implicit 'deny all' applies at the end of every list.",
                "practical_use": "Restricting guest VLAN users from accessing server VLAN management ports (e.g. block TCP 22/3389/445 to infrastructure subnets).",
                "troubleshooting_tip": "Always place specific rules above general rules. Check hit counters on Cisco ACLs to verify if traffic is actually matching rule criteria.",
                "relevant_tools": "Cisco show access-lists, pfSense Rules Inspector",
                "order": 14
            },
            {
                "title": "Firewall Architecture",
                "slug": "firewall",
                "category": "services_security",
                "badge_tag": "Perimeter Defense",
                "short_explanation": "Stateful network security system monitoring and controlling incoming and outgoing traffic based on predetermined security rules.",
                "how_it_works": "Tracks connection states (SYN_SENT, ESTABLISHED, FIN_WAIT). Once an outbound connection is permitted, the state table automatically allows return traffic.",
                "practical_use": "pfSense enterprise deployments guarding DMZ streaming servers, isolating broadcast subnets, and inspecting perimeter ingress.",
                "troubleshooting_tip": "Inspect the live firewall state table and system log; verify if packets are blocked by Default Deny or specific interface rules.",
                "relevant_tools": "pfSense System Logs, iptables, pfctl",
                "order": 15
            },
            {
                "title": "VPN (Virtual Private Networks)",
                "slug": "vpn",
                "category": "services_security",
                "badge_tag": "Encrypted Tunnels",
                "short_explanation": "Creates an encrypted, authenticated tunnel over untrusted public networks (the Internet) to securely connect remote users or sites.",
                "how_it_works": "Uses protocols like IPsec (IKEv2) or OpenVPN/WireGuard with strong AES-GCM encryption, HMAC authentication, and Diffie-Hellman key exchange.",
                "practical_use": "Secure site-to-site tunnels connecting branch studios and remote administrative access to internal management VLANs.",
                "troubleshooting_tip": "Phase 1 / Phase 2 negotiation errors in IPsec usually indicate mismatched pre-shared keys, conflicting DH groups, or mismatched proposal ciphers.",
                "relevant_tools": "OpenVPN, WireGuard, IPsec status in pfSense",
                "order": 16
            },
            {
                "title": "Wireless Networking (802.11)",
                "slug": "wireless",
                "category": "operations",
                "badge_tag": "WLAN Architecture",
                "short_explanation": "Radio frequency communication enabling mobile endpoints to connect to the local network infrastructure via Access Points (APs).",
                "how_it_works": "Access Points bridge 802.11 wireless frames to 802.3 Ethernet frames. SSIDs are mapped directly to specific VLANs (e.g., Corporate vs Guest Wi-Fi).",
                "practical_use": "Enterprise WPA2/WPA3-Enterprise (802.1X with RADIUS) for employee laptops and captive portal isolation for guest visitors.",
                "troubleshooting_tip": "Check RF interference, 2.4GHz channel congestion (stick to channels 1, 6, 11), and verify AP trunk ports carry all broadcast SSIDs.",
                "relevant_tools": "Wi-Fi Analyzer, inSSIDer, pfSense Captive Portal",
                "order": 17
            },
            {
                "title": "Network Troubleshooting Methodology",
                "slug": "network-troubleshooting",
                "category": "operations",
                "badge_tag": "Diagnostics Workflow",
                "short_explanation": "A structured, deterministic methodology for isolating, identifying, and resolving network connectivity and performance degradation.",
                "how_it_works": "Follows the systematic procedure: 1) Identify problem & scope, 2) Establish theory of probable cause (bottom-up OSI), 3) Test theory, 4) Formulate plan & implement fix, 5) Verify full functionality, 6) Document findings.",
                "practical_use": "Rapid MTTR (Mean Time To Resolution) for enterprise outages, broadcast stream drops, or domain authentication errors.",
                "troubleshooting_tip": "Never make multiple configuration changes simultaneously; change one variable at a time so you know exactly which action resolved the issue.",
                "relevant_tools": "ping, traceroute, tcpdump, Wireshark, iperf3, SNMP",
                "order": 18
            },
        ]

        for topic in topics_data:
            NetworkKnowledgeTopic.objects.create(**topic)
        self.stdout.write(f"  [+] {len(topics_data)} NetworkKnowledgeTopics created.")

        # 9. Security Tools
        SecurityTool.objects.all().delete()
        tools_data = [
            {
                "name": "Nmap",
                "slug": "nmap",
                "category": "recon",
                "purpose": "Network exploration, port scanning, host discovery, and network security auditing.",
                "how_i_used_it": "Used extensively during my cybersecurity internship at Offenso Hackers Academy for host discovery, port scanning (SYN stealth scans -sS), OS detection (-O), service versioning (-sV), and NSE vulnerability scripts.",
                "typical_syntax": "nmap -sS -sV -p- -T4 -Pn 192.168.10.0/24",
                "icon_class": "bi-radar",
                "order": 1
            },
            {
                "name": "Wireshark",
                "slug": "wireshark",
                "category": "traffic",
                "purpose": "Industry-standard network packet analyzer for deep protocol inspection and traffic diagnostics.",
                "how_i_used_it": "Utilized in both network operations and security auditing to dissect packet exchanges, inspect TLS handshakes, troubleshoot broadcast storms, and analyze suspicious network communications.",
                "typical_syntax": "tshark -i eth0 -f 'tcp port 80 or tcp port 443' -w capture.pcap",
                "icon_class": "bi-file-earmark-binary",
                "order": 2
            },
            {
                "name": "Burp Suite",
                "slug": "burp-suite",
                "category": "web",
                "purpose": "Leading web application security testing framework for HTTP interception and vulnerability scanning.",
                "how_i_used_it": "Hands-on usage during internship to intercept HTTP requests, analyze request/response headers, test parameters with Repeater, and identify vulnerabilities such as XSS, SQLi, and flawed access controls.",
                "typical_syntax": "Burp Proxy 127.0.0.1:8080 -> Intercept -> Repeater / Intruder",
                "icon_class": "bi-bug",
                "order": 3
            },
            {
                "name": "Metasploit",
                "slug": "metasploit",
                "category": "exploit",
                "purpose": "Penetration testing and exploit verification platform used to confirm vulnerability exploitability.",
                "how_i_used_it": "Utilized in controlled laboratory environments at Offenso Hackers Academy to verify discovered vulnerabilities, understand attack vectors, and formulate precise defensive remediation guidance.",
                "typical_syntax": "msfconsole -q -> use exploit/... -> set RHOSTS -> check",
                "icon_class": "bi-terminal-dash",
                "order": 4
            },
            {
                "name": "Splunk",
                "slug": "splunk",
                "category": "siem",
                "purpose": "Enterprise security information and event management (SIEM) for log search, analysis, and alerting.",
                "how_i_used_it": "Studied during the Google Cybersecurity Professional program for parsing event logs, writing SPL (Search Processing Language) queries, correlating security events, and tracking suspicious authentication spikes.",
                "typical_syntax": "index=security sourcetype=wineventlog EventCode=4625 | stats count by user",
                "icon_class": "bi-search",
                "order": 5
            },
            {
                "name": "Gobuster",
                "slug": "gobuster",
                "category": "recon",
                "purpose": "High-performance tool written in Go to brute-force URIs, DNS subdomains, and virtual host names.",
                "how_i_used_it": "Applied during web application security audits to uncover unlinked directories, exposed backup files, hidden admin interfaces, and sensitive endpoints.",
                "typical_syntax": "gobuster dir -u http://target.local -w /usr/share/wordlists/dirb/common.txt -t 30",
                "icon_class": "bi-folder2-open",
                "order": 6
            },
            {
                "name": "Netdiscover",
                "slug": "netdiscover",
                "category": "recon",
                "purpose": "Active and passive address reconnaissance tool based on ARP requests for wireless and wired networks.",
                "how_i_used_it": "Used in local subnet assessments to rapidly map live connected devices and identify unknown MAC hardware vendors on local segments.",
                "typical_syntax": "netdiscover -r 192.168.1.0/24 -i eth0",
                "icon_class": "bi-broadcast",
                "order": 7
            },
            {
                "name": "Hydra",
                "slug": "hydra",
                "category": "exploit",
                "purpose": "Fast network login auditing tool supporting numerous network protocols (SSH, FTP, HTTP, etc.).",
                "how_i_used_it": "Employed in controlled labs to test password strength resilience, verify account lockout policies, and confirm defense-in-depth credential protections.",
                "typical_syntax": "hydra -l admin -P wordlist.txt 192.168.10.50 ssh -t 4",
                "icon_class": "bi-key",
                "order": 8
            },
        ]

        for tool in tools_data:
            SecurityTool.objects.create(**tool)
        self.stdout.write(f"  [+] {len(tools_data)} SecurityTools created.")

        # 10. Security Concepts (Defensive & Educational)
        SecurityConcept.objects.all().delete()
        concepts_data = [
            {
                "title": "SQL Injection (SQLi)",
                "slug": "sql-injection",
                "vulnerability_type": "Injection Vulnerability",
                "owasp_reference": "OWASP A03:2021 - Injection",
                "what_it_is": "A vulnerability occurring when untrusted user input is directly concatenated into database queries without proper parameterization.",
                "why_it_occurs": "The interpreter cannot distinguish between user-supplied data and query control commands, allowing attackers to manipulate SQL execution logic.",
                "impact": "Unauthorized extraction of confidential database records, authentication bypass, data tampering, or full database server compromise.",
                "prevention": "Always use parameterized queries (prepared statements) or Object-Relational Mapping (Django ORM). Never construct raw SQL strings with string formatting.",
                "defensive_detection_idea": "Monitor database logs for anomalous SQL syntax (e.g., OR 1=1, UNION SELECT), deploy Web Application Firewall (WAF) regex inspection, and alert on sudden spikes in database syntax errors.",
                "order": 1
            },
            {
                "title": "Cross-Site Scripting (XSS)",
                "slug": "cross-site-scripting",
                "vulnerability_type": "Client-Side Injection",
                "owasp_reference": "OWASP A03:2021 - Injection",
                "what_it_is": "Flaw allowing malicious scripts to be injected into trusted web applications and executed in the victim's browser session (Stored, Reflected, or DOM-based).",
                "why_it_occurs": "Application reflects user input back into HTML documents without appropriate contextual encoding or input sanitization.",
                "impact": "Session hijacking via session cookie theft, credential harvesting through fake login overlays, or unauthorized actions performed on behalf of the user.",
                "prevention": "Context-aware HTML entity encoding (handled automatically by Django template engine), setting HttpOnly on cookies, and enforcing strict Content Security Policy (CSP).",
                "defensive_detection_idea": "Inspect HTTP request bodies and URL query parameters for script tags, javascript: pseudo-protocols, or event handlers (onload, onerror); configure WAF XSS inspection rules.",
                "order": 2
            },
            {
                "title": "Cross-Site Request Forgery (CSRF)",
                "slug": "csrf",
                "vulnerability_type": "Session Riding",
                "owasp_reference": "OWASP A01:2021 - Broken Access Control",
                "what_it_is": "An attack tricking an authenticated user into executing unwanted actions on a trusted web application where they are currently logged in.",
                "why_it_occurs": "Browsers automatically attach ambient credentials (cookies, HTTP basic auth) with cross-origin requests, so the server cannot distinguish intentional from forged requests without validation tokens.",
                "impact": "Unauthorized state changes such as password changes, email modifications, financial transfers, or privilege escalations.",
                "prevention": "Implement cryptographically strong anti-CSRF tokens (Django's built-in {% csrf_token %} system) and configure SameSite=Lax or SameSite=Strict on all cookies.",
                "defensive_detection_idea": "Audit server logs for 403 Forbidden errors triggered by missing or mismatched CSRF tokens; verify Sec-Fetch-Site and Origin request headers.",
                "order": 3
            },
            {
                "title": "Broken Access Control",
                "slug": "broken-access-control",
                "vulnerability_type": "Authorization Flaw",
                "owasp_reference": "OWASP A01:2021 - Broken Access Control",
                "what_it_is": "Failures in enforcing restrictions on what authenticated users are allowed to access and modify.",
                "why_it_occurs": "Relying on client-side checks, predictable direct object references (IDOR) without server-side ownership verification, or missing role validation on backend endpoints.",
                "impact": "Privilege escalation (standard user accessing admin consoles), unauthorized viewing or modification of other users' sensitive private data.",
                "prevention": "Enforce authorization checks on the server for every single request using role checks (e.g. Django @login_required, @permission_required) and verify resource ownership against request.user.",
                "defensive_detection_idea": "Monitor access logs for 403/401 patterns, automated sequential resource ID increments (IDOR probing), and unauthorized attempts to request /admin or /api/management endpoints.",
                "order": 4
            },
            {
                "title": "Server-Side Request Forgery (SSRF)",
                "slug": "ssrf",
                "vulnerability_type": "Server-Side Flaw",
                "owasp_reference": "OWASP A10:2021 - SSRF",
                "what_it_is": "A vulnerability where an attacker tricks a web server into making unintended requests to internal-only resources or external systems.",
                "why_it_occurs": "Web application accepts a user-provided URL to fetch remote content (e.g. webhook, image preview) without validating the destination IP or domain.",
                "impact": "Access to internal infrastructure management panels (e.g. 192.168.1.1, pfSense webGUI), cloud metadata services (169.254.169.254), or internal port scanning.",
                "prevention": "Enforce strict allowlists of acceptable domains/protocols, disable HTTP redirects, and prohibit connections to RFC 1918 private subnets and loopback addresses.",
                "defensive_detection_idea": "Analyze outbound firewall logs from application servers; alert when web servers initiate outbound connections to private IP ranges or metadata endpoints.",
                "order": 5
            },
            {
                "title": "Command Injection",
                "slug": "command-injection",
                "vulnerability_type": "Operating System Injection",
                "owasp_reference": "OWASP A03:2021 - Injection",
                "what_it_is": "Execution of arbitrary host operating system commands through vulnerable application input fields.",
                "why_it_occurs": "Passing unsanitized user inputs directly into system shell calls (e.g. os.system, exec, shell_exec) without argument isolation.",
                "impact": "Total server compromise, remote reverse shell acquisition, malware installation, and lateral movement into the internal network.",
                "prevention": "Avoid system shell calls entirely; utilize safe native programming language APIs. If system execution is unavoidable, use subprocess with shell=False and strict argument arrays.",
                "defensive_detection_idea": "Inspect auditd and host process monitoring for unexpected child processes spawned by web server workers (e.g. www-data spawning bash, sh, netcat, or curl).",
                "order": 6
            },
            {
                "title": "Brute-Force & Credential Stuffing",
                "slug": "brute-force",
                "vulnerability_type": "Authentication Attack",
                "owasp_reference": "OWASP A07:2021 - Identification & Authentication",
                "what_it_is": "Automated submission of thousands of username/password combinations to guess valid credentials or exploit reused passwords.",
                "why_it_occurs": "Missing rate-limiting mechanisms, lack of CAPTCHA/account lockouts, and absence of Multi-Factor Authentication (MFA).",
                "impact": "Account takeover, unauthorized corporate data access, and unauthorized privilege escalation.",
                "prevention": "Implement IP and username rate-limiting, enforce strong password complexity policies, require Multi-Factor Authentication (MFA), and use progressive delays.",
                "defensive_detection_idea": "Correlate Windows Event ID 4625 (failed logon) and Linux auth.log failed password attempts in SIEM (Splunk); trigger automated IP blocking upon threshold breaches.",
                "order": 7
            },
        ]

        for concept in concepts_data:
            SecurityConcept.objects.create(**concept)
        self.stdout.write(f"  [+] {len(concepts_data)} SecurityConcepts created.")

        # 11. Journal & Security Notes
        BlogCategory.objects.all().delete()
        BlogPost.objects.all().delete()
        SecurityNote.objects.all().delete()

        cat_net_blog = BlogCategory.objects.create(name="Networking & Infrastructure", slug="networking-infrastructure")
        cat_sec_blog = BlogCategory.objects.create(name="Cybersecurity & Hardening", slug="cybersecurity-hardening")
        cat_ops_blog = BlogCategory.objects.create(name="IT Operations & Systems", slug="it-operations-systems")

        BlogPost.objects.create(
            title="Enterprise VLAN Segmentation Architecture: Isolating Broadcast Domains & Threat Surfaces",
            slug="enterprise-vlan-segmentation-architecture",
            category=cat_net_blog,
            summary="A comprehensive guide to planning enterprise VLAN segmentation to isolate broadcast domains, restrict lateral movement, and optimize network traffic.",
            content="""### 1. The Operational Necessity of Segmentation
In modern enterprise environments, flat networks represent an unacceptable risk. When all endpoints share a single broadcast domain, any compromised client can execute ARP poisoning, perform unrestricted port scans, and facilitate rapid lateral movement.

### 2. Designing the Segmentation Schema
At JAIHIND TV and in enterprise laboratories, segmenting by functional department and risk profile provides defense-in-depth:
- **VLAN 10 (Management / IT)**: Switch management interfaces, jump boxes, out-of-band IPMI ports.
- **VLAN 20 (Corporate Administration)**: Standard office workstations, printers, domain controller connectivity.
- **VLAN 30 (Broadcast Production & Streaming)**: High-bandwidth live video ingest servers, Wirecast/OBS workstations.
- **VLAN 40 (Guest & Untrusted Wireless)**: Strictly isolated internet-only access with client-to-client blocking enabled.

### 3. Implementing 802.1Q Trunks & Inter-VLAN Routing
Connecting access switches to the core infrastructure requires 802.1Q tagged trunks:
```text
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 10,20,30,40
Switch(config-if)# switchport trunk native vlan 999
```
All inter-VLAN routing is delegated to a perimeter firewall (pfSense) or Layer 3 core switch where explicit Access Control Lists (ACLs) dictate allowable traffic paths.

### 4. Verification & Hardening
- Disable unused ports and assign them to an unrouted blackhole VLAN.
- Enable DHCP Snooping and Dynamic ARP Inspection (DAI) on untrusted access ports.
- Never use VLAN 1 for operational traffic.""",
            read_time_minutes=6,
            tags="VLAN, Cisco, pfSense, Network Security, 802.1Q",
            published_date=timezone.now().date(),
            is_published=True,
            order=1
        )

        BlogPost.objects.create(
            title="Hardening pfSense Perimeter Firewalls: Stateful Rules, NAT Optimization & Defense-in-Depth",
            slug="hardening-pfsense-perimeter-firewalls",
            category=cat_sec_blog,
            summary="Practical guidelines for configuring stateful packet inspection, strict ingress/egress policies, and alias management on firewalls.",
            content="""### 1. Default Deny as the Baseline
A firewall's primary strength lies in explicit permission rather than broad allowance. In pfSense, the default rule on WAN is an absolute block. On internal interfaces, replace default 'any-to-any' pass rules with strict destination-restricted rules.

### 2. The Power of Aliases for Clean Administration
Managing individual IP addresses directly in firewall rules leads to configuration drift and administrative mistakes. Creating aliases for:
- `DNS_SERVERS`: Approved internal and upstream resolvers.
- `MANAGEMENT_HOSTS`: SysAdmin workstations permitted to access SSH/HTTPS webConfigurator.
- `STREAMING_DESTINATIONS`: External live streaming broadcast endpoints.

This makes firewall rules readable and self-documenting.

### 3. Stateful Connection Inspection
pfSense monitors connection states using FreeBSD's pf packet filter. When a TCP 3-way handshake completes, a state table entry is generated. Return traffic is automatically correlated and allowed, meaning return rules on WAN are never required for client-initiated outbound traffic.

### 4. Essential Hardening Checklist
1. Disable webConfigurator access on WAN and all untrusted VLANs.
2. Change the default webConfigurator port from 443 to a dedicated high port.
3. Configure HTTPS with a custom TLS certificate rather than self-signed defaults.
4. Enable Snort or Suricata package for deep packet inspection and automated threat blocking.""",
            read_time_minutes=5,
            tags="pfSense, Firewall, Network Security, NAT, Hardening",
            published_date=timezone.now().date(),
            is_published=True,
            order=2
        )

        # Security Research Notes for Activity Wall
        SecurityNote.objects.create(
            title="Nmap Timing & Flag Optimization in Segmented Networks",
            category="recon",
            summary="Testing SYN stealth scans (-sS) versus full TCP connects (-sT) across stateful firewall boundaries.",
            key_takeaways="SYN scans leave fewer half-open artifacts in target application logs.\nTiming template -T3 prevents dropped packets on congested WAN links.\nUse -Pn when ICMP echo replies are administratively blocked by perimeter firewalls.",
            date_recorded=timezone.now().date(),
            is_published=True,
            order=1
        )
        SecurityNote.objects.create(
            title="Active Directory Kerberos & Group Policy Hardening",
            category="hardening",
            summary="Audit of domain password policies, Kerberos ticket lifetimes, and least-privilege delegation for departmental OUs.",
            key_takeaways="Enforce fine-grained password policies across administrative accounts.\nDisable SMBv1 network-wide to mitigate legacy protocol exploitation.\nRestrict remote desktop protocol (RDP) access using dedicated GPO security groups.",
            date_recorded=timezone.now().date(),
            is_published=True,
            order=2
        )
        SecurityNote.objects.create(
            title="Burp Suite Interception & Parameter Fuzzing Methodology",
            category="appsec",
            summary="Workflow for mapping application attack surfaces and automating input fuzzing across HTTP POST bodies.",
            key_takeaways="Map full sitemap before launching active scans to avoid hitting destructive logout endpoints.\nUse Intruder with grep-match extractors to identify subtle error message variances in authentication endpoints.\nVerify reflected parameters with contextual encoding checks.",
            date_recorded=timezone.now().date(),
            is_published=True,
            order=3
        )
        SecurityNote.objects.create(
            title="Live Stream Transport & Broadcast Diagnostics",
            category="operations",
            summary="Triage procedures for frame drops, network jitter, and bandwidth optimization during live high-bitrate video broadcasts.",
            key_takeaways="Prioritize encrypted streaming over public ISP backbones.\nVerify QoS traffic shaping ensures broadcast stream queues take priority over administrative traffic.\nMonitor encoder dropped frames percentage in OBS/Wirecast alongside switch port utilization.",
            date_recorded=timezone.now().date(),
            is_published=True,
            order=4
        )
        self.stdout.write("  [+] Journal posts and Security Notes initialized.")

        self.stdout.write(self.style.SUCCESS("Successfully seeded all Abhiram Anil portfolio data!"))
