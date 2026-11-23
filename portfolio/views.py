from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Project, Certification, Skill


def project_detail_api(request, slug):
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
    return JsonResponse(data)


def certification_detail_api(request, pk):
    cert = get_object_or_404(Certification, pk=pk)
    data = {
        'title': cert.title,
        'issuer': cert.issuer,
        'issue_date': cert.issue_date,
        'credential_url': cert.credential_url,
        'badge_icon': cert.badge_icon,
        'skills': cert.get_skills_list(),
        'description': cert.description,
    }
    return JsonResponse(data)
