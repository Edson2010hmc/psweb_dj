from django.urls import path
from . import views

urlpatterns = [
    # API Fiscais
    path('api/fiscais/', views.fiscais_list, name='fiscais_list'),
    path('api/fiscais/<int:fiscal_id>/', views.fiscais_detail, name='fiscais_detail'),
]