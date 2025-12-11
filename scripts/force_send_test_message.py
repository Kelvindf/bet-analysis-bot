#!/usr/bin/env python3
"""
Força o envio imediato de uma mensagem de teste usando TelegramBotManager.

Útil para confirmar a cadeia de envio sem executar toda a plataforma.
"""
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.telegram_bot.bot_manager import TelegramBotManager

def main():
    bot = TelegramBotManager()

    # Mensagem de teste simples estruturada como os sinais que bot_manager espera
    test_signal = {
        'game': 'Test',
        'signal': 'FORCE-TEST-001',
        'message': 'Envio forçado de teste — confirmar recebimento do bot.',
        'confidence': 0.95,
        'timestamp': datetime.now()
    }

    logger.info('Enviando sinal de teste forçado...')
    bot.send_signals([test_signal])
    logger.info('Envio concluído (verifique o Telegram).')

if __name__ == '__main__':
    main()
