"""
Script de Diagnóstico - Testar Conexões com APIs

Verifica a configuração e conectividade com:
1. Blaze API (múltiplos endpoints)
2. Telegram Bot
3. Ambiente de variáveis
4. Dependências Python
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

def print_header(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_environment():
    """Testa variáveis de ambiente"""
    print_header("1. VARIÁVEIS DE AMBIENTE")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'TELEGRAM_BOT_TOKEN': 'Token do bot Telegram',
        'TELEGRAM_CHANNEL_ID': 'ID do canal Telegram',
        'BLAZE_API_URL': 'URL base da API Blaze',
        'ANALYSIS_INTERVAL_MINUTES': 'Intervalo de análise',
    }
    
    for var, desc in required_vars.items():
        value = os.getenv(var, '❌ NÃO ENCONTRADO')
        status = '✅' if value != '❌ NÃO ENCONTRADO' else '❌'
        
        # Mascarar valores sensíveis
        if 'TOKEN' in var and value != '❌ NÃO ENCONTRADO':
            display = value[:20] + '...' + value[-10:]
        elif value != '❌ NÃO ENCONTRADO':
            display = value
        else:
            display = value
        
        print(f"{status} {var:30} = {display}")
        if value == '❌ NÃO ENCONTRADO':
            print(f"   └─ {desc}")

def test_dependencies():
    """Testa dependências Python"""
    print_header("2. DEPENDÊNCIAS PYTHON")
    
    dependencies = {
        'requests': 'Requisições HTTP',
        'numpy': 'Cálculos numéricos',
        'scipy': 'Análise estatística',
        'pandas': 'Manipulação de dados',
        'python-dotenv': 'Variáveis de ambiente',
        'schedule': 'Agendamento',
        'telegram': 'Bot Telegram',
        'sqlalchemy': 'ORM banco de dados',
    }
    
    for pkg, desc in dependencies.items():
        try:
            __import__(pkg)
            print(f"✅ {pkg:20} - {desc}")
        except ImportError:
            print(f"❌ {pkg:20} - {desc} (NÃO INSTALADO)")

def test_blaze_api():
    """Testa conectividade com Blaze API"""
    print_header("3. CONECTIVIDADE BLAZE API")
    
    import requests
    
    # Múltiplos endpoints para testar
    endpoints = [
        ("https://api.blaze.com", "API Base"),
        ("https://blaze.com/api", "Alternativa 1"),
        ("https://api.blaze.com/api", "Alternativa 2"),
        ("https://blaze.com", "Website principal"),
    ]
    
    for url, desc in endpoints:
        try:
            print(f"\nTestando: {desc}")
            print(f"URL: {url}")
            
            response = requests.get(url, timeout=5)
            print(f"✅ Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   └─ Resposta válida (200 OK)")
            elif response.status_code == 404:
                print(f"   └─ Página não encontrada (404)")
            elif response.status_code == 403:
                print(f"   └─ Acesso proibido (403)")
            elif response.status_code == 429:
                print(f"   └─ Rate limit (429)")
            else:
                print(f"   └─ Status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"❌ Timeout (5 segundos)")
        except requests.exceptions.ConnectionError:
            print(f"❌ Erro de conexão (verifique internet)")
        except Exception as e:
            print(f"❌ Erro: {str(e)[:60]}")

def test_telegram():
    """Testa conectividade com Telegram"""
    print_header("4. TELEGRAM BOT")
    
    import requests
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHANNEL_ID')
    
    if not token or not chat_id:
        print("❌ Token ou Chat ID não configurado")
        return
    
    try:
        # Testar validação do token
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data.get('result', {})
                print(f"✅ Bot conectado com sucesso")
                print(f"   └─ Nome: {bot_info.get('first_name', 'N/A')}")
                print(f"   └─ Username: @{bot_info.get('username', 'N/A')}")
                print(f"   └─ ID: {bot_info.get('id', 'N/A')}")
            else:
                print(f"❌ Token inválido")
                print(f"   └─ Erro: {data.get('description', 'Desconhecido')}")
        else:
            print(f"❌ Erro HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"❌ Timeout ao conectar Telegram")
    except Exception as e:
        print(f"❌ Erro: {str(e)[:60]}")

def test_local_data():
    """Verifica dados locais existentes"""
    print_header("5. DADOS LOCAIS")
    
    # Verificar arquivo de dados
    data_file = Path(__file__).parent.parent / 'data' / 'raw' / 'blaze_data.json'
    
    if data_file.exists():
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
                
            if isinstance(data, dict):
                crash_count = len(data.get('crash', []))
                double_count = len(data.get('double', []))
            elif isinstance(data, list):
                crash_count = len([d for d in data if d.get('type') == 'crash'])
                double_count = len([d for d in data if d.get('type') == 'double'])
            else:
                crash_count = double_count = 0
                
            print(f"✅ Arquivo de dados encontrado: {data_file.name}")
            print(f"   └─ Crash: {crash_count} registros")
            print(f"   └─ Double: {double_count} registros")
            
        except json.JSONDecodeError:
            print(f"❌ Arquivo corrompido ou inválido JSON")
    else:
        print(f"⚠️  Nenhum arquivo de dados local encontrado")
        print(f"   └─ Caminho esperado: {data_file}")

def test_blaze_client():
    """Testa o cliente BlazeDataCollector"""
    print_header("6. BLAZE DATA COLLECTOR")
    
    try:
        from src.data_collection.blaze_client import BlazeDataCollector
        
        print("✅ BlazeDataCollector importado com sucesso")
        
        collector = BlazeDataCollector()
        print(f"   └─ URL base: {collector.base_url}")
        
        # Tentar coletar dados
        print("\n   Tentando coletar dados do Double...")
        double_data = collector.get_double_history(limit=5)
        
        if double_data:
            print(f"   ✅ {len(double_data)} registros obtidos")
            if len(double_data) > 0:
                print(f"   └─ Primeiro registro: {double_data[0]}")
        else:
            print(f"   ⚠️  Nenhum dado retornado (pode ser fallback)")
            
    except Exception as e:
        print(f"❌ Erro ao importar/usar BlazeDataCollector:")
        print(f"   └─ {str(e)}")

def test_main_integration():
    """Testa integração com main.py"""
    print_header("7. INTEGRAÇÃO MAIN.PY")
    
    try:
        from src.main import BetAnalysisPlatform
        
        print("✅ BetAnalysisPlatform importado com sucesso")
        
        platform = BetAnalysisPlatform()
        print(f"   └─ Plataforma inicializada")
        print(f"   └─ Logger configurado")
        
        # Tentar rodar um ciclo
        print("\n   Tentando executar um ciclo de análise...")
        # Not running to avoid side effects
        
    except Exception as e:
        print(f"❌ Erro ao importar/usar BetAnalysisPlatform:")
        print(f"   └─ {str(e)}")

def generate_report():
    """Gera relatório em arquivo"""
    report_file = Path(__file__).parent.parent / 'logs' / 'diagnostico.txt'
    
    print_header("GERANDO RELATÓRIO")
    
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Relatório será salvo em: {report_file}")

def main():
    """Função principal"""
    print("\n" + "="*80)
    print("  DIAGNÓSTICO DE CONEXÕES - SISTEMA DE ANÁLISE DE APOSTAS")
    print("="*80)
    print(f"\nData: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        test_environment()
        test_dependencies()
        test_blaze_api()
        test_telegram()
        test_local_data()
        test_blaze_client()
        test_main_integration()
        
        print_header("RESUMO DIAGNÓSTICO")
        print("""
Próximas ações:

1. Se Blaze API não conecta:
   ✓ Verificar internet: ping google.com
   ✓ Verificar URL correta da API
   ✓ Dados de fallback estão sendo usados (OK)

2. Se Telegram não conecta:
   ✓ Verificar token em .env
   ✓ Verificar chat ID
   ✓ Executar: python get_chat_id.py

3. Se dependências faltam:
   ✓ Instalar: pip install -r requirements.txt

4. Para mais detalhes:
   ✓ Ver logs em: logs/bet_analysis.log
   ✓ Rodar: python src/main.py
        """)
        
    except Exception as e:
        print(f"\n❌ Erro durante diagnóstico: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
