"""
Script para obter seu Chat ID do Telegram
"""
import requests
import json

TOKEN = "8347334478:AAHGap7AeSEWG1vPG1OyRjg4wHNgCCFbAjg"

print("[*] Buscando Chat ID...")
print("[*] Abra o Telegram e:")
print("    1. Procure por seu bot (@seu_bot_name)")
print("    2. Envie /start")
print("    3. Envie qualquer mensagem")
print("[*] Aguardando...\n")

# Obter atualizacoes (mensagens recebidas)
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

try:
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if data.get('ok'):
        updates = data.get('result', [])
        
        if updates:
            print(f"[OK] Encontradas {len(updates)} mensagens\n")
            
            for update in updates:
                if 'message' in update:
                    chat_id = update['message']['chat']['id']
                    username = update['message']['chat'].get('username', 'N/A')
                    first_name = update['message']['chat'].get('first_name', 'N/A')
                    text = update['message'].get('text', 'N/A')
                    
                    print("=" * 60)
                    print(f"Chat ID: {chat_id}")
                    print(f"Username: {username}")
                    print(f"Primeiro Nome: {first_name}")
                    print(f"Última Mensagem: {text}")
                    print("=" * 60)
            
            print("\n[OK] Use o Chat ID acima para configurar .env:")
            print(f"    TELEGRAM_CHANNEL_ID={updates[0]['message']['chat']['id']}")
        else:
            print("[!] Nenhuma mensagem encontrada!")
            print("[!] Certifique-se de enviar uma mensagem para o bot no Telegram")
    else:
        print(f"[ERRO] Erro da API: {data.get('description', 'Desconhecido')}")
        
except Exception as e:
    print(f"[ERRO] Erro ao conectar: {str(e)}")
