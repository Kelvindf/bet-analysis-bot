import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT = os.getenv('TELEGRAM_CHANNEL_ID')

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    'chat_id': CHAT,
    'text': 'Teste HTTP direto: verifica se o chat existe e aceita mensagens (mensagem de teste).'
}

r = requests.post(url, data=payload)
print('status_code =', r.status_code)
try:
    print(r.json())
except Exception:
    print(r.text)
