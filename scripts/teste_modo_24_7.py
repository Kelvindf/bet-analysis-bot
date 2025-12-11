#!/usr/bin/env python3
"""
Teste Rápido - Modo 24/7

Testa se o sistema 24/7 pode inicializar e executar um ciclo
"""

import sys
import os
import time
from pathlib import Path

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

print("\n" + "="*80)
print("TESTE RÁPIDO - MODO 24/7")
print("="*80 + "\n")

try:
    print("[1] Testando imports...")
    from src.main import BetAnalysisPlatform
    print("    ✅ BetAnalysisPlatform importado")
    
    from src.telegram_bot.bot_manager import TelegramBotManager
    print("    ✅ TelegramBotManager importado")
    
    print("\n[2] Inicializando plataforma...")
    platform = BetAnalysisPlatform()
    print("    ✅ Plataforma inicializada")
    
    print("\n[3] Executando 1 ciclo de análise...")
    platform.run_analysis_cycle()
    print("    ✅ Ciclo concluído")
    
    print("\n[4] Verificando estatísticas...")
    print(f"    Ciclos: {platform.stats['signals_processed']}")
    print(f"    Sinais enviados: {platform.stats['signals_sent']}")
    print(f"    Cores coletadas: {platform.stats['colors_collected']}")
    
    print("\n" + "="*80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO")
    print("="*80)
    print("\nSistema 24/7 está pronto para usar!")
    print("Execute: python scripts\\modo_24_7.py")
    
except Exception as e:
    print(f"\n❌ ERRO: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
