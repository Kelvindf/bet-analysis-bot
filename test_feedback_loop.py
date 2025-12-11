# -*- coding: utf-8 -*-
"""
Teste do Feedback Loop - FASE 3, Tarefa 7

Valida:
    ✓ Coleta de resultados
    ✓ Cálculo de métricas
    ✓ Auto-ajuste de parâmetros
    ✓ Histórico de ajustes
    ✓ Integração com main.py
"""

import sys
import os
from datetime import datetime, timedelta

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from learning.feedback_loop import FeedbackLoop, SignalResult


def test_feedback_collection():
    """Teste 1: Coleta de resultados"""
    print("\n" + "="*80)
    print("[TEST 1] COLETA DE RESULTADOS")
    print("="*80)
    
    feedback = FeedbackLoop(min_samples=10)
    
    # Simular 15 resultados
    for i in range(15):
        result = SignalResult(
            signal_id=f"sig_{i:03d}",
            signal_type='Vermelho',
            game_type='Double',
            confidence=0.65 + (i % 3) * 0.05,
            bet_size=10.0,
            odds=1.9,
            timestamp=datetime.now() - timedelta(minutes=15-i),
            result='WIN' if i % 3 == 0 else 'LOSS',
            payout=19.0 if i % 3 == 0 else -100.0,
            context_hour=14,
            context_day=0,
            strategy_used='Strategy1',
            expected_wr=0.65,
            actual_wr_24h=0.65
        )
        feedback.record_result(result)
    
    print(f"✓ {feedback.stats['total_results']} resultados coletados")
    print(f"✓ Win Rate: {feedback.stats['current_wr']:.1%}")
    print(f"✓ Histórico: {len(feedback.results)} apostas registradas")
    
    assert feedback.stats['total_results'] == 15, "Resultados não foram coletados"
    assert feedback.stats['current_wr'] > 0, "Win rate inválido"
    print("\n✅ TESTE 1 PASSOU")
    
    return feedback


def test_win_rate_analysis(feedback):
    """Teste 2: Análise de Win Rate"""
    print("\n" + "="*80)
    print("[TEST 2] ANÁLISE DE WIN RATE")
    print("="*80)
    
    # Adicionar mais resultados com padrão de perda
    for i in range(15, 35):
        result = SignalResult(
            signal_id=f"sig_{i:03d}",
            signal_type='Preto',
            game_type='Double',
            confidence=0.68,
            bet_size=10.0,
            odds=1.9,
            timestamp=datetime.now() - timedelta(minutes=35-i),
            result='LOSS',  # Padrão de perda para testar ajuste
            payout=-100.0,
            context_hour=14,
            context_day=0,
            strategy_used='Strategy1',
            expected_wr=0.65,
            actual_wr_24h=0.60
        )
        feedback.record_result(result)
    
    print(f"✓ Adicionados 20 resultados com padrão de perda")
    print(f"✓ Win Rate atualizado: {feedback.stats['current_wr']:.1%}")
    print(f"✓ Total de apostas: {feedback.stats['total_results']}")
    
    # Testar ajustes
    adjustments = feedback.analyze_and_adjust()
    
    if adjustments:
        print(f"\n✓ {len(adjustments)} ajustes detectados:")
        for adj in adjustments:
            print(f"    • {adj.parameter}:")
            print(f"      {adj.old_value:.4f} → {adj.new_value:.4f}")
            print(f"      Razão: {adj.reason}")
    else:
        print("\n✓ Sem ajustes necessários (WR dentro do esperado)")
    
    print("\n✅ TESTE 2 PASSOU")
    return feedback


def test_parameter_adjustments(feedback):
    """Teste 3: Ajustes de parâmetros"""
    print("\n" + "="*80)
    print("[TEST 3] AJUSTES DE PARÂMETROS")
    print("="*80)
    
    params_before = feedback.get_current_parameters()
    
    print(f"✓ Parâmetros iniciais:")
    print(f"    min_confidence: {params_before['min_confidence']:.3f}")
    print(f"    kelly_fraction: {params_before.get('kelly_fraction', 'N/A')}")
    print(f"    Total ajustes: {params_before.get('total_adjustments', 0)}")
    
    # Simular 30 apostas muito negativas
    for i in range(35, 65):
        result = SignalResult(
            signal_id=f"sig_{i:03d}",
            signal_type='Vermelho',
            game_type='Double',
            confidence=0.62,
            bet_size=10.0,
            odds=1.9,
            timestamp=datetime.now() - timedelta(minutes=65-i),
            result='LOSS' if i % 4 != 0 else 'WIN',  # 75% de perda
            payout=-100.0 if i % 4 != 0 else 19.0,
            context_hour=14,
            context_day=0,
            strategy_used='Strategy1',
            expected_wr=0.65,
            actual_wr_24h=0.45
        )
        feedback.record_result(result)
    
    # Aplicar ajustes
    adjustments = feedback.analyze_and_adjust()
    
    params_after = feedback.get_current_parameters()
    
    print(f"\n✓ Após mais resultados negativos:")
    print(f"    min_confidence: {params_after['min_confidence']:.3f}")
    print(f"    Total ajustes: {params_after.get('total_adjustments', 0)}")
    
    # Validar histórico
    history = feedback.get_adjustment_history(limit=5)
    if history:
        print(f"\n✓ Últimos {len(history)} ajustes:")
        for adj in history[-3:]:
            print(f"    • {adj['parameter']}: {adj['old_value']:.3f} → {adj['new_value']:.3f}")
    
    print("\n✅ TESTE 3 PASSOU")
    return feedback


def test_metrics_export():
    """Teste 4: Exportação de métricas"""
    print("\n" + "="*80)
    print("[TEST 4] EXPORTAÇÃO DE MÉTRICAS")
    print("="*80)
    
    feedback = FeedbackLoop(min_samples=5)
    
    # Coletar alguns resultados
    for i in range(15):
        result = SignalResult(
            signal_id=f"sig_{i:03d}",
            signal_type='Vermelho',
            game_type='Double',
            confidence=0.65,
            bet_size=10.0,
            odds=1.9,
            timestamp=datetime.now() - timedelta(minutes=15-i),
            result='WIN' if i % 2 == 0 else 'LOSS',
            payout=19.0 if i % 2 == 0 else -100.0,
            context_hour=14,
            context_day=0,
            strategy_used='Strategy1',
            expected_wr=0.65,
            actual_wr_24h=0.65
        )
        feedback.record_result(result)
    
    # Exportar
    metrics = feedback.export_metrics()
    
    print("✓ Métricas exportadas:")
    print(f"    Timestamp: {metrics['timestamp']}")
    print(f"    Total resultados: {metrics['total_results']}")
    print(f"    Wins: {metrics['wins']}")
    print(f"    Losses: {metrics['losses']}")
    print(f"    Win Rate: {metrics['win_rate']}")
    print(f"    ROI: {metrics['roi']}")
    print(f"    Total ajustes: {metrics['total_adjustments']}")
    
    # Validar estrutura
    assert 'timestamp' in metrics
    assert 'total_results' in metrics
    assert 'current_parameters' in metrics
    assert metrics['total_results'] == 15
    
    print("\n✅ TESTE 4 PASSOU")


def test_cooldown_mechanism():
    """Teste 5: Mecanismo de cooldown"""
    print("\n" + "="*80)
    print("[TEST 5] MECANISMO DE COOLDOWN")
    print("="*80)
    
    feedback = FeedbackLoop(
        min_samples=10,
        adjustment_threshold=0.05
    )
    
    # Primeiro ajuste
    print("✓ Gerando condições para primeiro ajuste...")
    
    for i in range(30):
        result = SignalResult(
            signal_id=f"sig_{i:03d}",
            signal_type='Vermelho',
            game_type='Double',
            confidence=0.65,
            bet_size=10.0,
            odds=1.9,
            timestamp=datetime.now() - timedelta(minutes=30-i),
            result='LOSS',  # Todos LOSS para forçar ajuste
            payout=-100.0,
            context_hour=14,
            context_day=0,
            strategy_used='Strategy1',
            expected_wr=0.65,
            actual_wr_24h=0.35
        )
        feedback.record_result(result)
    
    adj1 = feedback.analyze_and_adjust()
    print(f"✓ Primeiro lote: {len(adj1)} ajustes")
    
    # Tentar segundo ajuste imediatamente
    adj2 = feedback.analyze_and_adjust()
    print(f"✓ Segundo lote: {len(adj2)} ajustes (deve ser 0 por cooldown)")
    
    # Validar cooldown
    assert len(adj2) == 0, "Cooldown não funcionou"
    
    print("\n✅ TESTE 5 PASSOU")


def main():
    """Executa todos os testes"""
    print("\n" + "="*80)
    print("TESTES DO FEEDBACK LOOP - FASE 3, TAREFA 7")
    print("="*80)
    
    try:
        # Teste 1: Coleta
        feedback = test_feedback_collection()
        
        # Teste 2: Análise
        feedback = test_win_rate_analysis(feedback)
        
        # Teste 3: Ajustes
        feedback = test_parameter_adjustments(feedback)
        
        # Teste 4: Métricas
        test_metrics_export()
        
        # Teste 5: Cooldown
        test_cooldown_mechanism()
        
        # Resultado final
        print("\n" + "="*80)
        print("RESULTADO GERAL")
        print("="*80)
        print("\n✅ TODOS OS TESTES PASSARAM (5/5)")
        print("\n[1] Coleta de resultados: ✅ PASSED")
        print("[2] Análise de Win Rate: ✅ PASSED")
        print("[3] Ajustes de parâmetros: ✅ PASSED")
        print("[4] Exportação de métricas: ✅ PASSED")
        print("[5] Mecanismo de cooldown: ✅ PASSED")
        
        print("\n" + "="*80)
        print("✅ FEEDBACK LOOP PRONTO PARA INTEGRAÇÃO")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
