from django.urls import path
from . import views

app_name = 'portal'

urlpatterns = [
    # Dashboard & Auth
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.portal_login_view, name='login'),
    path('logout/', views.portal_logout_view, name='logout'),
    path('captcha/refresh/', views.refresh_captcha_view, name='captcha_refresh'),

    # Visitor Contact Transmissions
    path('messages/', views.messages_list_view, name='messages'),
    path('messages/<int:pk>/', views.message_detail_view, name='message_detail'),
    path('messages/<int:pk>/toggle-read/', views.message_toggle_read_view, name='message_toggle_read'),
    path('messages/<int:pk>/delete/', views.message_delete_view, name='message_delete'),

    # Main Page Content Editing: Profile & System Settings
    path('profile/', views.profile_edit_view, name='profile_edit'),
    path('settings/', views.settings_edit_view, name='settings_edit'),

    # Projects
    path('projects/', views.projects_list_view, name='projects_list'),
    path('projects/create/', views.project_create_view, name='project_create'),
    path('projects/<int:pk>/edit/', views.project_edit_view, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete_view, name='project_delete'),

    # Skills
    path('skills/', views.skills_list_view, name='skills_list'),
    path('skills/create/', views.skill_create_view, name='skill_create'),
    path('skills/<int:pk>/edit/', views.skill_edit_view, name='skill_edit'),
    path('skills/<int:pk>/delete/', views.skill_delete_view, name='skill_delete'),

    # Certifications
    path('certifications/', views.certifications_list_view, name='certifications_list'),
    path('certifications/create/', views.certification_create_view, name='certification_create'),
    path('certifications/<int:pk>/edit/', views.certification_edit_view, name='certification_edit'),
    path('certifications/<int:pk>/delete/', views.certification_delete_view, name='certification_delete'),

    # Work Experience
    path('experience/', views.experience_list_view, name='experience_list'),
    path('experience/create/', views.experience_create_view, name='experience_create'),
    path('experience/<int:pk>/edit/', views.experience_edit_view, name='experience_edit'),
    path('experience/<int:pk>/delete/', views.experience_delete_view, name='experience_delete'),

    # Network Intelligence (Daily AI Publisher & Controls)
    path('intelligence/', views.intelligence_list_admin_view, name='intelligence_list'),
    path('intelligence/generate/', views.intelligence_generate_today_view, name='intelligence_generate'),
    path('intelligence/create/', views.intelligence_create_view, name='intelligence_create'),
    path('intelligence/import/', views.intelligence_import_view, name='intelligence_import'),
    path('intelligence/logs/', views.intelligence_logs_view, name='intelligence_logs'),
    path('intelligence/<int:pk>/edit/', views.intelligence_edit_view, name='intelligence_edit'),
    path('intelligence/<int:pk>/publish/', views.intelligence_publish_view, name='intelligence_publish'),
    path('intelligence/<int:pk>/unpublish/', views.intelligence_unpublish_view, name='intelligence_unpublish'),
    path('intelligence/<int:pk>/archive/', views.intelligence_archive_view, name='intelligence_archive'),
    path('intelligence/<int:pk>/delete/', views.intelligence_delete_view, name='intelligence_delete'),
    path('ai-settings/', views.ai_settings_edit_view, name='ai_settings'),

    # Technical Field Notes (Journal Posts)
    path('journal/', views.journal_list_admin_view, name='journal_list'),
    path('journal/create/', views.journal_create_view, name='journal_create'),
    path('journal/<int:pk>/edit/', views.journal_edit_view, name='journal_edit'),
    path('journal/<int:pk>/delete/', views.journal_delete_view, name='journal_delete'),
]
