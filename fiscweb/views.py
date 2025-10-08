from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.http.multipartparser import MultiPartParser
from django.core.files.uploadhandler import MemoryFileUploadHandler
from .models import FiscaisCad,BarcosCad,ModalBarco,PassServ
from .models import PortoTrocaTurma
from .models import PortoManutPrev
from .models import PortoAbast
from .models import PortoInspNorm,subTabPortoInspNorm
from .models import PortoInspPetr,subTabPortoInspPetr
from .models import PortoEmbMat,subTabPortoEmbMat
from .models import PortoEmbEquip,subTabPortoEmbEquip
#===============================================RENDERIZA TELA PRINCIPAL=================================================
def index(request):
    """Renderiza a página principal"""
    return render(request, 'index.html')

#===============================================CAPTURA CREDENCIAL WINDOWS - USERNAME=================================================
@csrf_exempt
@require_http_methods(["GET"])
def get_current_user(request):
    """
    Retorna o username do Windows do servidor (temporário para desenvolvimento)
    """
    import getpass
    
    try:
        username = getpass.getuser().upper()
        
        print(f"[AUTH] Username capturado do servidor: '{username}'")
        
        return JsonResponse({
            'success': True,
            'username': username
        })
        
    except Exception as e:
        print(f"[AUTH ERROR] Erro ao capturar username: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
#===============================================VERIFICA CREDENCIAIS DO USUÁRIO=================================================
@csrf_exempt
@require_http_methods(["POST"])
def validar_usuario(request):
    """
    Valida se o username do Windows existe no cadastro de fiscais
    """
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip().upper()
        
        print(f"[AUTH] Validando username: '{username}'")
        
        if not username:
            print("[AUTH ERROR] Username vazio")
            return JsonResponse({
                'success': False,
                'error': 'Username não fornecido'
            }, status=400)
        
        fiscal = FiscaisCad.objects.filter(chave__iexact=username).first()
        
        if not fiscal:
            print(f"[AUTH ERROR] Username '{username}' não encontrado no cadastro")
            return JsonResponse({
                'success': False,
                'authorized': False,
                'message': 'Usuário não autorizado a acessar o sistema'
            }, status=403)
        
        print(f"[AUTH OK] Usuário autorizado: {fiscal.nome}")
        
        return JsonResponse({
            'success': True,
            'authorized': True,
            'data': {
                'id': fiscal.id,
                'chave': fiscal.chave,
                'nome': fiscal.nome,
                'email': fiscal.email,
                'perfFisc': fiscal.perfFisc,
                'perfAdm': fiscal.perfAdm
            }
        })
        
    except Exception as e:
        print(f"[AUTH ERROR] Exceção: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
    
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
        

#================================================CADASTRO FISCAIS - API REST - USUARIOS COM PERFIL DE FISCAL=================================================
@csrf_exempt
@require_http_methods(["GET"])
def fiscais_perfil_fiscal(request):
    """
    Retorna fiscais que possuem perfFisc=True
    """
    try:
        fiscais = FiscaisCad.objects.filter(perfFisc=True).values(
            'id', 'chave', 'nome'
        )
        fiscais_list = list(fiscais)
        
        return JsonResponse({
            'success': True,
            'data': fiscais_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


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
                'id', 'tipoBarco', 'nomeBarco', 'modalBarco', 'modalSelec_id',
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


#================================================ENDPOINTS DE CHOICES E LISTAS=================================================
@csrf_exempt
@require_http_methods(["GET"])
def barcos_tipos(request):
    """
    GET: Retorna as choices de tipos de barcos
    """
    try:
        tipos = [
            {'value': choice[0], 'label': choice[1]} 
            for choice in BarcosCad.barcoTipoChoice
        ]
        
        return JsonResponse({
            'success': True,
            'data': tipos
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def modais_list(request):
    """
    GET: Retorna lista de modais cadastrados
    """
    try:
        modais = ModalBarco.objects.all().values('id', 'modal')
        modais_list = list(modais)
        
        return JsonResponse({
            'success': True,
            'data': modais_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

#================================================PASSAGEM DE SERVIÇO - API REST - VERIFICA RASCUNHO USUARIO=================================================
@csrf_exempt
@require_http_methods(["POST"])
def verificar_rascunho(request):
    """
    Verifica se existe PS em RASCUNHO para o fiscal logado
    """
    try:
        data = json.loads(request.body)
        fiscal_nome = data.get('fiscalNome', '').strip()
        
        if not fiscal_nome:
            return JsonResponse({
                'success': False,
                'error': 'Nome do fiscal não fornecido'
            }, status=400)
        
        # Buscar PS em RASCUNHO para o fiscal desembarcando
        ps_rascunho = PassServ.objects.filter(
            fiscalDes=fiscal_nome,
            statusPS='RASCUNHO'
        ).first()
        
        return JsonResponse({
            'success': True,
            'existeRascunho': ps_rascunho is not None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

#================================================PASSAGEM DE SERVIÇO - API REST - VERIFICA RASCUNHO EMBARCAÇÃO=================================================
@csrf_exempt
@require_http_methods(["POST"])
def verificar_rascunho_embarcacao(request):
    """
    Verifica se existe PS em RASCUNHO para uma embarcação específica
    Retorna dados do fiscal que criou se existir
    """
    try:
        data = json.loads(request.body)
        barco_id = data.get('barcoId')
        fiscal_nome = data.get('fiscalNome', '').strip()
        
        if not barco_id:
            return JsonResponse({
                'success': False,
                'error': 'ID da embarcação não fornecido'
            }, status=400)
        
        # Buscar embarcação
        try:
            barco = BarcosCad.objects.get(id=barco_id)
        except BarcosCad.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Embarcação não encontrada'
            }, status=404)
        
        # Buscar PS em RASCUNHO para essa embarcação
        barco_nome = f"{barco.tipoBarco} - {barco.nomeBarco}"
        ps_rascunho = PassServ.objects.filter(
            BarcoPS=barco_nome,
            statusPS='RASCUNHO'
        ).exclude(fiscalDes=fiscal_nome).first()
        
        if ps_rascunho:
            return JsonResponse({
                'success': True,
                'existeRascunho': True,
                'barcoNome': barco_nome,
                'fiscalNome': ps_rascunho.fiscalDes
            })
        
        return JsonResponse({
            'success': True,
            'existeRascunho': False
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

#================================================PASSAGEM DE SERVIÇO - API REST - DETALHES PS=================================================
@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def passagem_detail(request, ps_id):
    """
    GET: Retorna detalhes de uma PS específica
    PUT: Atualiza uma PS
    DELETE: Remove uma PS
    """
    try:
        ps = PassServ.objects.get(id=ps_id)
        
        if request.method == 'GET':
            return JsonResponse({
                'success': True,
                'data': {
                    'id': ps.id,
                    'numPS': ps.numPS,
                    'anoPS': ps.anoPS,
                    'dataInicio': str(ps.dataInicio),
                    'dataFim': str(ps.dataFim),
                    'dataEmissaoPS': str(ps.dataEmissaoPS),
                    'TipoBarco': ps.TipoBarco,
                    'BarcoPS': ps.BarcoPS,
                    'statusPS': ps.statusPS,
                    'fiscalEmb': ps.fiscalEmb,
                    'fiscalDes': ps.fiscalDes
                }
            })
        
        elif request.method == 'PUT':
            data = json.loads(request.body)
            
            ps.dataEmissaoPS = data.get('dataEmissaoPS', ps.dataEmissaoPS)
            ps.dataInicio = data.get('dataInicio', ps.dataInicio)
            ps.dataFim = data.get('dataFim', ps.dataFim)
            
            if data.get('fiscalEmb'):
                fiscal_emb = FiscaisCad.objects.get(id=data.get('fiscalEmb'))
                ps.fiscalEmb = f"{fiscal_emb.chave} - {fiscal_emb.nome}"
            
            ps.save()
            
            return JsonResponse({
                'success': True,
                'message': 'PS atualizada com sucesso'
            })
        
        elif request.method == 'DELETE':
            ps.delete()
            return JsonResponse({
                'success': True,
                'message': 'PS excluída com sucesso'
            })
        
    except PassServ.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'PS não encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

#================================================PASSAGEM DE SERVIÇO - API REST - CRIA NOVA PS=================================================
@csrf_exempt
@require_http_methods(["POST"])
def criar_nova_ps(request):
    """
    Cria uma nova PS em modo RASCUNHO
    """
    try:
        data = json.loads(request.body)
        
        barco_id = data.get('barcoId')
        fiscal_des_nome = data.get('fiscalDesNome')
        fiscal_emb_id = data.get('fiscalEmbId')
        numero = data.get('numero')
        ano = data.get('ano')
        data_inicio = data.get('dataInicio')
        data_fim = data.get('dataFim')
        data_emissao = data.get('dataEmissao')
        
        # Buscar embarcação
        barco = BarcosCad.objects.get(id=barco_id)
        
        # Buscar fiscal embarcando
        fiscal_emb_nome = ''
        if fiscal_emb_id:
            fiscal_emb = FiscaisCad.objects.get(id=fiscal_emb_id)
            fiscal_emb_nome = f"{fiscal_emb.chave} - {fiscal_emb.nome}"
        
        # Criar PS
        ps = PassServ.objects.create(
            numPS=numero,
            anoPS=str(ano),
            dataInicio=data_inicio,
            dataFim=data_fim,
            dataEmissaoPS=data_emissao,
            TipoBarco=barco.tipoBarco,
            BarcoPS=f"{barco.tipoBarco} - {barco.nomeBarco}",
            statusPS='RASCUNHO',
            fiscalEmb=fiscal_emb_nome,
            fiscalDes=fiscal_des_nome
        )
        
        return JsonResponse({
            'success': True,
            'message': 'PS criada com sucesso',
            'data': {
                'id': ps.id,
                'numPS': ps.numPS,
                'anoPS': ps.anoPS,
                'BarcoPS': ps.BarcoPS,
                'dataInicio': str(ps.dataInicio),
                'dataFim': str(ps.dataFim),
                'dataEmissaoPS': str(ps.dataEmissaoPS),
                'statusPS': ps.statusPS,
                'fiscalEmb': ps.fiscalEmb,
                'fiscalDes': ps.fiscalDes
            }
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

#================================================PASSAGEM DE SERVIÇO - API REST - DETALHES PS=================================================

    """
    GET: Retorna detalhes de uma PS específica
    DELETE: Remove uma PS
    """
    try:
        ps = PassServ.objects.get(id=ps_id)
        
        if request.method == 'GET':
            return JsonResponse({
                'success': True,
                'data': {
                    'id': ps.id,
                    'numPS': ps.numPS,
                    'anoPS': ps.anoPS,
                    'dataInicio': str(ps.dataInicio),
                    'dataFim': str(ps.dataFim),
                    'dataEmissaoPS': str(ps.dataEmissaoPS),
                    'TipoBarco': ps.TipoBarco,
                    'BarcoPS': ps.BarcoPS,
                    'statusPS': ps.statusPS,
                    'fiscalEmb': ps.fiscalEmb,
                    'fiscalDes': ps.fiscalDes
                }
            })
        
        elif request.method == 'DELETE':
            ps.delete()
            return JsonResponse({
                'success': True,
                'message': 'PS excluída com sucesso'
            })
        
    except PassServ.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'PS não encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    """
    Retorna detalhes de uma PS específica
    """
    try:
        ps = PassServ.objects.get(id=ps_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': ps.id,
                'numPS': ps.numPS,
                'anoPS': ps.anoPS,
                'dataInicio': str(ps.dataInicio),
                'dataFim': str(ps.dataFim),
                'dataEmissaoPS': str(ps.dataEmissaoPS),
                'TipoBarco': ps.TipoBarco,
                'BarcoPS': ps.BarcoPS,
                'statusPS': ps.statusPS,
                'fiscalEmb': ps.fiscalEmb,
                'fiscalDes': ps.fiscalDes
            }
        })
        
    except PassServ.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'PS não encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
#================================================PASSAGEM DE SERVIÇO - API REST - LISTA PS USUÁRIO=================================================
@csrf_exempt
@require_http_methods(["GET"])
def listar_passagens_usuario(request):
    """
    Lista todas as PS do usuário logado
    """
    try:
        fiscal_nome = request.GET.get('fiscalNome', '').strip()
        print(f"[DEBUG] Fiscal nome recebido: '{fiscal_nome}'")
        if not fiscal_nome:
            return JsonResponse({
                'success': False,
                'error': 'Nome do fiscal não fornecido'
            }, status=400)
        
        passagens = PassServ.objects.filter(
            fiscalDes=fiscal_nome
        ).order_by('-dataEmissaoPS')

        passagens_list = []
        for ps in passagens:
            passagens_list.append({
                'id': ps.id,
                'numPS': ps.numPS,
                'anoPS': ps.anoPS,
                'BarcoPS': ps.BarcoPS,
                'dataInicio': str(ps.dataInicio),
                'dataFim': str(ps.dataFim),
                'dataEmissaoPS': str(ps.dataEmissaoPS),
                'statusPS': ps.statusPS
            })
        
        return JsonResponse({
            'success': True,
            'data': passagens_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

#================================================TROCA DE TURMA - API REST=================================================
@csrf_exempt
@require_http_methods(["GET", "POST"])
def porto_troca_turma_list(request, ps_id):
    """
    GET: Retorna troca de turma de uma PS (se existir)
    POST: Cria nova troca de turma para uma PS
    """
    
    # Verificar se PS existe
    try:
        ps = PassServ.objects.get(id=ps_id)
    except PassServ.DoesNotExist:
        print(f"[API ERROR] PS ID {ps_id} não encontrada")
        return JsonResponse({
            'success': False,
            'error': 'Passagem de Serviço não encontrada'
        }, status=404)
    
    if request.method == 'GET':
        try:
            troca_turma = PortoTrocaTurma.objects.filter(idxPortoTT=ps).first()
            
            if not troca_turma:
                print(f"[API] GET /ps/{ps_id}/troca-turma/ - Nenhuma troca de turma encontrada")
                return JsonResponse({
                    'success': True,
                    'data': None
                })
            
            print(f"[API] GET /ps/{ps_id}/troca-turma/ - Retornando troca de turma ID {troca_turma.id}")
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': troca_turma.id,
                    'Porto': troca_turma.Porto,
                    'Terminal': troca_turma.Terminal,
                    'OrdSerPorto': troca_turma.OrdSerPorto,
                    'AtracPorto': str(troca_turma.AtracPorto),
                    'DuracPorto': troca_turma.DuracPorto,
                    'ObservPorto': troca_turma.ObservPorto
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] GET /ps/{ps_id}/troca-turma/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Verificar se já existe
            troca_existente = PortoTrocaTurma.objects.filter(idxPortoTT=ps).first()
            if troca_existente:
                print(f"[API ERROR] POST /ps/{ps_id}/troca-turma/ - Já existe troca de turma para esta PS")
                return JsonResponse({
                    'success': False,
                    'error': 'Já existe troca de turma para esta PS'
                }, status=400)
            
            print(f"[API] POST /ps/{ps_id}/troca-turma/ - Criando troca de turma")
            
            troca_turma = PortoTrocaTurma.objects.create(
                idxPortoTT=ps,
                Porto=data.get('Porto', ''),
                Terminal=data.get('Terminal', ''),
                OrdSerPorto=data.get('OrdSerPorto', ''),
                AtracPorto=data.get('AtracPorto'),
                DuracPorto=data.get('DuracPorto', ''),
                ObservPorto=data.get('ObservPorto', '')
            )
            
            print(f"[API] POST /ps/{ps_id}/troca-turma/ - Troca de turma criada com ID: {troca_turma.id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Troca de Turma criada com sucesso',
                'data': {
                    'id': troca_turma.id,
                    'Porto': troca_turma.Porto,
                    'Terminal': troca_turma.Terminal,
                    'OrdSerPorto': troca_turma.OrdSerPorto,
                    'AtracPorto': str(troca_turma.AtracPorto),
                    'DuracPorto': troca_turma.DuracPorto,
                    'ObservPorto': troca_turma.ObservPorto
                }
            }, status=201)
            
        except Exception as e:
            print(f"[API ERROR] POST /ps/{ps_id}/troca-turma/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def porto_troca_turma_detail(request, troca_turma_id):
    """
    PUT: Atualiza troca de turma
    DELETE: Remove troca de turma
    """
    
    try:
        troca_turma = PortoTrocaTurma.objects.get(id=troca_turma_id)
    except PortoTrocaTurma.DoesNotExist:
        print(f"[API ERROR] Troca de Turma ID {troca_turma_id} não encontrada")
        return JsonResponse({
            'success': False,
            'error': 'Troca de Turma não encontrada'
        }, status=404)
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            print(f"[API] PUT /troca-turma/{troca_turma_id}/ - Atualizando troca de turma")
            
            troca_turma.Porto = data.get('Porto', troca_turma.Porto)
            troca_turma.Terminal = data.get('Terminal', troca_turma.Terminal)
            troca_turma.OrdSerPorto = data.get('OrdSerPorto', troca_turma.OrdSerPorto)
            troca_turma.AtracPorto = data.get('AtracPorto', troca_turma.AtracPorto)
            troca_turma.DuracPorto = data.get('DuracPorto', troca_turma.DuracPorto)
            troca_turma.ObservPorto = data.get('ObservPorto', troca_turma.ObservPorto)
            troca_turma.save()
            
            print(f"[API] PUT /troca-turma/{troca_turma_id}/ - Troca de turma atualizada")
            
            return JsonResponse({
                'success': True,
                'message': 'Troca de Turma atualizada com sucesso',
                'data': {
                    'id': troca_turma.id,
                    'Porto': troca_turma.Porto,
                    'Terminal': troca_turma.Terminal,
                    'OrdSerPorto': troca_turma.OrdSerPorto,
                    'AtracPorto': str(troca_turma.AtracPorto),
                    'DuracPorto': troca_turma.DuracPorto,
                    'ObservPorto': troca_turma.ObservPorto
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] PUT /troca-turma/{troca_turma_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    elif request.method == 'DELETE':
        try:
            troca_turma.delete()
            
            print(f"[API] DELETE /troca-turma/{troca_turma_id}/ - Troca de turma removida")
            
            return JsonResponse({
                'success': True,
                'message': 'Troca de Turma removida com sucesso'
            })
            
        except Exception as e:
            print(f"[API ERROR] DELETE /troca-turma/{troca_turma_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


#================================================MANUTENÇÃO PREVENTIVA - API REST=================================================
@csrf_exempt
@require_http_methods(["GET", "POST"])
def porto_manut_prev_list(request, ps_id):
    """
    GET: Retorna manutenção preventiva de uma PS (se existir)
    POST: Cria nova manutenção preventiva para uma PS
    """
    
    # Verificar se PS existe
    try:
        ps = PassServ.objects.get(id=ps_id)
    except PassServ.DoesNotExist:
        print(f"[API ERROR] PS ID {ps_id} não encontrada")
        return JsonResponse({
            'success': False,
            'error': 'Passagem de Serviço não encontrada'
        }, status=404)
    
    if request.method == 'GET':
        try:
            manut_prev = PortoManutPrev.objects.filter(idxPortoMP=ps).first()
            
            if not manut_prev:
                print(f"[API] GET /ps/{ps_id}/manut-prev/ - Nenhuma manutenção preventiva encontrada")
                return JsonResponse({
                    'success': True,
                    'data': None
                })
            
            print(f"[API] GET /ps/{ps_id}/manut-prev/ - Retornando manutenção preventiva ID {manut_prev.id}")
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': manut_prev.id,
                    'prevManPrev': manut_prev.prevManPrev,
                    'Franquia': manut_prev.Franquia,
                    'SaldoFranquia': manut_prev.SaldoFranquia,
                    'OrdSerManutPrev': manut_prev.OrdSerManutPrev,
                    'Rade': manut_prev.Rade.url if manut_prev.Rade else None,
                    'RadeNome': manut_prev.Rade.name.split('/')[-1] if manut_prev.Rade else None,
                    'ObservManPrev': manut_prev.ObservManPrev
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] GET /ps/{ps_id}/manut-prev/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'POST':
        try:
            # Verificar se já existe
            manut_existente = PortoManutPrev.objects.filter(idxPortoMP=ps).first()
            if manut_existente:
                print(f"[API ERROR] POST /ps/{ps_id}/manut-prev/ - Já existe manutenção preventiva para esta PS")
                return JsonResponse({
                    'success': False,
                    'error': 'Já existe manutenção preventiva para esta PS'
                }, status=400)
            
            print(f"[API] POST /ps/{ps_id}/manut-prev/ - Criando manutenção preventiva")
            
            # Dados vêm de request.POST (não JSON) quando tem arquivo
            manut_prev = PortoManutPrev.objects.create(
                idxPortoMP=ps,
                prevManPrev=request.POST.get('prevManPrev', 'false').lower() == 'true',
                Franquia=int(request.POST.get('Franquia', 0)),
                SaldoFranquia=int(request.POST.get('SaldoFranquia', 0)),
                OrdSerManutPrev=request.POST.get('OrdSerManutPrev', ''),
                Rade=request.FILES.get('Rade'),
                ObservManPrev=request.POST.get('ObservManPrev', '')
            )
            
            print(f"[API] POST /ps/{ps_id}/manut-prev/ - Manutenção preventiva criada com ID: {manut_prev.id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Manutenção Preventiva criada com sucesso',
                'data': {
                    'id': manut_prev.id,
                    'prevManPrev': manut_prev.prevManPrev,
                    'Franquia': manut_prev.Franquia,
                    'SaldoFranquia': manut_prev.SaldoFranquia,
                    'OrdSerManutPrev': manut_prev.OrdSerManutPrev,
                    'Rade': manut_prev.Rade.url if manut_prev.Rade else None,
                    'RadeNome': manut_prev.Rade.name.split('/')[-1] if manut_prev.Rade else None,
                    'ObservManPrev': manut_prev.ObservManPrev
                }
            }, status=201)
            
        except Exception as e:
            print(f"[API ERROR] POST /ps/{ps_id}/manut-prev/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def porto_manut_prev_detail(request, manut_prev_id):
    """
    PUT: Atualiza manutenção preventiva
    DELETE: Remove manutenção preventiva
    """
    
    try:
        manut_prev = PortoManutPrev.objects.get(id=manut_prev_id)
    except PortoManutPrev.DoesNotExist:
        print(f"[API ERROR] Manutenção Preventiva ID {manut_prev_id} não encontrada")
        return JsonResponse({
            'success': False,
            'error': 'Manutenção Preventiva não encontrada'
        }, status=404)
    
    if request.method == 'PUT':
        try:
            print(f"[API] PUT /manut-prev/{manut_prev_id}/ - Atualizando manutenção preventiva")
            
            # Parser para FormData em requisições PUT
            if request.content_type and 'multipart/form-data' in request.content_type:
                # Parsear multipart data manualmente
                parser = MultiPartParser(request.META, request, [MemoryFileUploadHandler()])
                PUT, FILES = parser.parse()
                
                print(f"[DEBUG] PUT data parseado: {dict(PUT)}")
                print(f"[DEBUG] FILES parseado: {list(FILES.keys())}")
            else:
                PUT = request.POST
                FILES = request.FILES
            
            # Atualizar campos
            if 'prevManPrev' in PUT:
                manut_prev.prevManPrev = PUT.get('prevManPrev', 'false').lower() == 'true'
            
            if 'Franquia' in PUT:
                franquia = PUT.get('Franquia', '0')
                manut_prev.Franquia = int(franquia) if franquia else 0
            
            if 'SaldoFranquia' in PUT:
                saldo = PUT.get('SaldoFranquia', '0')
                manut_prev.SaldoFranquia = int(saldo) if saldo else 0
            
            if 'OrdSerManutPrev' in PUT:
                manut_prev.OrdSerManutPrev = PUT.get('OrdSerManutPrev', '')
            
            if 'ObservManPrev' in PUT:
                manut_prev.ObservManPrev = PUT.get('ObservManPrev', '')
            
            # Atualizar arquivo se foi enviado
            if 'Rade' in FILES:
                print(f"[DEBUG] Arquivo recebido: {FILES['Rade'].name}")
                
                # Deletar arquivo antigo se existir
                if manut_prev.Rade:
                    import os
                    try:
                        if os.path.isfile(manut_prev.Rade.path):
                            os.remove(manut_prev.Rade.path)
                    except:
                        pass
                
                manut_prev.Rade = FILES['Rade']
            
            manut_prev.save()
            
            print(f"[API] PUT /manut-prev/{manut_prev_id}/ - Dados salvos: Franquia={manut_prev.Franquia}, Saldo={manut_prev.SaldoFranquia}, OS={manut_prev.OrdSerManutPrev}")
            
            return JsonResponse({
                'success': True,
                'message': 'Manutenção Preventiva atualizada com sucesso',
                'data': {
                    'id': manut_prev.id,
                    'prevManPrev': manut_prev.prevManPrev,
                    'Franquia': manut_prev.Franquia,
                    'SaldoFranquia': manut_prev.SaldoFranquia,
                    'OrdSerManutPrev': manut_prev.OrdSerManutPrev,
                    'Rade': manut_prev.Rade.url if manut_prev.Rade else None,
                    'RadeNome': manut_prev.Rade.name.split('/')[-1] if manut_prev.Rade else None,
                    'ObservManPrev': manut_prev.ObservManPrev
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] PUT /manut-prev/{manut_prev_id}/ - {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


#================================================ABASTECIMENTO - API REST=================================================
@csrf_exempt
@require_http_methods(["GET", "POST"])
def porto_abast_list(request, ps_id):
    """
    GET: Retorna abastecimento de uma PS (se existir)
    POST: Cria novo abastecimento para uma PS
    """
    
    # Verificar se PS existe
    try:
        ps = PassServ.objects.get(id=ps_id)
    except PassServ.DoesNotExist:
        print(f"[API ERROR] PS ID {ps_id} não encontrada")
        return JsonResponse({
            'success': False,
            'error': 'Passagem de Serviço não encontrada'
        }, status=404)
    
    if request.method == 'GET':
        try:
            abast = PortoAbast.objects.filter(idxPortoAB=ps).first()
            
            if not abast:
                print(f"[API] GET /ps/{ps_id}/abast/ - Nenhum abastecimento encontrado")
                return JsonResponse({
                    'success': True,
                    'data': None
                })
            
            print(f"[API] GET /ps/{ps_id}/abast/ - Retornando abastecimento ID {abast.id}")
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': abast.id,
                    'prevAbast': abast.prevAbast,
                    'OrdSerAbast': abast.OrdSerAbast or '',
                    'DataHoraPrevAbast': abast.DataHoraPrevAbast.isoformat() if abast.DataHoraPrevAbast else None,
                    'QuantAbast': abast.QuantAbast,
                    'DuracPrev': abast.DuracPrev,
                    'UltAbast': str(abast.UltAbast) if abast.UltAbast else None,
                    'QuantUltAbast': abast.QuantUltAbast,
                    'Anexos': abast.Anexos.url if abast.Anexos else None,
                    'AnexosNome': abast.Anexos.name.split('/')[-1] if abast.Anexos else None,
                    'ObservAbast': abast.ObservAbast or ''
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] GET /ps/{ps_id}/abast/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'POST':
        try:
            # Verificar se já existe
            abast_existente = PortoAbast.objects.filter(idxPortoAB=ps).first()
            if abast_existente:
                print(f"[API ERROR] POST /ps/{ps_id}/abast/ - Já existe abastecimento para esta PS")
                return JsonResponse({
                    'success': False,
                    'error': 'Já existe abastecimento para esta PS'
                }, status=400)
            
            print(f"[API] POST /ps/{ps_id}/abast/ - Criando abastecimento")
            
            abast = PortoAbast.objects.create(
                idxPortoAB=ps,
                prevAbast=True,
                OrdSerAbast='',
                ObservAbast=''
            )
            
            print(f"[API] POST /ps/{ps_id}/abast/ - Abastecimento criado com ID: {abast.id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Abastecimento criado com sucesso',
                'data': {
                    'id': abast.id,
                    'prevAbast': abast.prevAbast
                }
            }, status=201)
            
        except Exception as e:
            print(f"[API ERROR] POST /ps/{ps_id}/abast/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def porto_abast_detail(request, abast_id):
    """
    PUT: Atualiza abastecimento
    DELETE: Remove abastecimento
    """
    
    try:
        abast = PortoAbast.objects.get(id=abast_id)
    except PortoAbast.DoesNotExist:
        print(f"[API ERROR] Abastecimento ID {abast_id} não encontrado")
        return JsonResponse({
            'success': False,
            'error': 'Abastecimento não encontrado'
        }, status=404)
    
    if request.method == 'PUT':
        try:
            print(f"[API] PUT /abast/{abast_id}/ - Atualizando abastecimento")
            
            # Parser para FormData em requisições PUT
            if request.content_type and 'multipart/form-data' in request.content_type:
                parser = MultiPartParser(request.META, request, [MemoryFileUploadHandler()])
                PUT, FILES = parser.parse()
                print(f"[DEBUG] PUT data parseado: {dict(PUT)}")
                print(f"[DEBUG] FILES parseado: {list(FILES.keys())}")
            else:
                PUT = request.POST
                FILES = request.FILES
            
            # Atualizar campos
            if 'prevAbast' in PUT:
                abast.prevAbast = PUT.get('prevAbast', 'false').lower() == 'true'
            
            if 'OrdSerAbast' in PUT:
                abast.OrdSerAbast = PUT.get('OrdSerAbast', '')
            
            if 'DataHoraPrevAbast' in PUT:
                data_hora = PUT.get('DataHoraPrevAbast')
                if data_hora:
                    from django.utils.dateparse import parse_datetime
                    abast.DataHoraPrevAbast = parse_datetime(data_hora)
            
            if 'QuantAbast' in PUT:
                qtd = PUT.get('QuantAbast', '')
                abast.QuantAbast = int(qtd) if qtd else None
            
            if 'DuracPrev' in PUT:
                duracao = PUT.get('DuracPrev', '')
                abast.DuracPrev = int(duracao) if duracao else None
            
            if 'UltAbast' in PUT:
                abast.UltAbast = PUT.get('UltAbast') or None
            
            if 'QuantUltAbast' in PUT:
                qtd_ult = PUT.get('QuantUltAbast', '')
                abast.QuantUltAbast = int(qtd_ult) if qtd_ult else None
            
            if 'ObservAbast' in PUT:
                abast.ObservAbast = PUT.get('ObservAbast', '')
            
            # Atualizar arquivo se foi enviado
            if 'Anexos' in FILES:
                print(f"[DEBUG] Arquivo recebido: {FILES['Anexos'].name}")
                
                # Deletar arquivo antigo se existir
                if abast.Anexos:
                    import os
                    try:
                        if os.path.isfile(abast.Anexos.path):
                            os.remove(abast.Anexos.path)
                    except:
                        pass
                
                abast.Anexos = FILES['Anexos']
            
            abast.save()
            
            print(f"[API] PUT /abast/{abast_id}/ - Dados salvos")
            
            return JsonResponse({
                'success': True,
                'message': 'Abastecimento atualizado com sucesso',
                'data': {
                    'id': abast.id,
                    'prevAbast': abast.prevAbast,
                    'OrdSerAbast': abast.OrdSerAbast or '',
                    'DataHoraPrevAbast': abast.DataHoraPrevAbast.isoformat() if abast.DataHoraPrevAbast else None,
                    'QuantAbast': abast.QuantAbast,
                    'DuracPrev': abast.DuracPrev,
                    'UltAbast': str(abast.UltAbast) if abast.UltAbast else None,
                    'QuantUltAbast': abast.QuantUltAbast,
                    'Anexos': abast.Anexos.url if abast.Anexos else None,
                    'AnexosNome': abast.Anexos.name.split('/')[-1] if abast.Anexos else None,
                    'ObservAbast': abast.ObservAbast or ''
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] PUT /abast/{abast_id}/ - {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    elif request.method == 'DELETE':
        try:
            abast.delete()
            
            print(f"[API] DELETE /abast/{abast_id}/ - Abastecimento removido")
            
            return JsonResponse({
                'success': True,
                'message': 'Abastecimento removido com sucesso'
            })
            
        except Exception as e:
            print(f"[API ERROR] DELETE /abast/{abast_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def buscar_ultimo_abastecimento(request, ps_id):
    """
    Busca o último abastecimento em PSs anteriores da mesma embarcação
    """
    try:
        ps_atual = PassServ.objects.get(id=ps_id)
    except PassServ.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'PS não encontrada'
        }, status=404)
    
    try:
        # Buscar PSs anteriores da mesma embarcação, ordenadas da mais recente para mais antiga
        ps_anteriores = PassServ.objects.filter(
            BarcoPS=ps_atual.BarcoPS,
            dataEmissaoPS__lt=ps_atual.dataEmissaoPS
        ).order_by('-dataEmissaoPS')
        
        print(f"[API] Buscando último abastecimento para {ps_atual.BarcoPS} - {ps_anteriores.count()} PSs anteriores encontradas")
        
        # Percorrer PSs anteriores buscando abastecimento
        for ps_ant in ps_anteriores:
            abast = PortoAbast.objects.filter(idxPortoAB=ps_ant, prevAbast=True).first()
            
            if abast and abast.DataHoraPrevAbast and abast.QuantAbast:
                print(f"[API] Último abastecimento encontrado na PS {ps_ant.numPS}/{ps_ant.anoPS}")
                
                return JsonResponse({
                    'success': True,
                    'encontrado': True,
                    'data': {
                        'UltAbast': abast.DataHoraPrevAbast.date().isoformat(),
                        'QuantUltAbast': abast.QuantAbast,
                        'psOrigem': f"{ps_ant.numPS}/{ps_ant.anoPS}"
                    }
                })
        
        # Não encontrou em nenhuma PS anterior
        print(f"[API] Nenhum abastecimento encontrado em PSs anteriores")
        
        return JsonResponse({
            'success': True,
            'encontrado': False,
            'mensagem': 'Não Informado em PSs anteriores'
        })
        
    except Exception as e:
        print(f"[API ERROR] Erro ao buscar último abastecimento: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

#================================================INSPEÇÃO NORMATIVA (PRINCIPAL) - API REST=================================================
@csrf_exempt
@require_http_methods(["GET", "POST"])
def porto_insp_norm_list(request, ps_id):
    """
    GET: Retorna inspeção normativa de uma PS (se existir)
    POST: Cria nova inspeção normativa para uma PS
    """
    
    # Verificar se PS existe
    try:
        ps = PassServ.objects.get(id=ps_id)
    except PassServ.DoesNotExist:
        print(f"[API ERROR] PS ID {ps_id} não encontrada")
        return JsonResponse({
            'success': False,
            'error': 'Passagem de Serviço não encontrada'
        }, status=404)
    
    if request.method == 'GET':
        try:
            insp_norm = PortoInspNorm.objects.filter(idxPortoIN=ps).first()
            
            if not insp_norm:
                print(f"[API] GET /ps/{ps_id}/insp-norm/ - Nenhuma inspeção encontrada")
                return JsonResponse({
                    'success': True,
                    'data': None
                })
            
            print(f"[API] GET /ps/{ps_id}/insp-norm/ - Retornando inspeção ID {insp_norm.id}")
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': insp_norm.id,
                    'prevInsNorm': insp_norm.prevInsNorm,
                    'ObservInspNorm': insp_norm.ObservInspNorm
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] GET /ps/{ps_id}/insp-norm/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Verificar se já existe
            insp_existente = PortoInspNorm.objects.filter(idxPortoIN=ps).first()
            if insp_existente:
                print(f"[API ERROR] POST /ps/{ps_id}/insp-norm/ - Já existe inspeção para esta PS")
                return JsonResponse({
                    'success': False,
                    'error': 'Já existe inspeção normativa para esta PS'
                }, status=400)
            
            print(f"[API] POST /ps/{ps_id}/insp-norm/ - Criando inspeção")
            
            insp_norm = PortoInspNorm.objects.create(
                idxPortoIN=ps,
                prevInsNorm=data.get('prevInsNorm', False),
                ObservInspNorm=data.get('ObservInspNorm', '')
            )
            
            print(f"[API] POST /ps/{ps_id}/insp-norm/ - Inspeção criada com ID: {insp_norm.id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Inspeção Normativa criada com sucesso',
                'data': {
                    'id': insp_norm.id,
                    'prevInsNorm': insp_norm.prevInsNorm,
                    'ObservInspNorm': insp_norm.ObservInspNorm
                }
            }, status=201)
            
        except Exception as e:
            print(f"[API ERROR] POST /ps/{ps_id}/insp-norm/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def porto_insp_norm_detail(request, insp_norm_id):
    """
    PUT: Atualiza inspeção normativa
    DELETE: Remove inspeção normativa
    """
    
    try:
        insp_norm = PortoInspNorm.objects.get(id=insp_norm_id)
    except PortoInspNorm.DoesNotExist:
        print(f"[API ERROR] Inspeção Normativa ID {insp_norm_id} não encontrada")
        return JsonResponse({
            'success': False,
            'error': 'Inspeção Normativa não encontrada'
        }, status=404)
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            print(f"[API] PUT /insp-norm/{insp_norm_id}/ - Atualizando inspeção")
            
            insp_norm.prevInsNorm = data.get('prevInsNorm', insp_norm.prevInsNorm)
            insp_norm.ObservInspNorm = data.get('ObservInspNorm', insp_norm.ObservInspNorm)
            insp_norm.save()
            
            print(f"[API] PUT /insp-norm/{insp_norm_id}/ - Inspeção atualizada")
            
            return JsonResponse({
                'success': True,
                'message': 'Inspeção Normativa atualizada com sucesso',
                'data': {
                    'id': insp_norm.id,
                    'prevInsNorm': insp_norm.prevInsNorm,
                    'ObservInspNorm': insp_norm.ObservInspNorm
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] PUT /insp-norm/{insp_norm_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    elif request.method == 'DELETE':
        try:
            # Ao deletar, remove também todos os itens da subtabela (CASCADE)
            insp_norm.delete()
            
            print(f"[API] DELETE /insp-norm/{insp_norm_id}/ - Inspeção removida")
            
            return JsonResponse({
                'success': True,
                'message': 'Inspeção Normativa removida com sucesso'
            })
            
        except Exception as e:
            print(f"[API ERROR] DELETE /insp-norm/{insp_norm_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

#================================================INSPEÇÃO NORMATIVA - SUBTABELA - API REST=================================================
@csrf_exempt
@require_http_methods(["GET", "POST"])
def subtab_insp_norm_list(request, insp_norm_id):
    """
    GET: Lista itens da subtabela de uma inspeção normativa
    POST: Adiciona novo item à subtabela
    """
    
    # Verificar se inspeção normativa existe
    try:
        insp_norm = PortoInspNorm.objects.get(id=insp_norm_id)
    except PortoInspNorm.DoesNotExist:
        print(f"[API ERROR] Inspeção Normativa ID {insp_norm_id} não encontrada")
        return JsonResponse({
            'success': False,
            'error': 'Inspeção Normativa não encontrada'
        }, status=404)
    
    if request.method == 'GET':
        try:
            itens = subTabPortoInspNorm.objects.filter(
                idxsubTabPortoInspNorm=insp_norm
            ).values('id', 'DescInspNorm', 'OrdSerInspNorm')
            
            itens_list = list(itens)
            
            print(f"[API] GET /subtab-insp-norm/{insp_norm_id}/ - Retornando {len(itens_list)} itens")
            
            return JsonResponse({
                'success': True,
                'data': itens_list
            })
            
        except Exception as e:
            print(f"[API ERROR] GET /subtab-insp-norm/{insp_norm_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            print(f"[API] POST /subtab-insp-norm/{insp_norm_id}/ - Criando item")
            
            item = subTabPortoInspNorm.objects.create(
                idxsubTabPortoInspNorm=insp_norm,
                DescInspNorm=data.get('DescInspNorm'),
                OrdSerInspNorm=data.get('OrdSerInspNorm')
            )
            
            print(f"[API] POST /subtab-insp-norm/{insp_norm_id}/ - Item criado com ID: {item.id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Item adicionado com sucesso',
                'data': {
                    'id': item.id,
                    'DescInspNorm': item.DescInspNorm,
                    'OrdSerInspNorm': item.OrdSerInspNorm
                }
            }, status=201)
            
        except Exception as e:
            print(f"[API ERROR] POST /subtab-insp-norm/{insp_norm_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def subtab_insp_norm_detail(request, item_id):
    """
    PUT: Atualiza um item da subtabela
    DELETE: Remove um item da subtabela
    """
    
    try:
        item = subTabPortoInspNorm.objects.get(id=item_id)
    except subTabPortoInspNorm.DoesNotExist:
        print(f"[API ERROR] Item ID {item_id} não encontrado")
        return JsonResponse({
            'success': False,
            'error': 'Item não encontrado'
        }, status=404)
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            print(f"[API] PUT /subtab-insp-norm-item/{item_id}/ - Atualizando item")
            
            item.DescInspNorm = data.get('DescInspNorm', item.DescInspNorm)
            item.OrdSerInspNorm = data.get('OrdSerInspNorm', item.OrdSerInspNorm)
            item.save()
            
            print(f"[API] PUT /subtab-insp-norm-item/{item_id}/ - Item atualizado")
            
            return JsonResponse({
                'success': True,
                'message': 'Item atualizado com sucesso',
                'data': {
                    'id': item.id,
                    'DescInspNorm': item.DescInspNorm,
                    'OrdSerInspNorm': item.OrdSerInspNorm
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] PUT /subtab-insp-norm-item/{item_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    elif request.method == 'DELETE':
        try:
            item.delete()
            
            print(f"[API] DELETE /subtab-insp-norm-item/{item_id}/ - Item removido")
            
            return JsonResponse({
                'success': True,
                'message': 'Item removido com sucesso'
            })
            
        except Exception as e:
            print(f"[API ERROR] DELETE /subtab-insp-norm-item/{item_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)


#================================================INSPEÇÃO PETROBRAS - API REST=================================================
@csrf_exempt
@require_http_methods(["GET", "POST"])
def porto_insp_petr_list(request, ps_id):
    """
    GET: Retorna inspeção Petrobras de uma PS (se existir)
    POST: Cria nova inspeção Petrobras para uma PS
    """
    
    try:
        ps = PassServ.objects.get(id=ps_id)
    except PassServ.DoesNotExist:
        print(f"[API ERROR] PS ID {ps_id} não encontrada")
        return JsonResponse({
            'success': False,
            'error': 'Passagem de Serviço não encontrada'
        }, status=404)
    
    if request.method == 'GET':
        try:
            insp_petr = PortoInspPetr.objects.filter(idxPortoIP=ps).first()
            
            if not insp_petr:
                print(f"[API] GET /ps/{ps_id}/insp-petr/ - Nenhuma inspeção Petrobras encontrada")
                return JsonResponse({
                    'success': True,
                    'data': None
                })
            
            print(f"[API] GET /ps/{ps_id}/insp-petr/ - Retornando inspeção Petrobras ID {insp_petr.id}")
            
            return JsonResponse({
                'success': True,
                'data': {
                    'id': insp_petr.id,
                    'prevInspPetr': insp_petr.prevInspPetr,
                    'ObservInspPetr': insp_petr.ObservInspPetr
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] GET /ps/{ps_id}/insp-petr/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'POST':
        try:
            insp_existente = PortoInspPetr.objects.filter(idxPortoIP=ps).first()
            if insp_existente:
                print(f"[API ERROR] POST /ps/{ps_id}/insp-petr/ - Já existe inspeção Petrobras para esta PS")
                return JsonResponse({
                    'success': False,
                    'error': 'Já existe Registro de Insara esta PS'
                }, status=400)
            
            print(f"[API] POST /ps/{ps_id}/insp-petr/ - Criando inspeção Petrobras")
            
            insp_petr = PortoInspPetr.objects.create(
                idxPortoIP=ps,
                prevInspPetr=True,
                ObservInspPetr=''
            )
            
            print(f"[API] POST /ps/{ps_id}/insp-petr/ - Inspeção Petrobras criada com ID: {insp_petr.id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Resgistro criado com sucesso',
                'data': {
                    'id': insp_petr.id,
                    'prevInspPetr': insp_petr.prevInspPetr,
                    'ObservInspPetr': insp_petr.ObservInspPetr
                }
            }, status=201)
            
        except Exception as e:
            print(f"[API ERROR] POST /ps/{ps_id}/insp-petr/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def porto_insp_petr_detail(request, insp_petr_id):
    """
    PUT: Atualiza inspeção Petrobras
    DELETE: Remove inspeção Petrobras
    """
    
    try:
        insp_petr = PortoInspPetr.objects.get(id=insp_petr_id)
    except PortoInspPetr.DoesNotExist:
        print(f"[API ERROR] Registro ID {insp_petr_id} não encontrada")
        return JsonResponse({
            'success': False,
            'error': 'Inspeção Petrobras não encontrada'
        }, status=404)
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            print(f"[API] PUT /insp-petr/{insp_petr_id}/ - Atualizando inspeção Petrobras")
            
            insp_petr.prevInspPetr = data.get('prevInspPetr', insp_petr.prevInspPetr)
            insp_petr.ObservInspPetr = data.get('ObservInspPetr', insp_petr.ObservInspPetr)
            insp_petr.save()
            
            print(f"[API] PUT /insp-petr/{insp_petr_id}/ - Inspeção Petrobras atualizada")
            
            return JsonResponse({
                'success': True,
                'message': 'Registro atualizado com sucesso',
                'data': {
                    'id': insp_petr.id,
                    'prevInspPetr': insp_petr.prevInspPetr,
                    'ObservInspPetr': insp_petr.ObservInspPetr
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] PUT /insp-petr/{insp_petr_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    elif request.method == 'DELETE':
        try:
            insp_petr.delete()
            
            print(f"[API] DELETE /insp-petr/{insp_petr_id}/ - Inspeção Petrobras removida")
            
            return JsonResponse({
                'success': True,
                'message': 'Registro removido com sucesso'
            })
            
        except Exception as e:
            print(f"[API ERROR] DELETE /insp-petr/{insp_petr_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

#================================================INSPEÇÃO PETROBRAS - SUBTABELA - API REST=================================================
@csrf_exempt
@require_http_methods(["GET", "POST"])
def subtab_insp_petr_list(request, insp_petr_id):
    """
    GET: Lista itens da subtabela de inspeção Petrobras
    POST: Adiciona novo item à subtabela
    """
    
    try:
        insp_petr = PortoInspPetr.objects.get(id=insp_petr_id)
    except PortoInspPetr.DoesNotExist:
        print(f"[API ERROR] Inspeção Petrobras ID {insp_petr_id} não encontrada")
        return JsonResponse({
            'success': False,
            'error': 'Registro não encontrado'
        }, status=404)
    
    if request.method == 'GET':
        try:
            itens = subTabPortoInspPetr.objects.filter(
                idxsubTabPortoIP=insp_petr
            ).values('id', 'DescInspPetr', 'auditorPetr', 'gerAuditorPetr')
            
            itens_list = list(itens)
            
            print(f"[API] GET /subtab-insp-petr/{insp_petr_id}/ - Retornando {len(itens_list)} itens")
            
            return JsonResponse({
                'success': True,
                'data': itens_list
            })
            
        except Exception as e:
            print(f"[API ERROR] GET /subtab-insp-petr/{insp_petr_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            print(f"[API] POST /subtab-insp-petr/{insp_petr_id}/ - Criando item")
            
            item = subTabPortoInspPetr.objects.create(
                idxsubTabPortoIP=insp_petr,
                DescInspPetr=data.get('DescInspPetr'),
                auditorPetr=data.get('auditorPetr'),
                gerAuditorPetr=data.get('gerAuditorPetr')
            )
            
            print(f"[API] POST /subtab-insp-petr/{insp_petr_id}/ - Item criado com ID: {item.id}")
            
            return JsonResponse({
                'success': True,
                'message': 'Item adicionado com sucesso',
                'data': {
                    'id': item.id,
                    'DescInspPetr': item.DescInspPetr,
                    'auditorPetr': item.auditorPetr,
                    'gerAuditorPetr': item.gerAuditorPetr
                }
            }, status=201)
            
        except Exception as e:
            print(f"[API ERROR] POST /subtab-insp-petr/{insp_petr_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)

@csrf_exempt
@require_http_methods(["PUT", "DELETE"])
def subtab_insp_petr_detail(request, item_id):
    """
    PUT: Atualiza um item da subtabela
    DELETE: Remove um item da subtabela
    """
    
    try:
        item = subTabPortoInspPetr.objects.get(id=item_id)
    except subTabPortoInspPetr.DoesNotExist:
        print(f"[API ERROR] Item ID {item_id} não encontrado")
        return JsonResponse({
            'success': False,
            'error': 'Item não encontrado'
        }, status=404)
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            print(f"[API] PUT /subtab-insp-petr-item/{item_id}/ - Atualizando item")
            
            item.DescInspPetr = data.get('DescInspPetr', item.DescInspPetr)
            item.auditorPetr = data.get('auditorPetr', item.auditorPetr)
            item.gerAuditorPetr = data.get('gerAuditorPetr', item.gerAuditorPetr)
            item.save()
            
            print(f"[API] PUT /subtab-insp-petr-item/{item_id}/ - Item atualizado")
            
            return JsonResponse({
                'success': True,
                'message': 'Item atualizado com sucesso',
                'data': {
                    'id': item.id,
                    'DescInspPetr': item.DescInspPetr,
                    'auditorPetr': item.auditorPetr,
                    'gerAuditorPetr': item.gerAuditorPetr
                }
            })
            
        except Exception as e:
            print(f"[API ERROR] PUT /subtab-insp-petr-item/{item_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    elif request.method == 'DELETE':
        try:
            item.delete()
            
            print(f"[API] DELETE /subtab-insp-petr-item/{item_id}/ - Item removido")
            
            return JsonResponse({
                'success': True,
                'message': 'Item removido com sucesso'
            })
            
        except Exception as e:
            print(f"[API ERROR] DELETE /subtab-insp-petr-item/{item_id}/ - {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)




















































































































