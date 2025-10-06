from django.urls import path
from . import views

urlpatterns = [
    # API Index
    path('', views.index, name='index'),

    # API Validação de Usuário
    path('api/validar-usuario/', views.validar_usuario, name='validar_usuario'),
    path('api/get-current-user/', views.get_current_user, name='get_current_user'),

    # API Usuarios
    path('api/fiscais/', views.fiscais_list, name='fiscais_list'), #filtro por perfil
    path('api/fiscais/<int:fiscal_id>/', views.fiscais_detail, name='fiscais_detail'),
    path('api/fiscais/perfil-fiscal/', views.fiscais_perfil_fiscal, name='fiscais_perfil_fiscal'),

    # API Barcos
    path('api/barcos/', views.barcos_list, name='barcos_list'),
    path('api/barcos/<int:barco_id>/', views.barcos_detail, name='barcos_detail'),
    path('api/barcos/tipos/', views.barcos_tipos, name='barcos_tipos'),

    # API Modais
    path('api/modais/', views.modais_list, name='modais_list'),

    # API Passagem de Serviço
    path('api/verificar-rascunho/', views.verificar_rascunho, name='verificar_rascunho'),
    path('api/verificar-rascunho-embarcacao/', views.verificar_rascunho_embarcacao, name='verificar_rascunho_embarcacao'),
    path('api/passagens/criar/', views.criar_nova_ps, name='criar_nova_ps'),
    path('api/passagens/<int:ps_id>/', views.passagem_detail, name='passagem_detail'),
    path('api/passagens/usuario/', views.listar_passagens_usuario, name='listar_passagens_usuario'),
    
]