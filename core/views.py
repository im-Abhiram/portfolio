from django.shortcuts import render
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings
import os
import re

from .models import PortfolioSettings
from portfolio.models import Profile, Education, SkillCategory, Experience, Project, Certification
from lab.models import NetworkKnowledgeTopic, SecurityTool, SecurityConcept
from journal.models import BlogPost, SecurityNote
from contact.forms import ContactForm
from intelligence.models import DailyArticle


def home_view(request):
    """
    Primary landing page for Abhiram Anil's portfolio.
    Aggregates all sections into a single responsive, interactive interface.
    """
    settings_obj = PortfolioSettings.load()
    profile_obj = Profile.load()
    
    skill_categories = SkillCategory.objects.prefetch_related('skills').all()
    experiences = Experience.objects.all()
    projects = Project.objects.prefetch_related('images').all()
    certifications = Certification.objects.all()
    educations = Education.objects.all()
    
    network_topics = NetworkKnowledgeTopic.objects.all()
    security_tools = SecurityTool.objects.all()
    security_concepts = SecurityConcept.objects.all()
    
    security_notes = SecurityNote.objects.filter(is_published=True)[:6]
    blog_posts = BlogPost.objects.filter(is_published=True)[:4]

    # Network Intelligence published articles
    published_intel = DailyArticle.objects.filter(status='published')
    featured_intel = published_intel.filter(is_featured=True).first() or published_intel.first()
    latest_intel = (
        published_intel.exclude(pk=featured_intel.pk)[:4]
        if featured_intel else published_intel[:4]
    )
    intel_categories = [c[0] for c in DailyArticle.CATEGORY_CHOICES]
    
    contact_form = ContactForm()

    context = {
        'site_settings': settings_obj,
        'profile': profile_obj,
        'skill_categories': skill_categories,
        'experiences': experiences,
        'projects': projects,
        'certifications': certifications,
        'educations': educations,
        'network_topics': network_topics,
        'security_tools': security_tools,
        'security_concepts': security_concepts,
        'security_notes': security_notes,
        'blog_posts': blog_posts,
        'featured_intel': featured_intel,
        'latest_intel': latest_intel,
        'intel_categories': intel_categories,
        'intel_total_count': published_intel.count(),
        'contact_form': contact_form,
    }
    return render(request, 'core/index.html', context)


def download_resume_view(request):
    """
    Serves the resume document configured in PortfolioSettings.
    If no file was uploaded yet, serves a well-formatted fallback text document
    so visitors always receive a valid download.
    """
    settings_obj = PortfolioSettings.load()
    if settings_obj.resume_file and settings_obj.resume_file.name:
        try:
            file_path = os.path.abspath(settings_obj.resume_file.path)
            media_root = os.path.abspath(settings.MEDIA_ROOT)
            # Ensure path is strictly within MEDIA_ROOT (prevent directory traversal / symlink attacks)
            if file_path.startswith(media_root) and os.path.exists(file_path):
                raw_name = settings_obj.resume_download_name or os.path.basename(file_path)
                # Sanitize filename against header injection / response splitting
                clean_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', raw_name)
                if not clean_name.lower().endswith(('.pdf', '.docx')):
                    clean_name += '.pdf'
                return FileResponse(
                    settings_obj.resume_file.open('rb'),
                    as_attachment=True,
                    filename=clean_name
                )
        except Exception:
            pass  # Fall through to fallback text document safely

    # Fallback resume content based strictly on resume data
    profile = Profile.load()
    fallback_resume = f"""================================================================================
ABHIRAM ANIL - IT INFRASTRUCTURE & CYBERSECURITY PROFESSIONAL
Location: {profile.location} | Phone: {profile.phone} | Email: {profile.email}
GitHub: https://github.com/im-Abhiram | LinkedIn: https://www.linkedin.com/in/imabhiram/
Headline: {profile.headline}
================================================================================

PROFESSIONAL SUMMARY
{profile.about_text}

--------------------------------------------------------------------------------
EDUCATION
--------------------------------------------------------------------------------
A.P.J ABDUL KALAM TECHNOLOGICAL UNIVERSITY — Kerala, India
Bachelor of Technology in Computer Science and Engineering (Graduation: April 2025)
Specialization: Computer Systems Architecture, Networks, Software Engineering & Security

--------------------------------------------------------------------------------
CURRENT EXPERIENCE
--------------------------------------------------------------------------------
JAIHIND TV — Thiruvananthapuram, India
Role: IT Executive (November 2025 – Present)
Key Responsibilities:
• Administered enterprise network infrastructure using Cisco switches and pfSense firewalls.
• Implemented VLAN segmentation for departmental isolation and threat mitigation.
• Managed users, shared resources, permissions and access controls via Active Directory domains & groups.
• Configured RTMP / RTMPS live streaming ingest pipelines through OBS and Wirecast.
• Supported live high-reliability video broadcasts to internal monitoring and public digital streaming destinations.

--------------------------------------------------------------------------------
PREVIOUS EXPERIENCE & INTERNSHIP
--------------------------------------------------------------------------------
OFFENSO HACKERS ACADEMY — Thiruvananthapuram, India
Role: Cybersecurity Intern (August 2025 – February 2026)
Key Responsibilities & Hands-on Training:
• Network reconnaissance, vulnerability assessment, port scanning and network auditing using Nmap.
• Identified potential enterprise attack surfaces and mapped active hosts and services.
• Performed controlled exploitation testing using Metasploit framework and documented technical findings.
• Conducted web application vulnerability assessments using Burp Suite for HTTP traffic interception.
• Analyzed Cross-Site Scripting (XSS), SQL Injection (SQLi), and access control vulnerabilities.

--------------------------------------------------------------------------------
TECHNICAL SKILLS
--------------------------------------------------------------------------------
• Network Infrastructure: Cisco Switching, VLAN Configuration (802.1Q), pfSense Firewall, TCP/IP, Subnetting, Routing & Switching, Network Troubleshooting.
• System Administration: Windows Server Administration, Active Directory, Domain & Group Policy Management, User & Resource Administration, Hardware Diagnostics.
• Cybersecurity: Nmap, Wireshark, Burp Suite, Metasploit Framework, Splunk (SIEM), Gobuster, Netdiscover, Hydra, Vulnerability Assessment.
• Software Development: Python, Django, SQL, JavaScript, C.
• Streaming Infrastructure: OBS Studio, Wirecast, RTMP, RTMPS broadcast protocols.

--------------------------------------------------------------------------------
KEY PROJECTS
--------------------------------------------------------------------------------
1. Network Simulation Platform
   Technologies: Python, Django, JavaScript, HTML5 Canvas, SQLite3, CSS3
   Interactive web platform featuring drag-and-drop network topology designer, rack layout planner, packet flow simulation engine, simulated Cisco IOS CLI, Linux shell, Windows CMD, and CCNA subnetting tools.
   Deployed Webapp: https://ramonet.pythonanywhere.com/ | GitHub: https://github.com/im-Abhiram/toolramo

2. Administrative Portal
   Technologies: Python, Django, SQLite3, RBAC, Audit Logging, Bootstrap
   Production-ready Django workforce management system with automated attendance tracking, leave management with auto-absent sync, shift-based overtime calculator, multi-cycle payroll calculation engine (weekly/bi-weekly/monthly), immutable audit logging, and strict role-based access control.
   Deployed Webapp: https://thamara.pythonanywhere.com/ | GitHub: https://github.com/im-Abhiram/tempsite1

3. Production Tracking System
   Technologies: Python, Django, SQLite3, Analytics Dashboard, PythonAnywhere
   Lightweight, responsive Django and SQLite3 web application built specifically for brick manufacturing and construction material companies to manage end-to-end business operations. Automates factory production shifts, live inventory formulas, client construction site material usage, truck dispatches, worker attendance, and financial credit/payment tracking.
   Deployed Webapp: https://thamarayyathproduction.pythonanywhere.com/ | GitHub: https://github.com/im-Abhiram/inventory

4. Remo — Smart Document & Asset Reminder
   Technologies: Flutter, Dart, SQLite, On-Device OCR, Local Notifications
   Premium offline Flutter application for intelligent receipt management, on-device OCR scanning, warranty tracking with proactive expiration alerts, EMI reminders, document organization, vehicle expenses, medical records, and personal asset management with 100% offline privacy.
   GitHub: https://github.com/im-Abhiram/reme-doccument-remainder-app

5. 6overnews — Modern Sports Media Platform
   Technologies: Python, Django, SQLite3, Bootstrap, HTML5, CSS3, JavaScript
   Modern Django-powered sports news website delivering real-time sports journalism, live match fixtures, league standings, trending stories, and interactive multimedia widgets.
   GitHub: https://github.com/im-Abhiram/6overnews-sports-news-website

6. Real Estate Web Application
   Technologies: Python, Django, SQLite3, HTML5, CSS3, JavaScript
   Modern and responsive real estate web application built with Django, featuring property listings, multi-parameter search filters, agent contact dispatch, and administrative listing management.
   GitHub: https://github.com/im-Abhiram/real-estate-website

7. EASEFOOD — Dynamic Food Ordering Solution
   Technologies: Python, Django, SQLite3, Payment Integration, HTML5, CSS3, JavaScript
   Dynamic food ordering solution featuring real-time order tracking, secure payment integration, and a comprehensive admin dashboard for seamless menu customization and backend order management.

8. Pet World
   Technologies: Python, Django, SQLite, HTML, CSS, JavaScript
   Full-stack Django web application featuring pet adoption, rescue coordination, vaccination booking, veterinarian consultation booking, and a secure marketplace. Built on MVT architecture with robust authentication.

--------------------------------------------------------------------------------
CERTIFICATIONS
--------------------------------------------------------------------------------
• Offenso Certified Security Professional (OCSP) — Offenso Hackers Academy
• Google Cybersecurity Professional — Coursera
• Cisco Networking Basics — Cisco Networking Academy
• Introduction to Microsoft Excel — Coursera
• Coding: Development & Advanced Engineering Job Simulation — Accenture (Forage)
• Excel Skills Job Simulation — JPMorgan Chase & Co. (Forage)
• Python for Data Science and Machine Learning — Udemy
• Android Malware Analysis — Udemy
• JavaScript for Beginners Complete Course — Udemy
• CSS Crash Course for Beginners — Udemy
• Mastering C & C++ Programming: From Fundamentals to Advanced — Udemy

================================================================================
[Generated dynamically by Abhiram Anil Portfolio System]
================================================================================
"""
    response = HttpResponse(fallback_resume, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{settings_obj.resume_download_name}"'
    return response


def custom_404_view(request, exception=None):
    return render(request, 'core/404.html', status=404)


def custom_500_view(request):
    return render(request, 'core/500.html', status=500)
