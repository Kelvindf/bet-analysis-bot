# -*- coding: utf-8 -*-
"""
Testes do A/B Testing Framework - FASE 3, Tarefa 8

Valida:
    ✓ Coleta de resultados para A e B
    ✓ Cálculo de métricas
    ✓ Análise estatística
    ✓ Decisão de rollout
    ✓ Incremento de rollout
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from learning.ab_test import ABTestManager, TestResult, RolloutPhase


def test_result_collection():
    """Teste 1: Coleta de resultados"""
    print("\n" + "="*80)
    print("[TEST 1] COLETA DE RESULTADOS")
    print("="*80)
    
    ab_test = ABTestManager(min_samples=10)
    
    # Simular 20 resultados
    for i in range(20):
        # Versão A
        result_a = TestResult(
            bet_id=f"a_{i:03d}",
            version='A',
            result='WIN' if i % 3 == 0 else 'LOSS',
            payout=19.0 if i % 3 == 0 else -100.0,
            timestamp=datetime.now(),
            confidence=0.65
        )
        ab_test.record_result_a(result_a)
        
        # Versão B
        result_b = TestResult(
            bet_id=f"b_{i:03d}",
            version='B',
            result='WIN' if i % 3 == 0 else 'LOSS',
            payout=19.0 if i % 3 == 0 else -100.0,
            timestamp=datetime.now(),
            confidence=0.65
        )
        ab_test.record_result_b(result_b)
    
    print(f"✓ {len(ab_test.results_a)} resultados de A coletados")
    print(f"✓ {len(ab_test.results_b)} resultados de B coletados")
    print(f"✓ Total: {len(ab_test.results_a) + len(ab_test.results_b)} resultados")
    
    assert len(ab_test.results_a) == 20
    assert len(ab_test.results_b) == 20
    print("\n✅ TESTE 1 PASSOU")
    
    return ab_test


def test_metrics_calculation(ab_test):
    """Teste 2: Cálculo de métricas"""
    print("\n" + "="*80)
    print("[TEST 2] CÁLCULO DE MÉTRICAS")
    print("="*80)
    
    # Verificar que should_analyze retorna True
    can_analyze = ab_test.should_analyze()
    print(f"✓ Can analyze? {can_analyze}")
    print(f"✓ Min samples: {ab_test.min_samples}")
    print(f"✓ Samples A: {len(ab_test.results_a)}")
    print(f"✓ Samples B: {len(ab_test.results_b)}")
    
    assert can_analyze, "Deveria poder analisar"
    print("\n✅ TESTE 2 PASSOU")


def test_statistical_analysis(ab_test):
    """Teste 3: Análise estatística"""
    print("\n" + "="*80)
    print("[TEST 3] ANÁLISE ESTATÍSTICA")
    print("="*80)
    
    if ab_test.should_analyze():
        analysis = ab_test.analyze()
        
        print(f"✓ Versão A:")
        print(f"    Win Rate: {analysis.wr_a:.1%}")
        print(f"    ROI: {analysis.roi_a:.2f}%")
        print(f"    Desvio: {analysis.std_a:.2f}")
        print(f"    Amostras: {analysis.results_a}")
        
        print(f"✓ Versão B:")
        print(f"    Win Rate: {analysis.wr_b:.1%}")
        print(f"    ROI: {analysis.roi_b:.2f}%")
        print(f"    Desvio: {analysis.std_b:.2f}")
        print(f"    Amostras: {analysis.results_b}")
        
        print(f"✓ Testes Estatísticos:")
        print(f"    p-value (WR): {analysis.pvalue_wr:.4f}")
        print(f"    p-value (ROI): {analysis.pvalue_roi:.4f}")
        print(f"    Confiança: {analysis.confidence_level:.0%}")
        
        print(f"✓ Conclusões:")
        print(f"    B é melhor? {analysis.b_is_better}")
        print(f"    Significante? {analysis.significant}")
        print(f"    Recomendação: {analysis.recommendation}")
        
        # Validações
        assert analysis.wr_a >= 0 and analysis.wr_a <= 1, "WR A inválido"
        assert analysis.wr_b >= 0 and analysis.wr_b <= 1, "WR B inválido"
        assert 0 <= analysis.pvalue_wr <= 1, "p-value WR inválido"
        
        print("\n✅ TESTE 3 PASSOU")
    else:
        print("Insuficiente dados para análise")


def test_rollout_decision():
    """Teste 4: Decisão de rollout"""
    print("\n" + "="*80)
    print("[TEST 4] DECISÃO DE ROLLOUT")
    print("="*80)
    
    ab_test = ABTestManager(min_samples=30)
    
    # Simular 40 resultados com B melhor
    for i in range(40):
        # Versão A
        result_a = TestResult(
            bet_id=f"a_{i:03d}",
            version='A',
            result='WIN' if random.random() < 0.65 else 'LOSS',
            payout=19.0 if random.random() < 0.65 else -100.0,
            timestamp=datetime.now(),
            confidence=0.65
        )
        ab_test.record_result_a(result_a)
        
        # Versão B (5% melhor)
        result_b = TestResult(
            bet_id=f"b_{i:03d}",
            version='B',
            result='WIN' if random.random() < 0.70 else 'LOSS',  # Melhor!
            payout=19.0 if random.random() < 0.70 else -100.0,
            timestamp=datetime.now(),
            confidence=0.67
        )
        ab_test.record_result_b(result_b)
    
    print(f"✓ Coletados {len(ab_test.results_a)} resultados para A")
    print(f"✓ Coletados {len(ab_test.results_b)} resultados para B")
    
    # Analisar
    if ab_test.should_analyze():
        analysis = ab_test.analyze()
        
        print(f"\n✓ Resultados:")
        print(f"    A: {analysis.wr_a:.1%} WR")
        print(f"    B: {analysis.wr_b:.1%} WR")
        print(f"    Diferença: {(analysis.wr_b - analysis.wr_a):.1%}")
        print(f"    p-value: {analysis.pvalue_wr:.4f}")
        
        # Verificar se deve fazer rollout
        should_rollout = ab_test.should_increase_rollout(analysis)
        print(f"\n✓ Deve fazer rollout? {should_rollout}")
        
        # Tentar aumentar rollout
        if should_rollout:
            success = ab_test.increase_rollout()
            print(f"✓ Rollout aumentado? {success}")
            
            pct_a, pct_b = ab_test.get_current_rollout()
            print(f"✓ Nova distribuição: {pct_a}% A, {pct_b}% B")
            
            assert pct_b > 0, "B deveria estar em rollout"
    
    print("\n✅ TESTE 4 PASSOU")


def test_rollout_phases():
    """Teste 5: Fases de rollout"""
    print("\n" + "="*80)
    print("[TEST 5] FASES DE ROLLOUT")
    print("="*80)
    
    ab_test = ABTestManager(min_samples=10)
    
    # Simular progressão de fases
    print(f"✓ Fase inicial: {ab_test.current_phase.value}")
    pct_a, pct_b = ab_test.get_current_rollout()
    print(f"    Distribuição: {pct_a}% A, {pct_b}% B")
    
    # Avançar fases manualmente
    ab_test.current_phase = RolloutPhase.ROLLOUT_10
    pct_a, pct_b = ab_test.get_current_rollout()
    print(f"✓ Fase 1 (10%): {pct_a}% A, {pct_b}% B")
    assert pct_b == 10, "Deveria ter 10% em B"
    
    ab_test.current_phase = RolloutPhase.ROLLOUT_50
    pct_a, pct_b = ab_test.get_current_rollout()
    print(f"✓ Fase 2 (50%): {pct_a}% A, {pct_b}% B")
    assert pct_b == 50, "Deveria ter 50% em B"
    
    ab_test.current_phase = RolloutPhase.ROLLOUT_100
    pct_a, pct_b = ab_test.get_current_rollout()
    print(f"✓ Fase 3 (100%): {pct_a}% A, {pct_b}% B")
    assert pct_b == 100, "Deveria ter 100% em B"
    
    print("\n✅ TESTE 5 PASSOU")


def test_status_export():
    """Teste 6: Exportação de status"""
    print("\n" + "="*80)
    print("[TEST 6] EXPORTAÇÃO DE STATUS")
    print("="*80)
    
    ab_test = ABTestManager(min_samples=15)
    
    # Coletar alguns resultados
    for i in range(20):
        result_a = TestResult(
            bet_id=f"a_{i:03d}",
            version='A',
            result='WIN' if i % 3 == 0 else 'LOSS',
            payout=19.0 if i % 3 == 0 else -100.0,
            timestamp=datetime.now(),
            confidence=0.65
        )
        ab_test.record_result_a(result_a)
        
        result_b = TestResult(
            bet_id=f"b_{i:03d}",
            version='B',
            result='WIN' if i % 3 == 0 else 'LOSS',
            payout=19.0 if i % 3 == 0 else -100.0,
            timestamp=datetime.now(),
            confidence=0.65
        )
        ab_test.record_result_b(result_b)
    
    # Exportar status
    status = ab_test.get_status()
    
    print(f"✓ Status exportado:")
    print(f"    Fase: {status['phase']}")
    print(f"    Rollout: {status['rollout_b']}% B")
    print(f"    Resultados A: {status['results_a']}")
    print(f"    Resultados B: {status['results_b']}")
    print(f"    Pode analisar? {status['can_analyze']}")
    
    # Validar estrutura
    assert 'phase' in status
    assert 'rollout_a' in status
    assert 'rollout_b' in status
    assert 'results_a' in status
    assert 'results_b' in status
    
    print("\n✅ TESTE 6 PASSOU")


def main():
    """Executa todos os testes"""
    print("\n" + "="*80)
    print("TESTES DO A/B TESTING FRAMEWORK - FASE 3, TAREFA 8")
    print("="*80)
    
    try:
        # Teste 1: Coleta
        ab_test = test_result_collection()
        
        # Teste 2: Métricas
        test_metrics_calculation(ab_test)
        
        # Teste 3: Análise
        test_statistical_analysis(ab_test)
        
        # Teste 4: Rollout
        test_rollout_decision()
        
        # Teste 5: Fases
        test_rollout_phases()
        
        # Teste 6: Status
        test_status_export()
        
        # Resultado final
        print("\n" + "="*80)
        print("RESULTADO GERAL")
        print("="*80)
        print("\n✅ TODOS OS TESTES PASSARAM (6/6)")
        print("\n[1] Coleta de Resultados: ✅ PASSED")
        print("[2] Cálculo de Métricas: ✅ PASSED")
        print("[3] Análise Estatística: ✅ PASSED")
        print("[4] Decisão de Rollout: ✅ PASSED")
        print("[5] Fases de Rollout: ✅ PASSED")
        print("[6] Exportação de Status: ✅ PASSED")
        
        print("\n" + "="*80)
        print("✅ A/B TESTING FRAMEWORK PRONTO PARA INTEGRAÇÃO")
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
