from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import FiscaisCad,BarcosCad,ModalBarco,PassServ

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
@csrf_exempt
@require_http_methods(["GET", "DELETE"])
def passagem_detail(request, ps_id):
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
        
        if not fiscal_nome:
            return JsonResponse({
                'success': False,
                'error': 'Nome do fiscal não fornecido'
            }, status=400)
        
        passagens = PassServ.objects.filter(
            fiscalDes=fiscal_nome
        ).order_by('-dataEmissaoPS').values(
            'id', 'numPS', 'anoPS', 'BarcoPS', 
            'dataInicio', 'dataFim', 'dataEmissaoPS', 'statusPS'
        )
        
        return JsonResponse({
            'success': True,
            'data': list(passagens)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)






























































































































