// ===== MODULO PASSAGENS DE SERVIÇO ======================================================

const PassagensModule = (() => {
 let psAtualId = null;

  // ===== CALCULAR PERÍODO DA PS ==========================================================
  function calcularPeriodoPS(dataPrimeiraEntrada) {
    const primeiraEntrada = new Date(dataPrimeiraEntrada);
    const hoje = new Date();
    hoje.setHours(0, 0, 0, 0);
    
    // Calcula quantos dias passaram desde primeira entrada
    const diasPassados = Math.floor((hoje - primeiraEntrada) / (1000 * 60 * 60 * 24));
    
    // Calcula qual ciclo atual (vigente)
    const cicloAtual = Math.floor(diasPassados / 14);
    
    // Calcula início do ciclo vigente
    const inicioVigente = new Date(primeiraEntrada);
    inicioVigente.setDate(inicioVigente.getDate() + (cicloAtual * 14));
    
    // Calcula fim do ciclo vigente (13 dias depois do início)
    const fimVigente = new Date(inicioVigente);
    fimVigente.setDate(fimVigente.getDate() + 13);
    
    // Data de emissão (dia seguinte ao fim)
    const emissao = new Date(fimVigente);
    emissao.setDate(emissao.getDate() + 1);
    
    // Contar emissões que caíram no ano da PS atual
    const ano = emissao.getFullYear();
    let psNoAno = 0;
    
    // Loop pelos ciclos anteriores para contar emissões no mesmo ano
    for (let ciclo = 0; ciclo < cicloAtual; ciclo++) {
      const inicioEsseCiclo = new Date(primeiraEntrada);
      inicioEsseCiclo.setDate(inicioEsseCiclo.getDate() + (ciclo * 14));
      
      const fimEsseCiclo = new Date(inicioEsseCiclo);
      fimEsseCiclo.setDate(fimEsseCiclo.getDate() + 13);
      
      const emissaoEsseCiclo = new Date(fimEsseCiclo);
      emissaoEsseCiclo.setDate(emissaoEsseCiclo.getDate() + 1);
      
      if (emissaoEsseCiclo.getFullYear() === ano) {
        psNoAno++;
      }
    }
    
    // Numeração da PS atual
    const numero = psNoAno + 1;
    
    return {
      inicio: inicioVigente.toISOString().slice(0, 10),
      fim: fimVigente.toISOString().slice(0, 10),
      emissao: emissao.toISOString().slice(0, 10),
      numero,
      ano,
      numeroFormatado: `${numero.toString().padStart(2, '0')}/${ano}`
    };
  }

  // ===== CRIAR NOVA PS ===================================================================
  async function criarNovaPS(barcoId, barcoData) {
    const usuario = AuthModule.getUsuarioLogado();
    if (!usuario) {
      alert('Usuário não identificado');
      return;
    }

    // Verificar rascunho para embarcação
    try {
      const checkResponse = await fetch('/api/verificar-rascunho-embarcacao/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          barcoId,
          fiscalNome: `${usuario.chave} - ${usuario.nome}`
        })
      });

      const checkResult = await checkResponse.json();

      if (!checkResult.success) {
        throw new Error(checkResult.error);
      }

      if (checkResult.existeRascunho) {
        alert(`Existe uma Passagem de Serviço em modo Rascunho para o barco ${checkResult.barcoNome} gerada pelo usuário ${checkResult.fiscalNome}`);
        document.getElementById('modalNovaPS').classList.add('hidden');
        document.querySelectorAll('.tablink').forEach(btn => btn.disabled = false);
        return;
      }

      //  Calcular período
      const periodo = calcularPeriodoPS(barcoData.dataPrimPorto);

      // Criar PS no backend
      const createResponse = await fetch('/api/passagens/criar/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          barcoId: barcoId,
          fiscalDesNome: `${usuario.chave} - ${usuario.nome}`,
          fiscalEmbId: null, // Será preenchido depois
          numero: periodo.numero,
          ano: periodo.ano,
          dataInicio: periodo.inicio,
          dataFim: periodo.fim,
          dataEmissao: periodo.emissao
        })
      });

      const createResult = await createResponse.json();

      if (!createResult.success) {
        throw new Error(createResult.error);
      }
      // Limpar formulários dos módulos antes de criar nova
      if (typeof TrocaTurmaModule !== 'undefined' && TrocaTurmaModule.limpar) {
        TrocaTurmaModule.limpar();
      }

      if (typeof ManutPrevModule !== 'undefined' && ManutPrevModule.limpar) {
        ManutPrevModule.limpar();
      }

      if (typeof InspNormModule !== 'undefined' && InspNormModule.limpar) {
        InspNormModule.limpar();
      }

      // Fechar modal e  guardar ID da PS atual
      psAtualId = createResult.data.id;
      document.getElementById('modalNovaPS').classList.add('hidden');
        document.querySelectorAll('.tablink').forEach(btn => btn.disabled = false);
      document.getElementById('selEmbNova').value = '';

      //  Preencher formulário da PS
      preencherFormularioPS(createResult.data, barcoData, usuario);

      // Criar card na lista
      criarCardPS(createResult.data);

      
      //  Ir para tela da PS
      document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
      document.getElementById('tab-passagem').classList.add('active');

    } catch (error) {
      alert('Erro ao criar PS: ' + error.message);
    }
  }

// ===== PREENCHER FORMULÁRIO DA PS =======================================================
function preencherFormularioPS(psData, barcoData, usuario) {
  // Mostrar formulário, ocultar placeholder
  document.getElementById('psPlaceholder').style.display = 'none';
  document.getElementById('psForm').classList.remove('hidden');

  // Número PS
  document.getElementById('fNumero').value = `${psData.numPS.toString().padStart(2, '0')}/${psData.anoPS}`;
  document.getElementById('fNumero').disabled = true;

  // Datas (habilitadas)
  document.getElementById('fData').value = psData.dataEmissaoPS;
  document.getElementById('fInicioPS').value = psData.dataInicio;
  document.getElementById('fFimPS').value = psData.dataFim;

  // Embarcação (desabilitada)
  document.getElementById('fEmb').value = psData.BarcoPS;
  document.getElementById('fEmb').disabled = true;

  // Status (desabilitado)
  document.getElementById('fStatus').value = psData.statusPS;
  document.getElementById('fStatus').disabled = true;

  // Fiscal Desembarcando (desabilitado)
  document.getElementById('fDesCNome').value = psData.fiscalDes;
  document.getElementById('fDesCNome').disabled = true;

  // Carregar combo de fiscais embarcando
  carregarFiscaisEmbarcando(psData.fiscalEmb);
  // Configurar botão excluir (apenas uma vez)
  if (!window.btnExcluirConfigurado) {
    configurarBotaoExcluir();
    window.btnExcluirConfigurado = true;
}
  // Configurar botão salvar (apenas uma vez)
  if (!window.btnSalvarConfigurado) {
    configurarBotaoSalvar();
    window.btnSalvarConfigurado = true;
}

// Carregar modulo Troca de Turma
if (typeof TrocaTurmaModule !== 'undefined' && TrocaTurmaModule.carregarDados) {
  TrocaTurmaModule.carregarDados(psData.id);
}

// Carregar Modulo Manutenção Preventiva
if (typeof ManutPrevModule !== 'undefined' && ManutPrevModule.carregarDados) {
  ManutPrevModule.carregarDados(psData.id);
}

// Carregar modulo Inspeção Normativa
if (typeof InspNormModule !== 'undefined' && InspNormModule.carregarDados) {
  InspNormModule.carregarDados(psData.id);
}


}

// ===== CARREGAR USUARIOS COM PERFIL FISCAL =====
async function carregarFiscaisEmbarcando(fiscalEmbSelecionado = '') {
  try {
    const response = await fetch('/api/fiscais/perfil-fiscal/');
    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error);
    }

    const select = document.getElementById('fEmbC');
    select.innerHTML = '<option value="">— selecione —</option>';

    result.data.forEach(fiscal => {
      const option = document.createElement('option');
      option.value = fiscal.id;
      const fiscalTexto = `${fiscal.chave} - ${fiscal.nome}`;
      option.textContent = fiscalTexto;
      
      // Pré-selecionar se corresponder
      if (fiscalEmbSelecionado && fiscalTexto === fiscalEmbSelecionado) {
        option.selected = true;
      }
      
      select.appendChild(option);
    });

  } catch (error) {
    alert('Erro ao carregar Fiscal: ' + error.message);
  }
}

  // ===== CRIAR CARD NA LISTA ==========================================================
  function criarCardPS(psData) {
    const lista = document.getElementById('listaPS');
    const li = document.createElement('li');
    li.dataset.psId = psData.id;

    li.innerHTML = `
      <div class="ps-card-content">
        <div class="ps-linha1">N°${psData.numPS.toString().padStart(2, '0')}/${psData.anoPS} => ${psData.BarcoPS}</div>
        <div class="ps-linha2">PERÍODO: ${formatarData(psData.dataInicio)} a ${formatarData(psData.dataFim)}</div>
        <div class="ps-linha3 status-${psData.statusPS}">${psData.statusPS}</div>
        <div class="ps-linha4">TROCA DE TURMA ${formatarData(psData.dataEmissaoPS)}</div>
      </div>
    `;

    lista.appendChild(li);
    li.addEventListener('click', function() {
      abrirPS(psData.id);
});
  }

  // ===== FORMATAR DATA =====
  function formatarData(dataISO) {
    const [ano, mes, dia] = dataISO.split('-');
    return `${dia}/${mes}/${ano}`;
  }

  // ===== ABRIR PS EXISTENTE ============================================================
async function abrirPS(psId) {
  try {
    const response = await fetch(`/api/passagens/${psId}/`);
    const result = await response.json();
    psAtualId = psId;

    if (!result.success) {
      psAtualId = psId;
      throw new Error(result.error);
    }

    // Preencher formulário com dados da PS
    preencherFormularioPS(result.data, null, null);

    // Carregar dados Modulo Troca de Turma
    if (typeof TrocaTurmaModule !== 'undefined' && TrocaTurmaModule.carregarDados) {
      TrocaTurmaModule.carregarDados(psId);
    }

    // Carregar Manutenção Preventiva
    if (typeof ManutPrevModule !== 'undefined' && ManutPrevModule.carregarDados) {
      ManutPrevModule.carregarDados(psId);
    }

    // Carregar dados Modulo Inspeção Normativa
    if (typeof InspNormModule !== 'undefined' && InspNormModule.carregarDados) {
      InspNormModule.carregarDados(psId);
    }

    // Ir para tela da PS
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.getElementById('tab-passagem').classList.add('active');

  } catch (error) {
    alert('Erro ao abrir PS: ' + error.message);
  }
}

// ===== EXCLUIR RASCUNHO =================================================================
async function excluirRascunho(psId) {
  if (!confirm('Confirma a exclusão do rascunho?')) {
    return;
  }

  try {
    const response = await fetch(`/api/passagens/${psId}/`, {
      method: 'DELETE'
    });

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error);
    }

    alert('Rascunho excluído com sucesso!');

    // Remover card da lista
    const card = document.querySelector(`li[data-ps-id="${psId}"]`);
    if (card) {
      card.remove();
    }

    // Limpar formulários dos módulos
    if (typeof TrocaTurmaModule !== 'undefined' && TrocaTurmaModule.limpar) {
      TrocaTurmaModule.limpar();
    }

    if (typeof ManutPrevModule !== 'undefined' && ManutPrevModule.limpar) {
      ManutPrevModule.limpar();
    }

    if (typeof InspNormModule !== 'undefined' && InspNormModule.limpar) {
      InspNormModule.limpar();
    }

    psAtualId = null;

    // Voltar para tela inicial
    document.querySelector('[data-tab="consultas"]').click();

  } catch (error) {
    alert('Erro ao excluir rascunho: ' + error.message);
  }
}

// ===== CONFIGURAR BOTÃO EXCLUIR =========================================================
function configurarBotaoExcluir() {
  const btnExcluir = document.getElementById('btnExcluirRasc');
  
  btnExcluir.addEventListener('click', function() {
    if (psAtualId) {
      excluirRascunho(psAtualId);
    } else {
      alert('Nenhuma PS carregada');
    }
  });
}

// ===== SALVAR RASCUNHO ==================================================================
async function salvarRascunho(psId, silencioso = false) {
  try {
    const dados = {
      dataEmissaoPS: document.getElementById('fData').value,
      dataInicio: document.getElementById('fInicioPS').value,
      dataFim: document.getElementById('fFimPS').value,
      fiscalEmb: document.getElementById('fEmbC').value
    };
    // Salvar dados Modulo Troca de Turma
    if (typeof TrocaTurmaModule !== 'undefined' && TrocaTurmaModule.salvar) {
      await TrocaTurmaModule.salvar();
    }

    // Salvar Manutenção Preventiva
    if (typeof ManutPrevModule !== 'undefined' && ManutPrevModule.salvar) {
      await ManutPrevModule.salvar();
    }

    // Salvar dados Modulo Inspeção Normativa
    if (typeof InspNormModule !== 'undefined' && InspNormModule.salvar) {
      await InspNormModule.salvar();
    }

    const response = await fetch(`/api/passagens/${psId}/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados)
    });

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error);
    }

    if (!silencioso) {
      alert('Rascunho salvo com sucesso!');
    }

  } catch (error) {
    if (!silencioso) {
      alert('Erro ao salvar rascunho: ' + error.message);
    }
  }
}

// ===== SALVAMENTO AO TROCAR DE ABA ============================================
async function salvarAntesDeSair() {
  if (!psAtualId) return;
  await salvarRascunho(psAtualId, true);
}

// ===== CONFIGURAR BOTÃO SALVAR ==========================================================
function configurarBotaoSalvar() {
  const btnSalvar = document.getElementById('btnSalvar');
  
  btnSalvar.addEventListener('click', function() {
    if (psAtualId) {
      salvarRascunho(psAtualId);
    } else {
      alert('Nenhuma PS carregada');
    }
  });
}

// ===== CARREGAR PASSAGENS DO USUÁRIO ====================================================
async function carregarPassagensUsuario() {
  const usuario = AuthModule.getUsuarioLogado();
  if (!usuario) return;

  try {
    const fiscalNome = `${usuario.chave} - ${usuario.nome}`;
    const response = await fetch(`/api/passagens/usuario/?fiscalNome=${encodeURIComponent(fiscalNome)}`);
    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error);
    }

    const lista = document.getElementById('listaPS');
    lista.innerHTML = '';

    result.data.forEach(ps => {
      criarCardPS(ps);
    });

  } catch (error) {
    console.error('Erro ao carregar passagens:', error);
  }
}

  // ===== EXPORTAR FUNÇÕES ================================================================
  return {
    criarNovaPS,
    carregarPassagensUsuario,
    salvarRascunho,
    salvarAntesDeSair
  };

})();