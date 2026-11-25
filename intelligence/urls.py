from django.urls import path
from . import views

app_name = 'intelligence'

urlpatterns = [
    path('', views.intelligence_list_view, name='list'),
    path('feed/', views.IntelligenceRssFeed(), name='feed'),
    path('subscribe/', views.digest_subscribe_view, name='subscribe'),
    path('<slug:slug>/', views.intelligence_detail_view, name='detail'),
]
