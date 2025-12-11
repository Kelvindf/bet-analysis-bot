#!/usr/bin/env python3
"""Teste rápido do bot do Telegram - verifica se consegue enviar mensagens"""

import os
import sys
from dotenv import load_dotenv
import requests

# Carregar .env
load_dotenv()

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('TELEGRAM_CHANNEL_ID')

print("╔══════════════════════════════════════════════════════════════╗")
print("║           TESTE DO BOT DO TELEGRAM                          ║")
print("╚══════════════════════════════════════════════════════════════╝")
print()

# 1. Verificar variáveis
print(f"✓ BOT_TOKEN: {BOT_TOKEN[:20]}... (encontrado)")
print(f"✓ CHAT_ID: {CHAT_ID}")
print()

if not BOT_TOKEN or not CHAT_ID:
    print("❌ ERRO: Variáveis de ambiente não encontradas!")
    sys.exit(1)

# 2. Testar getMe (bot info)
print("📡 Testando conexão com o bot...")
try:
    response = requests.get(f'https://api.telegram.org/bot{BOT_TOKEN}/getMe')
    data = response.json()
    
    if data.get('ok'):
        bot_info = data['result']
        print(f"✅ Bot conectado: @{bot_info['username']}")
        print(f"   Nome: {bot_info['first_name']}")
        print(f"   ID: {bot_info['id']}")
    else:
        print(f"❌ Erro ao conectar bot: {data}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Erro de conexão: {e}")
    sys.exit(1)

print()

# 3. Testar envio de mensagem
print("📤 Enviando mensagem de teste...")
try:
    message = """
🧪 TESTE DO BOT - Bet Analysis Platform

✅ Bot está funcionando corretamente!
✅ Kelly Criterion ativo
✅ Drawdown Manager ativo
✅ Pipeline 6 estratégias ativo

📊 Status: PRONTO PARA ENVIAR SINAIS
"""
    
    response = requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
        json={
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
    )
    
    data = response.json()
    
    if data.get('ok'):
        print(f"✅ Mensagem enviada com sucesso!")
        print(f"   Message ID: {data['result']['message_id']}")
        print(f"   Chat ID: {data['result']['chat']['id']}")
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  ✅ TELEGRAM BOT FUNCIONANDO CORRETAMENTE!                  ║")
        print("║  Você deve ter recebido uma mensagem no Telegram            ║")
        print("╚══════════════════════════════════════════════════════════════╝")
    else:
        print(f"❌ Erro ao enviar mensagem:")
        print(f"   {data}")
        print()
        
        # Diagnóstico de erros comuns
        error_desc = data.get('description', '')
        
        if 'chat not found' in error_desc.lower():
            print("💡 SOLUÇÃO:")
            print("   1. Inicie uma conversa com o bot no Telegram")
            print("   2. Envie /start para o bot")
            print("   3. Execute este script novamente")
        elif 'bot was blocked' in error_desc.lower():
            print("💡 SOLUÇÃO:")
            print("   1. Desbloqueie o bot no Telegram")
            print("   2. Envie /start para o bot")
            print("   3. Execute este script novamente")
        elif 'unauthorized' in error_desc.lower():
            print("💡 SOLUÇÃO:")
            print("   1. Verifique se o TELEGRAM_BOT_TOKEN está correto")
            print("   2. Obtenha um novo token com @BotFather se necessário")
        else:
            print("💡 SOLUÇÃO:")
            print("   1. Verifique se o CHAT_ID está correto")
            print(f"   2. Use o script get_chat_id.py para obter o ID correto")
        
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Erro ao enviar mensagem: {e}")
    sys.exit(1)
