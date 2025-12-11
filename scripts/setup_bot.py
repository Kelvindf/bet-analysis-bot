"""
Script para setup inicial do bot do Telegram
"""
import asyncio
import os
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

async def setup_telegram():
    """Configuração inicial do Telegram"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        print("❌ Token do Telegram não encontrado no .env")
        print("💡 Adicione: TELEGRAM_BOT_TOKEN=seu_token_aqui")
        return

    bot = Bot(token=token)

    try:
        # Testa conexão
        me = await bot.get_me()
        print(f"✅ Bot conectado: @{me.username}")

        # Solicita canal
        channel_name = input("Digite o username do canal (ex: @meucanal): ").strip()

        if channel_name:
            try:
                chat = await bot.get_chat(channel_name)
                print(f"✅ Canal encontrado: {chat.title}")

                # Verifica se o bot é administrador
                chat_member = await bot.get_chat_member(chat.id, me.id)
                if chat_member.status in ['administrator', 'creator']:
                    print("✅ Bot é administrador do canal")

                    # Atualiza .env
                    with open('.env', 'r') as f:
                        lines = f.readlines()

                    # Remove linha existente se houver
                    lines = [line for line in lines if not line.startswith('TELEGRAM_CHANNEL_ID=')]

                    # Adiciona nova linha
                    lines.append(f'TELEGRAM_CHANNEL_ID={channel_name}\n')

                    with open('.env', 'w') as f:
                        f.writelines(lines)

                    print("✅ Configuração salva no .env")
                    print("\n🎯 Configuração concluída! Agora execute:")
                    print("   python src/main.py")

                else:
                    print("❌ O bot precisa ser administrador do canal")
                    print("💡 Adicione o bot como administrador no Telegram")

            except Exception as e:
                print(f"❌ Erro ao acessar canal: {e}")
                print("💡 Certifique-se de:")
                print("   - O canal existe")
                print("   - O username está correto (começa com @)")
                print("   - O bot foi adicionado ao canal")

    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        print("💡 Verifique se o token está correto")

if __name__ == "__main__":
    print("🤖 Configuração do Bot do Telegram")
    print("=" * 40)
    asyncio.run(setup_telegram())