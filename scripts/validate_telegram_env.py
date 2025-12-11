import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import Settings


def main():
    print("TELEGRAM_BOT_TOKEN:", Settings.TELEGRAM_BOT_TOKEN)
    print("TELEGRAM_CHANNEL_ID:", Settings.TELEGRAM_CHANNEL_ID)


if __name__ == '__main__':
    main()
