from django.urls import path
from . import views

urlpatterns = [
    # API Index
    path('', views.index, name='index'),

    # API Validação de Usuário
    path('api/validar-usuario/', views.validar_usuario, name='validar_usuario'),
    path('api/get-current-user/', views.get_current_user, name='get_current_user'),

    # API Fiscais
    path('api/fiscais/', views.fiscais_list, name='fiscais_list'),
    path('api/fiscais/<int:fiscal_id>/', views.fiscais_detail, name='fiscais_detail'),

    # API Barcos
    path('api/barcos/', views.barcos_list, name='barcos_list'),
    path('api/barcos/<int:barco_id>/', views.barcos_detail, name='barcos_detail'),
    path('api/barcos/tipos/', views.barcos_tipos, name='barcos_tipos'),

    # API Modais
    path('api/modais/', views.modais_list, name='modais_list'),
    
]