from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import FiscaisCad,BarcosCad,ModalBarco
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
                'perfFisc', 'perfAdm',
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
                celular=data.get('celular', ''),
                perfFisc=data.get('perfFisc', False),
                perfAdm=data.get('perfAdm', False)
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
                    'celular': fiscal.celular,
                    'perfFisc': fiscal.perfFisc,
                    'perfAdm': fiscal.perfAdm
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
                'perfFisc': fiscal.perfFisc,
                'perfAdm': fiscal.perfAdm,
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
            fiscal.perfFisc = data.get('perfFisc', fiscal.perfFisc)
            fiscal.perfAdm = data.get('perfAdm', fiscal.perfAdm)
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
                    'celular': fiscal.celular,
                    'perfFisc': fiscal.perfFisc,
                    'perfAdm': fiscal.perfAdm
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
        


#================================================CADASTRO BARCOS - API REST=================================================
@csrf_exempt
@require_http_methods(["GET", "POST"])
def barcos_list(request):
    """
    GET: Lista todos os barcos
    POST: Cria um novo barco
    """
    
    if request.method == 'GET':
        try:
            barcos = BarcosCad.objects.all().values(
                'id', 'tipoBarco', 'nomeBarco', 'modalBarco', 
                'emailPetr', 'dataPrimPorto', 'emprNav', 'icjEmprNav',
                'emprServ', 'icjEmprServ', 'criado_em', 'atualizado_em'
            )
            barcos_list = list(barcos)
            
            print(f"[API] GET /barcos - Retornando {len(barcos_list)} barcos")
            
            return JsonResponse({
                'success': True,
                'data': barcos_list,
                'count': len(barcos_list)
            }, safe=False)
            
        except Exception as e:
            print(f"[API ERROR] GET /barcos - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            print(f"[API] POST /barcos - Criando barco: {data.get('nomeBarco')}")
            
            # Buscar modalSelec se informado
            modal_selec = None
            if data.get('modalSelec_id'):
                try:
                    modal_selec = ModalBarco.objects.get(id=data.get('modalSelec_id'))
                except ModalBarco.DoesNotExist:
                    print(f"[API ERROR] POST /barcos - Modal ID {data.get('modalSelec_id')} não encontrado")
                    return JsonResponse({
                        'success': False,
                        'error': 'Modal não encontrado'
                    }, status=400)
            
            barco = BarcosCad.objects.create(
                tipoBarco=data.get('tipoBarco'),
                nomeBarco=data.get('nomeBarco'),
                modalSelec=modal_selec,
                emailPetr=data.get('emailPetr'),
                dataPrimPorto=data.get('dataPrimPorto'),
                emprNav=data.get('emprNav'),
                icjEmprNav=data.get('icjEmprNav'),
                emprServ=data.get('emprServ'),
                icjEmprServ=data.get('icjEmprServ')
            )
            
            print(f"[API] POST /barcos - Barco criado com ID: {barco.id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Barco criado com sucesso',
                'data': {
                    'id': barco.id,
                    'tipoBarco': barco.tipoBarco,
                    'nomeBarco': barco.nomeBarco,
                    'modalBarco': barco.modalBarco,
                    'emailPetr': barco.emailPetr,
                    'dataPrimPorto': str(barco.dataPrimPorto),
                    'emprNav': barco.emprNav,
                    'icjEmprNav': barco.icjEmprNav,
                    'emprServ': barco.emprServ,
                    'icjEmprServ': barco.icjEmprServ
                }
            }, status=201)
            
        except Exception as e:
            print(f"[API ERROR] POST /barcos - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def barcos_detail(request, barco_id):
    """
    GET: Retorna um barco específico
    PUT: Atualiza um barco
    DELETE: Remove um barco
    """
    
    try:
        barco = BarcosCad.objects.get(id=barco_id)
    except BarcosCad.DoesNotExist:
        print(f"[API ERROR] Barco ID {barco_id} não encontrado")
        return JsonResponse({
            'success': False,
            'error': 'Barco não encontrado'
        }, status=404)
    
    if request.method == 'GET':
        print(f"[API] GET /barcos/{barco_id} - {barco.nomeBarco}")
        return JsonResponse({
            'success': True,
            'data': {
                'id': barco.id,
                'tipoBarco': barco.tipoBarco,
                'nomeBarco': barco.nomeBarco,
                'modalBarco': barco.modalBarco,
                'modalSelec_id': barco.modalSelec.id if barco.modalSelec else None,
                'emailPetr': barco.emailPetr,
                'dataPrimPorto': str(barco.dataPrimPorto),
                'emprNav': barco.emprNav,
                'icjEmprNav': barco.icjEmprNav,
                'emprServ': barco.emprServ,
                'icjEmprServ': barco.icjEmprServ,
                'criado_em': barco.criado_em,
                'atualizado_em': barco.atualizado_em
            }
        })
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            print(f"[API] PUT /barcos/{barco_id} - Atualizando: {barco.nomeBarco}")
            
            # Atualizar modalSelec se informado
            if 'modalSelec_id' in data:
                if data['modalSelec_id']:
                    try:
                        barco.modalSelec = ModalBarco.objects.get(id=data['modalSelec_id'])
                    except ModalBarco.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'error': 'Modal não encontrado'
                        }, status=400)
                else:
                    barco.modalSelec = None
            
            barco.tipoBarco = data.get('tipoBarco', barco.tipoBarco)
            barco.nomeBarco = data.get('nomeBarco', barco.nomeBarco)
            barco.emailPetr = data.get('emailPetr', barco.emailPetr)
            barco.dataPrimPorto = data.get('dataPrimPorto', barco.dataPrimPorto)
            barco.emprNav = data.get('emprNav', barco.emprNav)
            barco.icjEmprNav = data.get('icjEmprNav', barco.icjEmprNav)
            barco.emprServ = data.get('emprServ', barco.emprServ)
            barco.icjEmprServ = data.get('icjEmprServ', barco.icjEmprServ)
            barco.save()
            
            print(f"[API] PUT /barcos/{barco_id} - Atualizado com sucesso")
            
            return JsonResponse({
                'success': True,
                'message': 'Barco atualizado com sucesso',
                'data': {
                    'id': barco.id,
                    'tipoBarco': barco.tipoBarco,
                    'nomeBarco': barco.nomeBarco,
                    'modalBarco': barco.modalBarco,
                    'emailPetr': barco.emailPetr,
                    'dataPrimPorto': str(barco.dataPrimPorto),
                    'emprNav': barco.emprNav,
                    'icjEmprNav': barco.icjEmprNav,
                    'emprServ': barco.emprServ,
                    'icjEmprServ': barco.icjEmprServ
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] PUT /barcos/{barco_id} - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    elif request.method == 'DELETE':
        try:
            nome_barco = barco.nomeBarco
            barco.delete()
            
            print(f"[API] DELETE /barcos/{barco_id} - Barco '{nome_barco}' removido")
            
            return JsonResponse({
                'success': True,
                'message': f'Barco {nome_barco} removido com sucesso'
            })
            
        except Exception as e:
            print(f"[API ERROR] DELETE /barcos/{barco_id} - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

















































































































































