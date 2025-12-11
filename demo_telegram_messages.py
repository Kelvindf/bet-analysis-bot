"""
Executa todos os testes de mensagens automaticamente
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
import requests
import time
from src.telegram_bot.message_enricher import TelegramMessageEnricher
from src.strategies.advanced_pattern_analyzer import PatternSignal
from datetime import datetime

load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('TELEGRAM_CHANNEL_ID')

def send_telegram_message(message: str, parse_mode: str = 'Markdown') -> bool:
    """Envia mensagem para Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': parse_mode
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print(f"✅ Mensagem {result['result']['message_id']} enviada")
                return True
        print(f"❌ Erro: {response.status_code}")
        return False
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False


print("\n" + "="*60)
print("🚀 DEMONSTRAÇÃO: Mensagens Melhoradas")
print("="*60)
print(f"\n📱 Abra o Telegram Web:")
print("   https://web.telegram.org/a/#8347334478")
print("\n⏱️  Enviando exemplos em 3 segundos...")
time.sleep(3)

enricher = TelegramMessageEnricher()

# 1. Mensagem Simples
print("\n[1/6] Mensagem simples...")
msg1 = enricher.create_simple_signal_message('Vermelho', 0.85)
send_telegram_message(msg1)
time.sleep(2)

# 2. Mensagem Rica
print("[2/6] Mensagem rica completa...")
signal = PatternSignal(
    signal_type='Preto',
    confidence=0.875,
    strength='MUITO_FORTE',
    volume_score=0.92,
    trend_score=0.85,
    sequence_score=0.78,
    volatility_score=0.88,
    current_streak=4,
    expected_reversal=True,
    risk_level='BAIXO',
    suggested_stake=0.035,
    stop_loss=2.0,
    take_profit=5.0,
    timestamp=datetime.now()
)
msg2 = enricher.create_rich_signal_message(signal.to_dict())
send_telegram_message(msg2)
time.sleep(3)

# 3. Alerta Success
print("[3/6] Alerta de sucesso...")
msg3 = enricher.create_alert_message('success', 'Sistema V2.0 ativado com melhorias!')
send_telegram_message(msg3)
time.sleep(2)

# 4. Alerta Fire
print("[4/6] Alerta de streak...")
msg4 = enricher.create_alert_message('fire', 'Streak de 6 Vermelho detectado! 🔥')
send_telegram_message(msg4)
time.sleep(2)

# 5. Resumo de Performance
print("[5/6] Resumo de performance...")
stats = {
    'total_signals': 25,
    'avg_confidence': 0.82,
    'avg_suggested_stake': 0.032,
    'strength_distribution': {'MUITO_FORTE': 10, 'FORTE': 12, 'MODERADO': 3},
    'risk_distribution': {'BAIXO': 18, 'MEDIO': 6, 'ALTO': 1},
    'signals_by_type': {'Vermelho': 13, 'Preto': 12}
}
msg5 = enricher.create_performance_summary(stats)
send_telegram_message(msg5)
time.sleep(3)

# 6. Comparação
print("[6/6] Comparação Antes vs Depois...")
msg_old = """⚠️ ANTES (sistema atual):

Sinal: Preto
Confiança: 80.6%"""
send_telegram_message(msg_old)
time.sleep(2)

msg_new = enricher.create_simple_signal_message('Preto', 0.806)
send_telegram_message(f"✨ DEPOIS (com melhorias):\n\n{msg_new}")

print("\n" + "="*60)
print("✅ DEMONSTRAÇÃO CONCLUÍDA!")
print("="*60)
print("\n📱 Confira as mensagens no Telegram Web!")
print("   https://web.telegram.org/a/#8347334478")
print("")
