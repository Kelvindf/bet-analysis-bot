#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Teste Rápido FASE 2 - Validação dos 3 Módulos
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 80)
print("TESTE RAPIDO FASE 2 - Validacao de Integracao")
print("=" * 80)

# Teste 1: OptimalSequencer
print("\n[1/3] Testando OptimalSequencer...")
try:
    from learning.optimal_sequencer import OptimalSequencer
    seq = OptimalSequencer()
    
    bet1 = seq.get_optimal_bet(0.85, 100.0, 20)
    bet2 = seq.get_optimal_bet(0.60, 50.0, 3)
    
    assert 0.0 <= bet1 <= 0.5
    assert 0.0 <= bet2 <= 0.5
    assert bet1 > bet2  # High confidence > Low confidence
    
    print(f"   [OK] DP Table: {len(seq.dp_table)} estados")
    print(f"   [OK] Alta confianca (0.85, 20h): {bet1:.1%}")
    print(f"   [OK] Baixa confianca (0.60, 3h): {bet2:.1%}")
    print("   [OK] OptimalSequencer OK")
except Exception as e:
    print(f"   [ERRO]: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Teste 2: SignalPruner
print("\n[2/3] Testando SignalPruner...")
try:
    from learning.signal_pruner import SignalPruner
    pruner = SignalPruner(min_threshold=0.02)
    
    result1 = pruner.prune_signal('sig_001', 0.85, 'Double', 0.65)
    result2 = pruner.prune_signal('sig_002', 0.50, 'Double', 0.45)
    
    assert result1.should_prune == False
    assert hasattr(result1, 'lower_bound')
    assert hasattr(result1, 'bet_adjustment')
    
    print(f"   [OK] Alta confianca: should_prune={result1.should_prune}")
    print(f"   [OK] Lower bound: {result1.lower_bound:.1%}")
    print(f"   [OK] Bet adjustment: {result1.bet_adjustment:.0%}")
    print("   [OK] SignalPruner OK")
except Exception as e:
    print(f"   [ERRO]: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Teste 3: MetaLearner
print("\n[3/3] Testando MetaLearner...")
try:
    from learning.meta_learner import MetaLearner, MetaContext
    ml = MetaLearner()
    
    # Teste heurística (sem treinamento)
    context = MetaContext(
        timestamp=None,
        hour_of_day=20,
        day_of_week=3,
        pattern_id=1,
        game_type='Double',
        recent_wr=0.60,
        recent_drawdown=2.0,
        bankroll_pct=100
    )
    
    weights = ml.predict_strategy_weights(context)
    
    assert len(weights) == 6
    assert abs(sum(weights) - 1.0) < 0.01
    assert all(w >= 0 for w in weights)
    
    print(f"   [OK] MetaContext criado")
    print(f"   [OK] Heuristica (noite): {[f'{w:.2f}' for w in weights]}")
    print(f"   [OK] Soma dos pesos: {sum(weights):.4f}")
    print("   [OK] MetaLearner OK")
except Exception as e:
    print(f"   [ERRO]: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Teste 4: Verificar integração em main.py
print("\n[4/4] Verificando integracao em main.py...")
try:
    with open(os.path.join(os.path.dirname(__file__), 'src', 'main.py'), 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('OptimalSequencer', 'from learning.optimal_sequencer import OptimalSequencer' in content),
        ('SignalPruner', 'from learning.signal_pruner import SignalPruner' in content),
        ('MetaLearner', 'from learning.meta_learner import MetaLearner' in content),
        ('self.optimal_sequencer', 'self.optimal_sequencer = OptimalSequencer()' in content),
        ('self.signal_pruner', 'self.signal_pruner = SignalPruner' in content),
        ('self.meta_learner', 'self.meta_learner = MetaLearner' in content),
        ('_apply_fase2_optimizations', 'def _apply_fase2_optimizations' in content),
        ('_collect_training_data', 'def _collect_training_data_for_meta_learner' in content),
    ]
    
    all_ok = True
    for name, check in checks:
        status = "[OK]" if check else "[ERRO]"
        print(f"   {status} {name}")
        if not check:
            all_ok = False
    
    if all_ok:
        print("   [OK] Integracao em main.py OK")
    else:
        print("   [ERRO] Integracao incompleta")
        sys.exit(1)
        
except Exception as e:
    print(f"   [ERRO]: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("[OK] TODOS OS TESTES PASSARAM!")
print("=" * 80)
print("\nResumo da Integracao FASE 2:")
print("  . OptimalSequencer (DP): Calcula tamanho otimo de aposta")
print("  . SignalPruner (B&B): Filtra sinais ineficientes")
print("  . MetaLearner (ML): Seleciona estrategias por contexto")
print("\nProximos passos:")
print("  1. Testar com dados reais do sistema")
print("  2. Validar ganhos esperados vs reais")
print("  3. Implementar Tarefa 7-9 (Feedback Loop, A/B Testing, Dashboard)")
print("=" * 80)
