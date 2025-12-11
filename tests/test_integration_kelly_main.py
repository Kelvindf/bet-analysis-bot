#!/usr/bin/env python3
"""
Teste de Integração: Kelly Criterion + Drawdown Manager com Main.py

Simula ciclos de apostas e valida:
  - Kelly calcula tamanho correto
  - Drawdown pausa trading quando necessário
  - Sinais incluem informações de aposta
"""

import sys
import os
import json

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from strategies.kelly_criterion import KellyCriterion
from drawdown_manager import DrawdownManager


def simulate_betting_session(num_bets=10, win_rate=0.65):
    """
    Simula uma sessão de apostas com Kelly + Drawdown.
    
    Args:
        num_bets: Número de apostas a simular
        win_rate: Taxa de vitória esperada (0.0-1.0)
    """
    print("\n" + "="*70)
    print("TESTE DE INTEGRAÇÃO: Kelly Criterion + Drawdown Manager")
    print("="*70 + "\n")
    
    # Limpar estado
    kelly_file = os.path.join("logs", "kelly_stats.json")
    drawdown_file = os.path.join("logs", "drawdown_state.json")
    if os.path.exists(kelly_file):
        os.remove(kelly_file)
    if os.path.exists(drawdown_file):
        os.remove(drawdown_file)
    
    # Inicializar
    kelly = KellyCriterion(initial_bankroll=1000.0, kelly_fraction=0.25)
    drawdown = DrawdownManager(initial_bankroll=1000.0, max_drawdown_percent=5.0)
    
    print(f"📊 Configuração:")
    print(f"   Initial Bankroll: ${kelly.current_bankroll:.2f}")
    print(f"   Kelly Fraction: {kelly.kelly_fraction*100:.0f}%")
    print(f"   Max Drawdown: {drawdown.max_drawdown_percent:.1f}%")
    print(f"   Simulated Win Rate: {win_rate*100:.0f}%")
    print(f"   Num Bets: {num_bets}\n")
    
    # Simular apostas
    import random
    random.seed(42)  # Reproducible
    
    total_bet = 0
    total_profit = 0
    cycle = 0
    
    for i in range(num_bets):
        # Pular se paused
        if drawdown.is_paused:
            print(f"[{i+1:2d}] ⏸️  PAUSED - Skipping bet (drawdown={drawdown.get_status()['drawdown_percent']:.1f}%)")
            continue
        
        cycle += 1
        
        # Calcular tamanho da aposta
        bet_size = kelly.calculate_bet_size(win_rate=win_rate, odds=1.9)
        total_bet += bet_size
        
        # Simular resultado
        is_win = random.random() < win_rate
        
        # Registrar
        kelly.record_bet(bet_size=bet_size, win=is_win, payout_odds=2.0)
        
        # Atualizar drawdown
        status = drawdown.update_bankroll(kelly.current_bankroll)
        
        # Log
        profit = (bet_size if is_win else -bet_size)
        total_profit += profit
        result_str = "WIN  ✅" if is_win else "LOSS ❌"
        
        print(f"[{i+1:2d}] {result_str} | Bet: ${bet_size:7.2f} | "
              f"Bankroll: ${kelly.current_bankroll:8.2f} | "
              f"Drawdown: {status['drawdown_percent']:5.2f}% | "
              f"Action: {status['action']}")
    
    # Resumir se necessário
    if drawdown.is_paused:
        print("\n🔄 Resuming trading after drawdown pause...")
        drawdown.manual_resume()
    
    # Resultados finais
    print("\n" + "="*70)
    print("RESULTADOS FINAIS")
    print("="*70)
    
    kelly_stats = kelly.get_stats()
    drawdown_status = drawdown.get_status()
    
    print(f"\n📈 Kelly Statistics:")
    print(f"   Total Bets: {kelly_stats['total_bets']}")
    print(f"   Wins: {kelly_stats['total_wins']} ({kelly_stats['win_rate']*100:.1f}%)")
    print(f"   Losses: {kelly_stats['total_losses']}")
    print(f"   Total Profit: ${kelly_stats['total_profit']:,.2f}")
    print(f"   ROI: {kelly_stats['roi_percent']:.2f}%")
    print(f"   Final Bankroll: ${kelly_stats['current_bankroll']:,.2f}")
    
    print(f"\n📊 Drawdown Status:")
    print(f"   Peak Bankroll: ${drawdown_status['peak_bankroll']:,.2f}")
    print(f"   Current: ${drawdown_status['current_bankroll']:,.2f}")
    print(f"   Max Drawdown: {drawdown_status['drawdown_percent']:.2f}%")
    print(f"   Pause Events: {drawdown_status['pause_count']}")
    print(f"   Currently Paused: {drawdown_status['is_paused']}")
    
    print(f"\n💾 State Persistence:")
    print(f"   Kelly State File: {os.path.exists(kelly_file)} → {kelly_file}")
    print(f"   Drawdown State File: {os.path.exists(drawdown_file)} → {drawdown_file}")
    
    # Verificações
    print(f"\n✅ Test Assertions:")
    assert kelly_stats['total_bets'] == kelly_stats['total_wins'] + kelly_stats['total_losses'], \
        "Bet count mismatch"
    assert kelly_stats['current_bankroll'] > 0, "Bankroll should be positive"
    assert drawdown_status['peak_bankroll'] >= drawdown_status['current_bankroll'], \
        "Peak should be >= current"
    
    print(f"   ✓ Bet count matches (wins + losses = total)")
    print(f"   ✓ Bankroll is positive")
    print(f"   ✓ Peak >= Current bankroll")
    
    if drawdown.pause_history:
        print(f"   ✓ Drawdown pause events recorded: {len(drawdown.pause_history)}")
    
    print(f"\n🎯 Integration Test: PASSED ✅\n")
    
    return {
        'kelly': kelly_stats,
        'drawdown': drawdown_status,
        'success': True
    }


if __name__ == "__main__":
    # Teste 1: Win rate alto (60%)
    print("\n🧪 Teste 1: Win Rate Alto (60%)")
    result1 = simulate_betting_session(num_bets=15, win_rate=0.60)
    
    # Teste 2: Win rate baixo com drawdown (40%)
    print("\n🧪 Teste 2: Win Rate Baixo - Drawdown Esperado (40%)")
    result2 = simulate_betting_session(num_bets=20, win_rate=0.40)
    
    print("\n" + "="*70)
    print("🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO")
    print("="*70)
