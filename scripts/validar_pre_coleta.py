"""
Script de Validação Pré-Coleta

Verifica se todos os componentes estão prontos para a coleta de 48 horas.
Detecta problemas comuns e oferece soluções.
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ValidadorPre:
    """Validador de pré-coleta"""
    
    def __init__(self, base_path=None):
        self.base_path = base_path or Path(__file__).parent.parent
        self.erros = []
        self.avisos = []
        self.sucessos = []
    
    def validar_tudo(self):
        """Executa todas as validações"""
        print("\n" + "="*100)
        print("VALIDADOR PRÉ-COLETA - Verificando ambiente")
        print("="*100 + "\n")
        
        self.validar_python()
        self.validar_diretorio()
        self.validar_arquivos_principais()
        self.validar_dependencias()
        self.validar_apis()
        self.validar_ambiente()
        self.validar_espaco_disco()
        
        self._exibir_relatorio()
    
    def validar_python(self):
        """Valida versão do Python"""
        version = sys.version_info
        if version.major == 3 and version.minor >= 9:
            self.sucessos.append(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        else:
            self.erros.append(f"❌ Python {version.major}.{version.minor} (requer 3.9+)")
    
    def validar_diretorio(self):
        """Valida estrutura de diretórios"""
        dirs_necessarios = [
            'src', 'src/analysis', 'src/config', 'src/data_collection',
            'scripts', 'data', 'logs', 'tests'
        ]
        
        for dir_name in dirs_necessarios:
            dir_path = self.base_path / dir_name
            if dir_path.exists():
                self.sucessos.append(f"✅ Diretório '{dir_name}/' existe")
            else:
                self.avisos.append(f"⚠️  Diretório '{dir_name}/' não encontrado (criando...)")
                dir_path.mkdir(parents=True, exist_ok=True)
    
    def validar_arquivos_principais(self):
        """Valida arquivos principais necessários"""
        arquivos_necessarios = {
            'src/main.py': 'Main orchestration',
            'src/analysis/monte_carlo_strategy.py': 'Monte Carlo strategy',
            'src/analysis/strategy_pipeline.py': '6-strategy pipeline',
            'scripts/coleta_continua_dados.py': 'Continuous collection',
            'scripts/dashboard_monitoramento.py': 'Real-time dashboard',
            'src/config/settings.py': 'Configuration settings',
            'src/telegram_bot/bot_manager.py': 'Telegram bot',
        }
        
        for arquivo, desc in arquivos_necessarios.items():
            caminho = self.base_path / arquivo
            if caminho.exists():
                self.sucessos.append(f"✅ {arquivo} ({desc})")
            else:
                self.erros.append(f"❌ {arquivo} não encontrado ({desc})")
    
    def validar_dependencias(self):
        """Valida dependências Python"""
        dependencias = {
            'numpy': 'Cálculos matemáticos',
            'scipy': 'Análise estatística',
            'requests': 'Requisições HTTP',
            'telegram': 'Bot do Telegram',
            'schedule': 'Agendamento de tarefas',
            'python-dotenv': 'Variáveis de ambiente',
        }
        
        for dep, desc in dependencias.items():
            try:
                __import__(dep)
                self.sucessos.append(f"✅ {dep} ({desc})")
            except ImportError:
                self.avisos.append(f"⚠️  {dep} não encontrado ({desc})")
    
    def validar_apis(self):
        """Valida configuração de APIs"""
        # Telegram
        env_file = self.base_path / '.env'
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    env_content = f.read()
                    if 'TELEGRAM_BOT_TOKEN' in env_content and 'TELEGRAM_CHAT_ID' in env_content:
                        self.sucessos.append("✅ Telegram configurado (.env encontrado)")
                    else:
                        self.avisos.append("⚠️  .env incompleto (faltam TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID)")
            except:
                self.avisos.append("⚠️  Erro ao ler .env")
        else:
            self.avisos.append("⚠️  .env não encontrado (Telegram pode não funcionar)")
        
        # Blaze API
        try:
            import requests
            response = requests.get('https://api.blaze.com/api', timeout=5)
            if response.status_code in [200, 429, 403]:  # 429 = rate limit, 403 = forbidden
                self.sucessos.append("✅ Blaze API acessível")
            else:
                self.avisos.append(f"⚠️  Blaze API retornou status {response.status_code}")
        except Exception as e:
            self.avisos.append(f"⚠️  Erro ao conectar Blaze API: {str(e)[:50]}")
    
    def validar_ambiente(self):
        """Valida variáveis de ambiente"""
        venv_python = self.base_path / 'venv' / 'Scripts' / 'python.exe'
        if sys.prefix.endswith('venv'):
            self.sucessos.append("✅ Virtual environment ativado")
        elif venv_python.exists():
            self.avisos.append("⚠️  Virtual environment existe mas não está ativado (use: .\\venv\\Scripts\\Activate.ps1)")
        else:
            self.erros.append("❌ Virtual environment não encontrado")
    
    def validar_espaco_disco(self):
        """Valida espaço em disco disponível"""
        import shutil
        usage = shutil.disk_usage(str(self.base_path))
        free_gb = usage.free / (1024**3)
        
        # Estimativa: 48 horas com 1000 cores = ~100-500 KB
        if free_gb > 1:
            self.sucessos.append(f"✅ Espaço em disco: {free_gb:.1f} GB disponível")
        else:
            self.erros.append(f"❌ Espaço insuficiente: {free_gb:.1f} GB (requer >1 GB)")
    
    def _exibir_relatorio(self):
        """Exibe relatório final"""
        print("\n" + "="*100)
        print("RELATÓRIO DE VALIDAÇÃO")
        print("="*100 + "\n")
        
        # Sucessos
        if self.sucessos:
            print("✅ VALIDAÇÕES APROVADAS ({})".format(len(self.sucessos)))
            print("-" * 100)
            for sucesso in self.sucessos[:10]:  # Mostrar apenas 10 primeiros
                print(f"  {sucesso}")
            if len(self.sucessos) > 10:
                print(f"  ... e mais {len(self.sucessos) - 10} validações")
            print()
        
        # Avisos
        if self.avisos:
            print("⚠️  AVISOS ({})".format(len(self.avisos)))
            print("-" * 100)
            for aviso in self.avisos:
                print(f"  {aviso}")
            print()
        
        # Erros
        if self.erros:
            print("❌ ERROS ({})".format(len(self.erros)))
            print("-" * 100)
            for erro in self.erros:
                print(f"  {erro}")
            print()
        
        # Resumo
        print("="*100)
        print("RESUMO")
        print("="*100)
        
        if self.erros:
            print("\n❌ COLETA NÃO RECOMENDADA - Erros encontrados:")
            for erro in self.erros:
                print(f"   - {erro}")
            print("\nResolva os erros acima antes de iniciar coleta.")
            return False
        
        if self.avisos:
            print(f"\n⚠️  {len(self.avisos)} aviso(s) encontrado(s), mas coleta pode prosseguir.")
            print("Recomendações:")
            for aviso in self.avisos:
                if "Virtual environment" in aviso:
                    print(f"   - {aviso}")
                    print("     Solução: .\\venv\\Scripts\\Activate.ps1")
                elif ".env" in aviso:
                    print(f"   - {aviso}")
                    print("     Solução: Criar arquivo .env com TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID")
                elif "Blaze" in aviso:
                    print(f"   - {aviso}")
                    print("     Solução: Verificar conexão com internet")
        else:
            print("\n✅ AMBIENTE PERFEITO - Tudo pronto para coleta!")
        
        print("\n" + "="*100)
        print("PRÓXIMOS PASSOS")
        print("="*100)
        print("""
1. Abra dois terminais PowerShell:

   Terminal 1 - Coleta de dados:
   $ python scripts/coleta_continua_dados.py --duration 48 --interval 30

   Terminal 2 - Monitoramento (inicie após ~30 segundos):
   $ python scripts/dashboard_monitoramento.py --interval 10

2. Deixe rodando por 48 horas

3. Após 48 horas, execute novo backtest:
   $ python scripts/run_backtest_optimized.py --win-rate 0.60 --margin 0.08 --compare

Esperado: ROI de 4-5% (vs 3.56% com dados aleatórios)
""")
        print("="*100 + "\n")
        
        return True


def main():
    """Função principal"""
    validador = ValidadorPre()
    resultado = validador.validar_tudo()
    
    # Retornar código de saída apropriado
    sys.exit(0 if resultado else 1)


if __name__ == "__main__":
    main()
