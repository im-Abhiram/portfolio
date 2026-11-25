from django.urls import path
from . import views

app_name = 'nexus'

urlpatterns = [
    path('api/status/', views.nexus_status_api, name='status'),
    path('api/chat/', views.nexus_chat_api, name='chat'),
]
