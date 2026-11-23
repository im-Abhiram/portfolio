from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, Http404
from .models import Project, Certification, Skill
import re


def project_detail_api(request, slug):
    # Validate slug format strictly to prevent injection/traversal probes
    if not re.match(r'^[a-zA-Z0-9_\-]+$', slug):
        raise Http404("Invalid project identifier format")

    project = get_object_or_404(Project, slug=slug)
    data = {
        'title': project.title,
        'category': project.category,
        'summary': project.summary,
        'architecture': project.architecture,
        'features': project.get_features_list(),
        'challenges': project.challenges_and_solutions,
        'technologies': project.get_technologies_list(),
        'badge_label': project.badge_label,
        'github_url': project.github_url,
        'demo_url': project.demo_url,
    }
    response = JsonResponse(data)
    response['Cache-Control'] = 'public, max-age=300'
    return response


def certification_detail_api(request, pk):
    try:
        pk_int = int(pk)
    except (ValueError, TypeError):
        raise Http404("Invalid certification ID format")

    cert = get_object_or_404(Certification, pk=pk_int)
    data = {
        'title': cert.title,
        'issuer': cert.issuer,
        'issue_date': cert.issue_date,
        'credential_url': cert.credential_url,
        'badge_icon': cert.badge_icon,
        'skills': cert.get_skills_list(),
        'description': cert.description,
    }
    response = JsonResponse(data)
    response['Cache-Control'] = 'public, max-age=300'
    return response
