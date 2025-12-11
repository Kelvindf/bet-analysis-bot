#!/usr/bin/env python3
"""
Roda UM ciclo de análise em foreground com modo de teste ativado.

Este script é útil para observar a inicialização, a notificação ao Telegram
e o envio de um sinal forçado (quando não existirem sinais reais).
"""
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Configurar logging para console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import BetAnalysisPlatform
from src.telegram_bot.bot_manager import TelegramBotManager
from datetime import datetime

def main():
    logger.info('Iniciando teste: 1 ciclo (foreground) com test_mode=True')

    # Inicializa plataforma e bot
    platform = BetAnalysisPlatform(test_mode=True)
    bot = TelegramBotManager()

    # Envia notificação de inicialização
    try:
        bot.send_signals([{
            'game': 'Test',
            'signal': 'Inicializacao-Check',
            'message': 'Teste de inicialização do sistema (foreground).',
            'confidence': 0.99,
            'timestamp': datetime.now()
        }])
    except Exception as e:
        logger.warning(f'Não conseguiu enviar notificação inicial: {e}')

    # Forçar modo de teste na plataforma (garante sinal forçado se não houver sinais)
    platform.test_mode = True

    # Executar um ciclo de análise e encerrrar
    platform.run_analysis_cycle()

    # Mostrar estatísticas resumidas
    logger.info('Estatísticas após ciclo:')
    logger.info(platform.stats)

if __name__ == '__main__':
    main()
