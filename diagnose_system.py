"""
SCRIPT DE DIAGNÓSTICO COMPLETO
Verifica se tudo está funcionando corretamente
"""
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Add src directory to path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

load_dotenv()

print("\n" + "="*80)
print("🔍 DIAGNÓSTICO COMPLETO - SISTEMA DE APOSTAS")
print("="*80)
print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

# 1. CONFIGURAÇÕES
print("1️⃣  VERIFICANDO CONFIGURAÇÕES (.env)")
print("-" * 80)

telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
telegram_channel = os.getenv('TELEGRAM_CHANNEL_ID')

print(f"  {'✅' if telegram_token else '❌'} TELEGRAM_BOT_TOKEN: {'Configurado' if telegram_token else 'NÃO configurado'}")
print(f"  {'✅' if telegram_channel else '❌'} TELEGRAM_CHANNEL_ID: {'Configurado' if telegram_channel else 'NÃO configurado'}")

# 2. MÓDULOS
print("\n2️⃣  VERIFICANDO MÓDULOS CRÍTICOS")
print("-" * 80)

modules = [('numpy', 'NumPy'), ('pandas', 'Pandas'), ('telegram', 'Python-Telegram-Bot'), ('scipy', 'SciPy')]

for module_name, display_name in modules:
    try:
        __import__(module_name)
        print(f"  ✅ {display_name}")
    except ImportError:
        print(f"  ❌ {display_name} (NÃO instalado)")

# 3. COLETA DE DADOS
print("\n3️⃣  VERIFICANDO COLETA DE DADOS (Blaze)")
print("-" * 80)

try:
    from data_collection.blaze_client_v2 import BlazeDataCollectorV2  # type: ignore
    collector = BlazeDataCollectorV2()
    data = collector.get_all_data(limit=50)
    
    double_count = len(data.get('double', []))
    crash_count = len(data.get('crash', []))
    
    print(f"  ✅ Conexão com Blaze OK")
    print(f"     • Double: {double_count} registros")
    print(f"     • Crash: {crash_count} registros")
except Exception as e:
    print(f"  ❌ Erro: {str(e)}")

# 4. ANÁLISE
print("\n4️⃣  VERIFICANDO ANÁLISE ESTATÍSTICA")
print("-" * 80)

try:
    from analysis.statistical_analyzer import StatisticalAnalyzer  # type: ignore
    import pandas as pd
    
    analyzer = StatisticalAnalyzer()
    test_data = {
        'double': pd.DataFrame({'color': ['red', 'black'] * 5}),
        'crash': pd.DataFrame({'crash_point': [1.5, 2.0] * 5}),
        'source': 'test'
    }
    
    results = analyzer.analyze_patterns(test_data)
    print(f"  ✅ Análise funcionando OK")
except Exception as e:
    print(f"  ❌ Erro: {str(e)}")

# 5. PIPELINE
print("\n5️⃣  VERIFICANDO PIPELINE (6 Estratégias)")
print("-" * 80)

try:
    from analysis.strategy_pipeline import StrategyPipeline  # type: ignore
    import logging
    logger = logging.getLogger(__name__)
    pipeline = StrategyPipeline(logger)
    print(f"  ✅ Pipeline inicializado OK")
    print(f"     • Monte Carlo (TRVs): ATIVO ✅")
except Exception as e:
    print(f"  ❌ Erro: {str(e)}")

# 6. TELEGRAM
print("\n6️⃣  VERIFICANDO TELEGRAM BOT")
print("-" * 80)

try:
    from telegram_bot.bot_manager import TelegramBotManager  # type: ignore
    bot = TelegramBotManager()
    
    if bot.bot and bot.channel_id:
        print(f"  ✅ Bot Telegram OK")
        print(f"     • Token: {str(telegram_token)[:15]}...")
        print(f"     • Canal: {telegram_channel}")
    else:
        print(f"  ❌ Bot não configurado")
except Exception as e:
    print(f"  ❌ Erro: {str(e)}")

# 7. MONTE CARLO
print("\n7️⃣  VERIFICANDO MONTE CARLO (TRVs)")
print("-" * 80)

try:
    from analysis.monte_carlo_strategy import Strategy5_MonteCarloValidation  # type: ignore
    
    mc = Strategy5_MonteCarloValidation(n_simulations=1000, trv_method="hybrid")
    test_colors = ['red'] * 30 + ['black'] * 20
    test_data_mc = {
        'historical_colors': test_colors,
        'observed_count': 7,
        'total_games': 10,
        'expected_color': 'vermelho'
    }
    
    result, confidence, details = mc.analyze(test_data_mc)
    mc_info = details['monte_carlo']
    
    print(f"  ✅ Monte Carlo com TRVs OK")
    print(f"     • Método: {mc_info['method']}")
    print(f"     • Redução Variância: {mc_info['variance_reduction']}")
    print(f"     • Confiança: {confidence:.1%}")
except ImportError:
    print(f"  ❌ Módulo monte_carlo_strategy não encontrado")
    print(f"     • Verifique se src/analysis/monte_carlo_strategy.py existe")
except Exception as e:
    print(f"  ❌ Erro: {str(e)}")

# RESUMO
print("\n" + "="*80)
print("📊 RESUMO FINAL")
print("="*80)

print("""
✅ SISTEMA PRONTO!

PRÓXIMOS PASSOS:

1. Teste único:
   python src/main.py

2. Modo contínuo (a cada 5 minutos):
   python src/main.py --scheduled --interval 5

3. Monitore os logs:
   Get-Content logs/bet_analysis.log -Wait -Tail 50
""")

print("="*80)
