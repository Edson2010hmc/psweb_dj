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
    configurarAccordion();
    // Fecha todos os accordions ao iniciar
  document.querySelectorAll('.accordion-content').forEach(c => {
    c.classList.remove('active');
  });
  document.querySelectorAll('.accordion-header .toggle').forEach(t => {
    t.textContent = '▼';
  });
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
        if (targetTab === 'cadastros') {
          reiniciarCadastros();
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

function configurarAccordion() {
  const headers = document.querySelectorAll('.accordion-header');
  
  headers.forEach(header => {
    header.addEventListener('click', function() {
      const target = this.getAttribute('data-target');
      const content = document.getElementById(`acc-${target}`);
      const toggle = this.querySelector('.toggle');
      
      // Se já está aberto, fecha
      if (content.classList.contains('active')) {
        content.classList.remove('active');
        toggle.textContent = '▼';
        return;
      }
      
      // Fecha todos os conteúdos
      document.querySelectorAll('.accordion-content').forEach(c => {
        c.classList.remove('active');
      });
      
      // Reset todos os toggles
      document.querySelectorAll('.accordion-header .toggle').forEach(t => {
        t.textContent = '▼';
      });
      
      // Abre o clicado
      content.classList.add('active');
      toggle.textContent = '▲';
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

// ===== REINICIAR FORMULÁRIOS DE CADASTROS =====
  function reiniciarCadastros() {
    // Reinicia formulário de Fiscais
    if (typeof FiscaisModule !== 'undefined' && FiscaisModule.reiniciar) {
      FiscaisModule.reiniciar();
    }

    // Reinicia formulário de Embarcações
    if (typeof EmbarcacoesModule !== 'undefined' && EmbarcacoesModule.reiniciar) {
      EmbarcacoesModule.reiniciar();
    }
     document.querySelectorAll('.accordion-content').forEach(c => {
    c.classList.remove('active');
  });
  document.querySelectorAll('.accordion-header .toggle').forEach(t => {
    t.textContent = '▼';
  });
  }





  // ===== EXECUTAR QUANDO DOM CARREGAR =====
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();