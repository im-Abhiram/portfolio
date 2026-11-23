from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('api/project/<slug:slug>/', views.project_detail_api, name='project_detail_api'),
    path('api/cert/<int:pk>/', views.certification_detail_api, name='cert_detail_api'),
]
