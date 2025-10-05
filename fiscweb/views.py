from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import FiscaisCad
#================================================CADASTRO FISCAIS - API REST=================================================
@csrf_exempt
@require_http_methods(["GET", "POST"])
def fiscais_list(request):
    """
    GET: Lista todos os fiscais
    POST: Cria um novo fiscal
    """
    
    if request.method == 'GET':
        try:
            fiscais = FiscaisCad.objects.all().values(
                'id', 'chave', 'nome', 'email', 'celular', 
                'criado_em', 'atualizado_em'
            )
            fiscais_list = list(fiscais)
            
            print(f"[API] GET /fiscais - Retornando {len(fiscais_list)} fiscais")
            
            return JsonResponse({
                'success': True,
                'data': fiscais_list,
                'count': len(fiscais_list)
            }, safe=False)
            
        except Exception as e:
            print(f"[API ERROR] GET /fiscais - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            print(f"[API] POST /fiscais - Criando fiscal: {data.get('nome')}")
            
            fiscal = FiscaisCad.objects.create(
                chave=data.get('chave'),
                nome=data.get('nome'),
                email=data.get('email'),
                celular=data.get('celular', '')
            )
            
            print(f"[API] POST /fiscais - Fiscal criado com ID: {fiscal.id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Fiscal criado com sucesso',
                'data': {
                    'id': fiscal.id,
                    'chave': fiscal.chave,
                    'nome': fiscal.nome,
                    'email': fiscal.email,
                    'celular': fiscal.celular
                }
            }, status=201)
            
        except Exception as e:
            print(f"[API ERROR] POST /fiscais - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def fiscais_detail(request, fiscal_id):
    """
    GET: Retorna um fiscal específico
    PUT: Atualiza um fiscal
    DELETE: Remove um fiscal
    """
    
    try:
        fiscal = FiscaisCad.objects.get(id=fiscal_id)
    except FiscaisCad.DoesNotExist:
        print(f"[API ERROR] Fiscal ID {fiscal_id} não encontrado")
        return JsonResponse({
            'success': False,
            'error': 'Fiscal não encontrado'
        }, status=404)
    
    if request.method == 'GET':
        print(f"[API] GET /fiscais/{fiscal_id} - {fiscal.nome}")
        return JsonResponse({
            'success': True,
            'data': {
                'id': fiscal.id,
                'chave': fiscal.chave,
                'nome': fiscal.nome,
                'email': fiscal.email,
                'celular': fiscal.celular,
                'criado_em': fiscal.criado_em,
                'atualizado_em': fiscal.atualizado_em
            }
        })
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            print(f"[API] PUT /fiscais/{fiscal_id} - Atualizando: {fiscal.nome}")
            
            fiscal.chave = data.get('chave', fiscal.chave)
            fiscal.nome = data.get('nome', fiscal.nome)
            fiscal.email = data.get('email', fiscal.email)
            fiscal.celular = data.get('celular', fiscal.celular)
            fiscal.save()
            
            print(f"[API] PUT /fiscais/{fiscal_id} - Atualizado com sucesso")
            
            return JsonResponse({
                'success': True,
                'message': 'Fiscal atualizado com sucesso',
                'data': {
                    'id': fiscal.id,
                    'chave': fiscal.chave,
                    'nome': fiscal.nome,
                    'email': fiscal.email,
                    'celular': fiscal.celular
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] PUT /fiscais/{fiscal_id} - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    elif request.method == 'DELETE':
        try:
            nome_fiscal = fiscal.nome
            fiscal.delete()
            
            print(f"[API] DELETE /fiscais/{fiscal_id} - Fiscal '{nome_fiscal}' removido")
            
            return JsonResponse({
                'success': True,
                'message': f'Fiscal {nome_fiscal} removido com sucesso'
            })
            
        except Exception as e:
            print(f"[API ERROR] DELETE /fiscais/{fiscal_id} - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)