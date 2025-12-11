"""
Testes para módulo do Telegram
"""
import pytest
from src.telegram_bot.bot_manager import TelegramBotManager

class TestTelegramBotManager:
    """Testes para o gerenciador do Telegram"""

    def test_bot_initialization(self):
        """Testa inicialização do bot"""
        bot_manager = TelegramBotManager()
        assert bot_manager is not None

    def test_message_formatting(self):
        """Testa formatação de mensagens"""
        bot_manager = TelegramBotManager()

        test_signal = {
            'game': 'Crash',
            'signal': 'TEST_SIGNAL',
            'message': 'This is a test signal',
            'confidence': 0.75,
            'timestamp': '2023-01-01 12:00:00'
        }

        formatted_message = bot_manager.format_signal_message(test_signal)
        assert 'Crash' in formatted_message
        assert 'TEST_SIGNAL' in formatted_message