"""
Configurações da plataforma
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configurações da aplicação"""

    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8260416435:AAH7aPa8eL8bYG0051IPyulUXqmaetFxrzQ')
    TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', '8329919168')

    # Análise
    ANALYSIS_INTERVAL_MINUTES = int(os.getenv('ANALYSIS_INTERVAL_MINUTES', '2'))
    MIN_CONFIDENCE_LEVEL = float(os.getenv('MIN_CONFIDENCE_LEVEL', '0.65'))
    DATA_RETENTION_DAYS = 30

    # APIs
    BLAZE_API_BASE_URL = os.getenv('BLAZE_API_URL', 'https://blaze.com/api')
    REQUEST_TIMEOUT = 10
    MAX_RETRIES = 3

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = "logs/bet_analysis.log"