"""
Script de Teste - Melhorias nas Estratégias
============================================

Testa os novos componentes:
1. AdvancedPatternAnalyzer
2. TelegramMessageEnricher

Uso:
    python test_improvements.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from strategies.advanced_pattern_analyzer import AdvancedPatternAnalyzer
from telegram_bot.message_enricher import TelegramMessageEnricher


def generate_sample_data(n_rows: int = 50) -> pd.DataFrame:
    """Gera dados de exemplo para teste"""
    colors = []
    rolls = []
    timestamps = []
    
    base_time = datetime.now() - timedelta(minutes=n_rows)
    
    # Simular padrão com streak
    current_color = 'red'
    streak = 0
    
    for i in range(n_rows):
        # Criar streaks realistas
        if streak >= 5:  # Após 5, maior chance de reverter
            if np.random.random() > 0.3:
                current_color = 'black' if current_color == 'red' else 'red'
                streak = 1
            else:
                streak += 1
        elif np.random.random() > 0.6:  # 40% chance de mudar
            current_color = 'black' if current_color == 'red' else 'red'
            streak = 1
        else:
            streak += 1
        
        colors.append(current_color)
        rolls.append(np.random.randint(0, 15))
        timestamps.append(base_time + timedelta(minutes=i))
    
    return pd.DataFrame({
        'color': colors,
        'roll': rolls,
        'timestamp': timestamps
    })


def test_advanced_analyzer():
    """Testa o analisador avançado"""
    print("\n" + "="*60)
    print("TESTE: Advanced Pattern Analyzer")
    print("="*60)
    
    # Gerar dados
    data = generate_sample_data(50)
    print(f"\n[OK] Dados gerados: {len(data)} registros")
    print(f"Últimas 5 cores: {data['color'].tail(5).tolist()}")
    
    # Criar analisador
    analyzer = AdvancedPatternAnalyzer(min_confidence=0.60)
    
    # Analisar
    signal = analyzer.analyze(data)
    
    if signal:
        print(f"\n{'-'*60}")
        print("SINAL GERADO:")
        print(f"{'-'*60}")
        print(f"Tipo: {signal.signal_type}")
        print(f"Confiança: {signal.confidence:.1%}")
        print(f"Força: {signal.strength}")
        print(f"Risco: {signal.risk_level}")
        print(f"\nScores:")
        print(f"  • Volume: {signal.volume_score:.3f}")
        print(f"  • Tendência: {signal.trend_score:.3f}")
        print(f"  • Sequência: {signal.sequence_score:.3f}")
        print(f"  • Volatilidade: {signal.volatility_score:.3f}")
        print(f"\nContexto:")
        print(f"  • Streak atual: {signal.current_streak}")
        print(f"  • Reversão esperada: {signal.expected_reversal}")
        print(f"\nGestão:")
        print(f"  • Stake sugerido: {signal.suggested_stake:.1%}")
        print(f"  • Stop-loss: {signal.stop_loss}")
        print(f"  • Take-profit: {signal.take_profit}")
        print(f"{'-'*60}")
        
        return signal
    else:
        print("\n[!] Nenhum sinal válido gerado (confiança abaixo do mínimo)")
        return None


def test_message_enricher(signal):
    """Testa o enriquecedor de mensagens"""
    print("\n" + "="*60)
    print("TESTE: Telegram Message Enricher")
    print("="*60)
    
    enricher = TelegramMessageEnricher()
    
    if signal:
        # Mensagem rica
        rich_message = enricher.create_rich_signal_message(signal.to_dict())
        print("\n[MENSAGEM RICA]")
        print(rich_message)
        
        # Mensagem simples
        simple_message = enricher.create_simple_signal_message(
            signal.signal_type, 
            signal.confidence
        )
        print("\n" + "-"*60)
        print("[MENSAGEM SIMPLES]")
        print(simple_message)
    else:
        # Testar com dados mock
        print("\n[!] Usando dados mock para teste")
        simple_message = enricher.create_simple_signal_message('Vermelho', 0.75)
        print(simple_message)
    
    # Testar alertas
    print("\n" + "-"*60)
    print("[ALERTAS]")
    print(enricher.create_alert_message('success', 'Sistema operacional!'))
    print(enricher.create_alert_message('warning', 'Volatilidade alta detectada'))
    print(enricher.create_alert_message('fire', 'Streak de 6! Sinal forte próximo'))


def test_multiple_analyses():
    """Testa múltiplas análises e gera estatísticas"""
    print("\n" + "="*60)
    print("TESTE: Múltiplas Análises")
    print("="*60)
    
    analyzer = AdvancedPatternAnalyzer(min_confidence=0.60)
    enricher = TelegramMessageEnricher()
    
    signals_generated = 0
    
    for i in range(5):
        print(f"\n[Análise {i+1}/5]", end=" ")
        data = generate_sample_data(np.random.randint(30, 60))
        signal = analyzer.analyze(data)
        
        if signal:
            signals_generated += 1
            print(f"✅ {signal.signal_type} ({signal.confidence:.1%})")
        else:
            print("❌ Sem sinal")
    
    # Estatísticas
    print("\n" + "="*60)
    print("ESTATÍSTICAS DE PERFORMANCE")
    print("="*60)
    
    stats = analyzer.get_performance_stats()
    summary = enricher.create_performance_summary(stats)
    print(summary)


def main():
    """Executa todos os testes"""
    print("\n" + "#"*60)
    print("# TESTE DE MELHORIAS - Estratégias Avançadas")
    print("#"*60)
    
    try:
        # Teste 1: Analisador
        signal = test_advanced_analyzer()
        
        # Teste 2: Mensagens
        test_message_enricher(signal)
        
        # Teste 3: Múltiplas análises
        test_multiple_analyses()
        
        print("\n" + "#"*60)
        print("# ✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO")
        print("#"*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
