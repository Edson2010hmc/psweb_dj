#!/usr/bin/env python
"""
Django + PyWebView Launcher
Executa a aplicação Django em uma janela desktop
"""

import os
import sys
import time
import threading
import webbrowser
from pathlib import Path

try:
    import webview
except ImportError:
    print("PyWebView não encontrado. Instale com: pip install pywebview")
    sys.exit(1)

try:
    import django
    from django.core.management import execute_from_command_line
    from django.core.wsgi import get_wsgi_application
except ImportError:
    print("Django não encontrado. Instale com: pip install django")
    sys.exit(1)


class DjangoApp:
    def __init__(self):
        self.django_port = 8000
        self.django_host = '127.0.0.1'
        self.django_url = f'http://{self.django_host}:{self.django_port}/admin/'
        self.server_thread = None
        
    def setup_django(self):
        """Configura o ambiente Django"""
        # Definir o settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        
        # Verificar se manage.py existe
        if not Path('manage.py').exists():
            print("ERRO: manage.py não encontrado!")
            print("Execute este script no diretório raiz do projeto Django")
            return False
            
        # Inicializar Django
        try:
            django.setup()
            print("✅ Django configurado com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao configurar Django: {e}")
            return False
    
    def run_django_server(self):
        """Executa o servidor Django em thread separada"""
        try:
            print(f"🚀 Iniciando servidor Django em {self.django_url}")
            
            # Comandos Django equivalentes a: python manage.py runserver
            sys.argv = ['manage.py', 'runserver', f'{self.django_host}:{self.django_port}', '--noreload']
            execute_from_command_line(sys.argv)
            
        except Exception as e:
            print(f"❌ Erro no servidor Django: {e}")
    
    def wait_for_server(self, timeout=30):
        """Aguarda o servidor Django estar pronto"""
        import urllib.request
        import urllib.error
        
        print("⏳ Aguardando servidor Django inicializar...")
        
        for i in range(timeout):
            try:
                urllib.request.urlopen(self.django_url, timeout=1)
                print("✅ Servidor Django está pronto!")
                return True
            except urllib.error.URLError:
                time.sleep(1)
                print(f"   Tentativa {i+1}/{timeout}...")
                
        print("❌ Timeout: Servidor Django não respondeu")
        return False
    
    def create_desktop_app(self):
        """Cria a aplicação desktop com PyWebView"""
        
        # Configurações da janela
        window_config = {
            'title': 'Sistema de Vendas - Django',
            'url': self.django_url,
            'width': 1200,
            'height': 800,
            'min_size': (800, 600),
            'resizable': True,
            'fullscreen': False,
            'minimized': False,
            'on_top': False,
            
        }
        
        print("🖥️  Criando janela desktop...")
        
        # Criar janela PyWebView
        webview.create_window(**window_config)
        
        # Configurações adicionais do PyWebView
        webview_config = {
            'debug': True,  # Ativar DevTools (F12)
            'private_mode': False,
            'storage_path': './webview_storage',  # Cache/cookies
        }
        
        print("🎯 Iniciando aplicação desktop...")
        webview.start(**webview_config)
    
    def run(self):
        """Método principal - executa toda a aplicação"""
        print("=" * 50)
        print("🚀 DJANGO + PYWEBVIEW LAUNCHER")
        print("=" * 50)
        
        # 1. Configurar Django
        if not self.setup_django():
            return
        
        # 2. Iniciar servidor Django em thread separada
        self.server_thread = threading.Thread(
            target=self.run_django_server,
            daemon=True  # Thread morre quando main thread morrer
        )
        self.server_thread.start()
        
        # 3. Aguardar servidor estar pronto
        if not self.wait_for_server():
            return
            
        # 4. Abrir aplicação desktop
        try:
            self.create_desktop_app()
        except KeyboardInterrupt:
            print("\n👋 Aplicação finalizada pelo usuário")
        except Exception as e:
            print(f"❌ Erro na aplicação desktop: {e}")
        finally:
            print("🔚 Encerrando aplicação...")


def main():
    """Função principal"""
    app = DjangoApp()
    app.run()


if __name__ == '__main__':
    main()