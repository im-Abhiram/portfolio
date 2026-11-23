from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.utils.text import slugify

from contact.models import ContactMessage
from portfolio.models import Profile, Project, Skill, Certification, Experience
from core.models import PortfolioSettings

from .captcha import generate_captcha_code, generate_captcha_image
from .forms import (
    PortalLoginForm, ProfileEditForm, PortfolioSettingsEditForm,
    ProjectForm, SkillForm, CertificationForm, ExperienceForm
)


def refresh_captcha_view(request):
    """AJAX endpoint to generate and return a fresh CAPTCHA challenge."""
    code = generate_captcha_code()
    request.session['portal_captcha_code'] = code.upper()
    img_data = generate_captcha_image(code)
    return JsonResponse({'status': 'ok', 'image': img_data})


def portal_login_view(request):
    """Custom high-security NOC authentication portal with visual CAPTCHA verification."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('portal:dashboard')

    next_url = request.GET.get('next') or request.POST.get('next') or 'portal:dashboard'

    if request.method == 'POST':
        form = PortalLoginForm(request.POST)
        session_code = request.session.get('portal_captcha_code', '').strip().upper()
        user_code = request.POST.get('captcha', '').strip().upper()

        # 1. Enforce CAPTCHA security challenge
        if not session_code or user_code != session_code:
            new_code = generate_captcha_code()
            request.session['portal_captcha_code'] = new_code.upper()
            captcha_img = generate_captcha_image(new_code)

            form.is_valid()  # populate cleaned_data/errors
            form.add_error('captcha', "Security challenge verification failed. Please enter the characters shown below.")
            return render(request, 'portal/login.html', {
                'form': form,
                'captcha_img': captcha_img,
                'next': next_url,
            })

        # 2. CAPTCHA passed: single-use token purge
        request.session.pop('portal_captcha_code', None)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active and user.is_staff:
                    django_login(request, user)
                    messages.success(request, f"Authentication verified. Welcome back, {user.username}.")
                    return redirect(next_url)
                else:
                    messages.error(request, "Access restricted. Staff privilege clearance required.")
            else:
                messages.error(request, "Access denied. Invalid operator credentials.")

        # If authentication failed, generate a fresh CAPTCHA for the next attempt
        new_code = generate_captcha_code()
        request.session['portal_captcha_code'] = new_code.upper()
        captcha_img = generate_captcha_image(new_code)
        return render(request, 'portal/login.html', {
            'form': form,
            'captcha_img': captcha_img,
            'next': next_url,
        })
    else:
        form = PortalLoginForm()
        code = generate_captcha_code()
        request.session['portal_captcha_code'] = code.upper()
        captcha_img = generate_captcha_image(code)

    return render(request, 'portal/login.html', {
        'form': form,
        'captcha_img': captcha_img,
        'next': next_url,
    })


def portal_logout_view(request):
    """Terminates operator session and redirects to login."""
    django_logout(request)
    messages.info(request, "Operator session safely terminated. Encryption keys purged.")
    return redirect('portal:login')


@staff_member_required(login_url='portal:login')
def dashboard_view(request):
    """Central Operations HUD for portfolio telemetry and quick management."""
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    total_projects = Project.objects.count()
    total_skills = Skill.objects.count()
    total_certs = Certification.objects.count()
    total_exp = Experience.objects.count()

    recent_messages = ContactMessage.objects.all()[:5]
    profile = Profile.load()
    settings = PortfolioSettings.load()

    context = {
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'total_projects': total_projects,
        'total_skills': total_skills,
        'total_certs': total_certs,
        'total_exp': total_exp,
        'recent_messages': recent_messages,
        'profile': profile,
        'settings': settings,
        'active_tab': 'dashboard',
    }
    return render(request, 'portal/dashboard.html', context)


# ==========================================
# CONTACT MESSAGES INBOX
# ==========================================

@staff_member_required(login_url='portal:login')
def messages_list_view(request):
    """Inbox for visitor transmissions."""
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '').strip()

    messages_qs = ContactMessage.objects.all()

    if status_filter == 'unread':
        messages_qs = messages_qs.filter(is_read=False)
    elif status_filter == 'read':
        messages_qs = messages_qs.filter(is_read=True)

    if search_query:
        messages_qs = messages_qs.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query) |
            Q(ip_address__icontains=search_query)
        )

    unread_count = ContactMessage.objects.filter(is_read=False).count()

    context = {
        'messages_list': messages_qs,
        'status_filter': status_filter,
        'search_query': search_query,
        'unread_count': unread_count,
        'total_count': ContactMessage.objects.count(),
        'active_tab': 'messages',
    }
    return render(request, 'portal/messages_list.html', context)


@staff_member_required(login_url='portal:login')
def message_detail_view(request, pk):
    """View a single visitor transmission and auto-mark as read."""
    msg = get_object_or_404(ContactMessage, pk=pk)
    if not msg.is_read:
        msg.is_read = True
        msg.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'id': msg.pk,
            'name': msg.name,
            'email': msg.email,
            'subject': msg.subject,
            'message': msg.message,
            'ip_address': msg.ip_address,
            'created_at': msg.created_at.strftime('%b %d, %Y %H:%M'),
            'is_read': msg.is_read,
        })

    return redirect('portal:messages')


@staff_member_required(login_url='portal:login')
def message_toggle_read_view(request, pk):
    """Toggle read / unread status of a contact message."""
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = not msg.is_read
    msg.save()
    status_label = "read" if msg.is_read else "unread"
    messages.success(request, f"Transmission #{msg.pk} marked as {status_label}.")
    return redirect(request.META.get('HTTP_REFERER', 'portal:messages'))


@staff_member_required(login_url='portal:login')
def message_delete_view(request, pk):
    """Delete a visitor contact message."""
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    messages.success(request, "Transmission deleted from system logs.")
    return redirect('portal:messages')


# ==========================================
# MAIN PAGE EDITING: PROFILE & SETTINGS
# ==========================================

@staff_member_required(login_url='portal:login')
def profile_edit_view(request):
    """Edit personal brand identity, headlines, and photo shown on the main page."""
    profile = Profile.load()

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile information successfully updated on main page.")
            return redirect('portal:profile_edit')
        else:
            messages.error(request, "Please correct the errors indicated below.")
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'portal/profile_edit.html', {
        'form': form,
        'profile': profile,
        'active_tab': 'profile',
    })


@staff_member_required(login_url='portal:login')
def settings_edit_view(request):
    """Edit global system settings, resume upload, and section toggles."""
    settings = PortfolioSettings.load()

    if request.method == 'POST':
        form = PortfolioSettingsEditForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Portfolio settings and HUD telemetry updated.")
            return redirect('portal:settings_edit')
        else:
            messages.error(request, "Please check the settings form errors.")
    else:
        form = PortfolioSettingsEditForm(instance=settings)

    return render(request, 'portal/settings_edit.html', {
        'form': form,
        'settings': settings,
        'active_tab': 'settings',
    })


# ==========================================
# PROJECTS CRUD
# ==========================================

@staff_member_required(login_url='portal:login')
def projects_list_view(request):
    projects = Project.objects.all().order_by('order', 'title')
    return render(request, 'portal/projects_list.html', {
        'items': projects,
        'active_tab': 'projects',
    })


@staff_member_required(login_url='portal:login')
def project_create_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            if not project.slug:
                project.slug = slugify(project.title)
            project.save()
            messages.success(request, f"Project '{project.title}' added to portfolio.")
            return redirect('portal:projects_list')
    else:
        form = ProjectForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Add New Project',
        'subtitle': 'Deploy new full-stack or infrastructure application to main page',
        'cancel_url': 'portal:projects_list',
        'active_tab': 'projects',
    })


@staff_member_required(login_url='portal:login')
def project_edit_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f"Project '{project.title}' updated.")
            return redirect('portal:projects_list')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': f'Edit Project // {project.title}',
        'subtitle': 'Update architecture, features, live URLs or technical summary',
        'cancel_url': 'portal:projects_list',
        'active_tab': 'projects',
    })


@staff_member_required(login_url='portal:login')
def project_delete_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    title = project.title
    project.delete()
    messages.success(request, f"Project '{title}' removed from portfolio.")
    return redirect('portal:projects_list')


# ==========================================
# SKILLS CRUD
# ==========================================

@staff_member_required(login_url='portal:login')
def skills_list_view(request):
    skills = Skill.objects.select_related('category').all().order_by('category__order', 'order', 'name')
    return render(request, 'portal/skills_list.html', {
        'items': skills,
        'active_tab': 'skills',
    })


@staff_member_required(login_url='portal:login')
def skill_create_view(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save()
            messages.success(request, f"Skill '{skill.name}' added.")
            return redirect('portal:skills_list')
    else:
        form = SkillForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Add Technical Competency',
        'subtitle': 'Add a networking, infrastructure or security skill to your matrix',
        'cancel_url': 'portal:skills_list',
        'active_tab': 'skills',
    })


@staff_member_required(login_url='portal:login')
def skill_edit_view(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, f"Skill '{skill.name}' updated.")
            return redirect('portal:skills_list')
    else:
        form = SkillForm(instance=skill)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': f'Edit Skill // {skill.name}',
        'subtitle': 'Update proficiency tag, icon, or practical description',
        'cancel_url': 'portal:skills_list',
        'active_tab': 'skills',
    })


@staff_member_required(login_url='portal:login')
def skill_delete_view(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    name = skill.name
    skill.delete()
    messages.success(request, f"Skill '{name}' removed.")
    return redirect('portal:skills_list')


# ==========================================
# CERTIFICATIONS CRUD
# ==========================================

@staff_member_required(login_url='portal:login')
def certifications_list_view(request):
    certs = Certification.objects.all().order_by('order', 'title')
    return render(request, 'portal/certifications_list.html', {
        'items': certs,
        'active_tab': 'certifications',
    })


@staff_member_required(login_url='portal:login')
def certification_create_view(request):
    if request.method == 'POST':
        form = CertificationForm(request.POST)
        if form.is_valid():
            cert = form.save()
            messages.success(request, f"Certification '{cert.title}' added.")
            return redirect('portal:certifications_list')
    else:
        form = CertificationForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Add Industry Certification',
        'subtitle': 'Register accredited cybersecurity, networking, or engineering credential',
        'cancel_url': 'portal:certifications_list',
        'active_tab': 'certifications',
    })


@staff_member_required(login_url='portal:login')
def certification_edit_view(request, pk):
    cert = get_object_or_404(Certification, pk=pk)
    if request.method == 'POST':
        form = CertificationForm(request.POST, instance=cert)
        if form.is_valid():
            form.save()
            messages.success(request, f"Certification '{cert.title}' updated.")
            return redirect('portal:certifications_list')
    else:
        form = CertificationForm(instance=cert)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': f'Edit Certification // {cert.title}',
        'subtitle': 'Update issuer, skills covered, or verification badge',
        'cancel_url': 'portal:certifications_list',
        'active_tab': 'certifications',
    })


@staff_member_required(login_url='portal:login')
def certification_delete_view(request, pk):
    cert = get_object_or_404(Certification, pk=pk)
    title = cert.title
    cert.delete()
    messages.success(request, f"Certification '{title}' removed.")
    return redirect('portal:certifications_list')


# ==========================================
# WORK EXPERIENCE CRUD
# ==========================================

@staff_member_required(login_url='portal:login')
def experience_list_view(request):
    experiences = Experience.objects.all().order_by('order', '-is_current')
    return render(request, 'portal/experience_list.html', {
        'items': experiences,
        'active_tab': 'experience',
    })


@staff_member_required(login_url='portal:login')
def experience_create_view(request):
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save()
            messages.success(request, f"Experience entry for '{exp.company}' added.")
            return redirect('portal:experience_list')
    else:
        form = ExperienceForm()

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': 'Add Work Experience',
        'subtitle': 'Add professional IT operations, cybersecurity or network engineering role',
        'cancel_url': 'portal:experience_list',
        'active_tab': 'experience',
    })


@staff_member_required(login_url='portal:login')
def experience_edit_view(request, pk):
    exp = get_object_or_404(Experience, pk=pk)
    if request.method == 'POST':
        form = ExperienceForm(request.POST, instance=exp)
        if form.is_valid():
            form.save()
            messages.success(request, f"Experience for '{exp.company}' updated.")
            return redirect('portal:experience_list')
    else:
        form = ExperienceForm(instance=exp)

    return render(request, 'portal/generic_form.html', {
        'form': form,
        'title': f'Edit Experience // {exp.role} @ {exp.company}',
        'subtitle': 'Update duration, responsibilities or technology stack',
        'cancel_url': 'portal:experience_list',
        'active_tab': 'experience',
    })


@staff_member_required(login_url='portal:login')
def experience_delete_view(request, pk):
    exp = get_object_or_404(Experience, pk=pk)
    comp = exp.company
    exp.delete()
    messages.success(request, f"Experience entry '{comp}' deleted.")
    return redirect('portal:experience_list')
