from django.urls import path
from . import views

app_name = 'lab'

urlpatterns = [
    path('', views.lab_index_view, name='index'),
    path('api/subnet/', views.api_subnet_calc, name='api_subnet_calc'),
]
