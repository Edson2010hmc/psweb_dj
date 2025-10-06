// ===== APLICAÇÃO PRINCIPAL - GERENCIADOR DE NAVEGAÇÃO =====

(function() {
  'use strict';

  // ===== INICIALIZAÇÃO =====
  async function init() {
    // Validar usuário ANTES de mostrar interface
    if (typeof AuthModule !== 'undefined' && AuthModule.validarUsuario) {
      const autorizado = await AuthModule.validarUsuario();
      if (!autorizado) {
        return; // Para aqui se não autorizado
      }
    }
    configurarNavegacaoTabs();
    configurarNavegacaoSubtabs();
    inicializarModulos();
  }

  // ===== CONFIGURAR NAVEGAÇÃO ENTRE TABS PRINCIPAIS =====
  function configurarNavegacaoTabs() {
    const tablinks = document.querySelectorAll('.tablink');
    
    tablinks.forEach(link => {
      link.addEventListener('click', function() {
        const targetTab = this.getAttribute('data-tab');
        
        // Remove active de todos os links
        tablinks.forEach(l => l.classList.remove('active'));
        
        // Remove active de todas as tabs
        document.querySelectorAll('.tab').forEach(tab => {
          tab.classList.remove('active');
        });
        
        // Adiciona active no link clicado
        this.classList.add('active');
        
        // Adiciona active na tab correspondente
        const targetSection = document.getElementById(`tab-${targetTab}`);
        if (targetSection) {
          targetSection.classList.add('active');
        }
      });
    });
  }

  // ===== CONFIGURAR NAVEGAÇÃO ENTRE SUBTABS =====
  function configurarNavegacaoSubtabs() {
    const sublinks = document.querySelectorAll('.sublink');
    
    sublinks.forEach(link => {
      link.addEventListener('click', function() {
        const targetSub = this.getAttribute('data-sub');
        
        // Remove active de todos os sublinks
        sublinks.forEach(l => l.classList.remove('active'));
        
        // Remove active de todas as subtabs
        document.querySelectorAll('.subtab').forEach(subtab => {
          subtab.classList.remove('active');
        });
        
        // Adiciona active no sublink clicado
        this.classList.add('active');
        
        // Adiciona active na subtab correspondente
        const targetSubsection = document.getElementById(`sub-${targetSub}`);
        if (targetSubsection) {
          targetSubsection.classList.add('active');
        }
      });
    });
  }

  // ===== INICIALIZAR MÓDULOS EXISTENTES =====
  function inicializarModulos() {
    // Inicializar módulo de Fiscais
    if (typeof FiscaisModule !== 'undefined' && FiscaisModule.init) {
      FiscaisModule.init();
    }

    // Inicializar módulo de Embarcações
    if (typeof EmbarcacoesModule !== 'undefined' && EmbarcacoesModule.init) {
      EmbarcacoesModule.init();
    }
  }

  // ===== EXECUTAR QUANDO DOM CARREGAR =====
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();