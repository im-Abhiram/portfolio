from django.urls import path
from . import views

app_name = 'journal'

urlpatterns = [
    path('', views.journal_list_view, name='list'),
    path('<slug:slug>/', views.journal_detail_view, name='detail'),
]
