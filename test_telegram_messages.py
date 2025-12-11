"""
Testador de Mensagens Telegram
================================

Envia mensagens de TESTE diretamente para o Telegram
para validar formatação Markdown, emojis, etc.

Abra o Telegram Web em paralelo para ver os resultados:
https://web.telegram.org/a/#8347334478

Uso:
    python test_telegram_messages.py
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
import requests
import time
from telegram_bot.message_enricher import TelegramMessageEnricher
from strategies.advanced_pattern_analyzer import PatternSignal
from datetime import datetime

load_dotenv()

# Configuração
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') or os.getenv('TELEGRAM_CHANNEL_ID')

def send_telegram_message(message: str, parse_mode: str = 'Markdown') -> bool:
    """Envia mensagem para Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': CHAT_ID,
            'text': message,
            'parse_mode': parse_mode
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print(f"✅ Mensagem enviada! (ID: {result['result']['message_id']})")
                return True
            else:
                print(f"❌ Erro na resposta: {result}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar: {str(e)}")
        return False


def test_simple_message():
    """Teste 1: Mensagem simples"""
    print("\n" + "="*60)
    print("TESTE 1: Mensagem Simples")
    print("="*60)
    
    enricher = TelegramMessageEnricher()
    message = enricher.create_simple_signal_message('Vermelho', 0.85)
    
    print("\nMensagem gerada:")
    print(message)
    print("\nEnviando para Telegram...")
    
    send_telegram_message(message)
    time.sleep(2)


def test_rich_message():
    """Teste 2: Mensagem rica completa"""
    print("\n" + "="*60)
    print("TESTE 2: Mensagem Rica Completa")
    print("="*60)
    
    # Criar sinal mock
    signal = PatternSignal(
        signal_type='Preto',
        confidence=0.875,
        strength='MUITO_FORTE',
        volume_score=0.92,
        trend_score=0.85,
        sequence_score=0.78,
        volatility_score=0.88,
        current_streak=4,
        expected_reversal=True,
        risk_level='BAIXO',
        suggested_stake=0.035,
        stop_loss=2.0,
        take_profit=5.0,
        timestamp=datetime.now()
    )
    
    enricher = TelegramMessageEnricher()
    message = enricher.create_rich_signal_message(signal.to_dict())
    
    print("\nMensagem gerada:")
    print(message)
    print("\nEnviando para Telegram...")
    
    send_telegram_message(message)
    time.sleep(2)


def test_alert_messages():
    """Teste 3: Mensagens de alerta"""
    print("\n" + "="*60)
    print("TESTE 3: Mensagens de Alerta")
    print("="*60)
    
    enricher = TelegramMessageEnricher()
    
    alerts = [
        ('success', '✅ Sistema iniciado com sucesso!'),
        ('warning', '⚠️ Volatilidade alta detectada'),
        ('fire', '🔥 Streak de 6 detectado - Sinal forte iminente!'),
        ('rocket', '🚀 Confiança acima de 90% - Sinal premium'),
    ]
    
    for alert_type, text in alerts:
        message = enricher.create_alert_message(alert_type, text)
        print(f"\n{message}")
        send_telegram_message(message)
        time.sleep(1)


def test_performance_summary():
    """Teste 4: Resumo de performance"""
    print("\n" + "="*60)
    print("TESTE 4: Resumo de Performance")
    print("="*60)
    
    # Stats mock
    stats = {
        'total_signals': 25,
        'avg_confidence': 0.78,
        'avg_suggested_stake': 0.028,
        'strength_distribution': {
            'MUITO_FORTE': 8,
            'FORTE': 12,
            'MODERADO': 5
        },
        'risk_distribution': {
            'BAIXO': 15,
            'MEDIO': 8,
            'ALTO': 2
        },
        'signals_by_type': {
            'Vermelho': 13,
            'Preto': 12
        }
    }
    
    enricher = TelegramMessageEnricher()
    message = enricher.create_performance_summary(stats)
    
    print("\nMensagem gerada:")
    print(message)
    print("\nEnviando para Telegram...")
    
    send_telegram_message(message)
    time.sleep(2)


def test_markdown_formatting():
    """Teste 5: Formatação Markdown"""
    print("\n" + "="*60)
    print("TESTE 5: Teste de Formatação Markdown")
    print("="*60)
    
    test_messages = [
        # Negrito
        "*Texto em negrito*",
        
        # Itálico
        "_Texto em itálico_",
        
        # Combinado
        "*Negrito* e _itálico_ juntos",
        
        # Lista
        """📊 *Lista de Testes:*
• Item 1
• Item 2
• Item 3""",
        
        # Emojis + Formatação
        """🎯 *TESTE COMPLETO*

📈 *Indicadores:*
• Volume: 0.95 ⭐⭐⭐⭐⭐
• Tendência: 0.88 ⭐⭐⭐⭐
• Risco: BAIXO 🟢

💰 *Gestão:*
• Stake: *3.5%*
• Stop: 2 perdas
• Target: 5 ganhos"""
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\nTeste {i}:")
        print(message)
        print("\nEnviando...")
        send_telegram_message(message)
        time.sleep(2)


def test_comparison():
    """Teste 6: Comparação Antes vs Depois"""
    print("\n" + "="*60)
    print("TESTE 6: Comparação Antes vs Depois")
    print("="*60)
    
    # Mensagem antiga (simples)
    old_message = """Sinal: Vermelho
Confiança: 80.6%"""
    
    print("\n[ANTES - Mensagem Antiga]")
    print(old_message)
    print("\nEnviando...")
    send_telegram_message(old_message)
    time.sleep(3)
    
    # Mensagem nova (rica)
    enricher = TelegramMessageEnricher()
    new_message = enricher.create_simple_signal_message('Vermelho', 0.806)
    
    print("\n[DEPOIS - Mensagem Nova]")
    print(new_message)
    print("\nEnviando...")
    send_telegram_message(new_message)
    time.sleep(2)


def interactive_test():
    """Modo interativo - enviar mensagens personalizadas"""
    print("\n" + "="*60)
    print("MODO INTERATIVO")
    print("="*60)
    print("\nDigite suas mensagens para testar (ou 'sair' para encerrar)")
    print("Dica: Use * para negrito, _ para itálico, emojis 🎯 funcionam!")
    print("")
    
    while True:
        try:
            message = input("\n📝 Mensagem: ")
            
            if message.lower() in ['sair', 'exit', 'quit']:
                print("Encerrando...")
                break
            
            if message.strip():
                send_telegram_message(message)
            
        except KeyboardInterrupt:
            print("\n\nEncerrando...")
            break
        except EOFError:
            break


def main():
    """Menu principal"""
    print("\n" + "#"*60)
    print("# TESTADOR DE MENSAGENS TELEGRAM")
    print("#"*60)
    print(f"\nBot: {BOT_TOKEN[:10]}...")
    print(f"Chat ID: {CHAT_ID}")
    print(f"\n🌐 Abra o Telegram Web para ver os resultados:")
    print("   https://web.telegram.org/a/#8347334478")
    print("")
    
    while True:
        print("\n" + "="*60)
        print("MENU DE TESTES")
        print("="*60)
        print("1. Mensagem simples")
        print("2. Mensagem rica completa")
        print("3. Alertas diversos")
        print("4. Resumo de performance")
        print("5. Teste de formatação Markdown")
        print("6. Comparação Antes vs Depois")
        print("7. Modo interativo")
        print("8. EXECUTAR TODOS OS TESTES")
        print("0. Sair")
        print("")
        
        try:
            choice = input("Escolha uma opção: ").strip()
            
            if choice == '1':
                test_simple_message()
            elif choice == '2':
                test_rich_message()
            elif choice == '3':
                test_alert_messages()
            elif choice == '4':
                test_performance_summary()
            elif choice == '5':
                test_markdown_formatting()
            elif choice == '6':
                test_comparison()
            elif choice == '7':
                interactive_test()
            elif choice == '8':
                print("\n🚀 Executando TODOS os testes...")
                test_simple_message()
                test_rich_message()
                test_alert_messages()
                test_performance_summary()
                test_markdown_formatting()
                test_comparison()
                print("\n✅ Todos os testes concluídos!")
            elif choice == '0':
                print("\n👋 Até logo!")
                break
            else:
                print("❌ Opção inválida")
                
        except KeyboardInterrupt:
            print("\n\n👋 Interrompido pelo usuário")
            break
        except EOFError:
            break
        except Exception as e:
            print(f"❌ Erro: {str(e)}")


if __name__ == "__main__":
    main()
