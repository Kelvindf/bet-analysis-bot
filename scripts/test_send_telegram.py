from src.telegram_bot.bot_manager import TelegramBotManager
from datetime import datetime

bm = TelegramBotManager()

signal = {
    'signal': 'TEST_SIGNAL',
    'message': 'Teste de envio de sinal — verificar recebimento',
    'confidence': 0.95,
    'timestamp': datetime.now(),
    'game': 'Test'
}

print('Enviando sinal de teste...')
bm.send_signals([signal])
print('Feito.')
