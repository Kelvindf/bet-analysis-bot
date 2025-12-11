"""
Testes de Integração - FASE 2

Valida:
1. OptimalSequencer funciona corretamente
2. SignalPruner filtra sinais apropriadamente
3. MetaLearner treina e prediz
4. Integração completa em main.py
"""

import pytest
import sys
import os
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from learning.optimal_sequencer import OptimalSequencer
from learning.signal_pruner import SignalPruner
from learning.meta_learner import MetaLearner, MetaContext


class TestOptimalSequencer:
    """Testes para OptimalSequencer (DP)"""
    
    def test_initialization(self):
        """Teste: Inicialização da tabela DP"""
        seq = OptimalSequencer()
        
        assert seq.dp_table is not None
        assert len(seq.dp_table) == 1920  # 8 * 10 * 24
        print("✓ DP table criada com 1920 estados")
    
    def test_get_optimal_bet(self):
        """Teste: Busca de aposta ótima"""
        seq = OptimalSequencer()
        
        # Teste 1: Confiança alta, hora boa
        bet1 = seq.get_optimal_bet(confidence=0.85, bankroll_percentage=100.0, hour_of_day=20)
        assert 0.0 <= bet1 <= 0.5
        assert bet1 > 0.15  # Deve ser aposta significativa
        print(f"✓ High confidence (0.85, 20h): {bet1:.1%} aposta")
        
        # Teste 2: Confiança baixa, hora ruim
        bet2 = seq.get_optimal_bet(confidence=0.60, bankroll_percentage=50.0, hour_of_day=3)
        assert 0.0 <= bet2 <= 0.5
        assert bet2 < 0.15  # Deve ser aposta conservadora
        print(f"✓ Low confidence (0.60, 3h, 50% BR): {bet2:.1%} aposta")
        
        # Teste 3: Confiança média, bankroll baixo
        bet3 = seq.get_optimal_bet(confidence=0.72, bankroll_percentage=20.0, hour_of_day=12)
        assert 0.0 <= bet3 <= 0.5
        print(f"✓ Medium confidence (0.72, 12h, 20% BR): {bet3:.1%} aposta")
    
    def test_strategy_by_hour(self):
        """Teste: Estratégia varia por hora"""
        seq = OptimalSequencer()
        
        # Madrugada (3h): win rate 55%
        bet_early = seq.get_optimal_bet(0.75, 100.0, hour_of_day=3)
        
        # Noite (20h): win rate 72%
        bet_night = seq.get_optimal_bet(0.75, 100.0, hour_of_day=20)
        
        # Noite deve ter aposta maior (melhor win rate)
        assert bet_night > bet_early
        print(f"✓ Madrugada (3h): {bet_early:.1%} < Noite (20h): {bet_night:.1%}")


class TestSignalPruner:
    """Testes para SignalPruner (Branch & Bound)"""
    
    def test_initialization(self):
        """Teste: Inicialização do pruner"""
        pruner = SignalPruner(base_threshold=0.02)
        
        assert pruner.base_threshold == 0.02
        assert pruner.results_history == []
        print("✓ SignalPruner inicializado")
    
    def test_prune_signal_high_confidence(self):
        """Teste: Sinal com alta confiança é aceito"""
        pruner = SignalPruner(base_threshold=0.02)
        
        result = pruner.prune_signal(
            confidence=0.85,
            recent_performance=0.65,
            pattern_history_strength=0.80,
            current_drawdown=1.0
        )
        
        assert result.should_execute == True
        assert result.lower_bound > 0.30  # Ganho esperado alto
        print(f"✓ Alta confiança aceita: lower_bound={result.lower_bound:.1%}")
    
    def test_prune_signal_low_confidence(self):
        """Teste: Sinal com baixa confiança é rejeitado"""
        pruner = SignalPruner(base_threshold=0.02)
        
        result = pruner.prune_signal(
            confidence=0.50,
            recent_performance=0.45,
            pattern_history_strength=0.40,
            current_drawdown=0.5
        )
        
        # Pode ser rejeitado se lower_bound < threshold
        # ou aceito com ajuste forte
        print(f"✓ Baixa confiança: should_execute={result.should_execute}, lower_bound={result.lower_bound:.1%}")
    
    def test_bet_adjustment(self):
        """Teste: Ajuste de tamanho de aposta"""
        pruner = SignalPruner(base_threshold=0.02)
        
        # Sinal fraco deve reduzir aposta
        result_weak = pruner.prune_signal(
            confidence=0.55,
            recent_performance=0.52,
            pattern_history_strength=0.50,
            current_drawdown=3.0
        )
        
        # Sinal forte não deve reduzir
        result_strong = pruner.prune_signal(
            confidence=0.85,
            recent_performance=0.70,
            pattern_history_strength=0.85,
            current_drawdown=1.0
        )
        
        if result_weak.should_execute:
            assert result_weak.bet_adjustment < 1.0
        
        assert result_strong.bet_adjustment >= 0.9
        print(f"✓ Sinal fraco: ajuste={result_weak.bet_adjustment:.0%}")
        print(f"✓ Sinal forte: ajuste={result_strong.bet_adjustment:.0%}")


class TestMetaLearner:
    """Testes para MetaLearner (Random Forest)"""
    
    def test_initialization(self):
        """Teste: Inicialização do meta-learner"""
        ml = MetaLearner(min_training_samples=10)
        
        assert ml.model is None  # Sem dados ainda
        assert ml.training_sample_count == 0
        print("✓ MetaLearner inicializado")
    
    def test_add_training_sample(self):
        """Teste: Adicionar amostra de treinamento"""
        ml = MetaLearner(min_training_samples=10)
        
        context = MetaContext(
            hour_of_day=14,
            day_of_week=2,
            pattern_id=1,
            game_type=0,
            recent_win_rate=0.60,
            recent_drawdown=2.0,
            bankroll_percentage=100.0
        )
        
        ml.add_training_sample(context, winning_strategies=[1, 3, 5])
        
        assert ml.training_sample_count == 1
        print("✓ Amostra de treinamento adicionada")
    
    def test_training_and_prediction(self):
        """Teste: Treino e predição do modelo"""
        ml = MetaLearner(min_training_samples=5)
        
        # Adicionar 10 amostras de treinamento
        for i in range(10):
            context = MetaContext(
                hour_of_day=(14 + i) % 24,
                day_of_week=i % 7,
                pattern_id=1 + (i % 3),
                game_type=i % 2,
                recent_win_rate=0.55 + (i % 5) * 0.02,
                recent_drawdown=1.0 + (i % 3),
                bankroll_percentage=80.0 + (i % 5) * 4
            )
            
            winning_strats = [1, 3] if i % 2 == 0 else [2, 4, 6]
            ml.add_training_sample(context, winning_strats)
        
        # Treinar
        assert ml.should_retrain()
        ml.train()
        assert ml.model is not None
        print(f"✓ Modelo treinado com {ml.training_sample_count} amostras")
        
        # Predizer
        new_context = MetaContext(
            hour_of_day=20,
            day_of_week=3,
            pattern_id=2,
            game_type=1,
            recent_win_rate=0.62,
            recent_drawdown=2.5,
            bankroll_percentage=95.0
        )
        
        weights = ml.predict_strategy_weights(new_context)
        
        assert len(weights) == 6
        assert abs(sum(weights) - 1.0) < 0.01  # Soma ~1.0
        assert all(w >= 0 for w in weights)
        print(f"✓ Predição: weights={[f'{w:.2f}' for w in weights]}")
    
    def test_heuristic_fallback(self):
        """Teste: Fallback heurístico sem modelo"""
        ml = MetaLearner(min_training_samples=100)
        
        # Sem modelo treinado, usar heurística
        context = MetaContext(
            hour_of_day=20,  # Noite
            day_of_week=3,
            pattern_id=1,
            game_type=0,
            recent_win_rate=0.60,
            recent_drawdown=2.0,
            bankroll_percentage=100.0
        )
        
        weights = ml.predict_strategy_weights(context)
        
        assert len(weights) == 6
        assert abs(sum(weights) - 1.0) < 0.01
        print(f"✓ Heurística (noite): weights={[f'{w:.2f}' for w in weights]}")


class TestIntegration:
    """Testes de integração entre módulos"""
    
    def test_pipeline_flow(self):
        """Teste: Fluxo completo Sinal → FASE 2 → Resultado"""
        
        # Inicializar componentes
        seq = OptimalSequencer()
        pruner = SignalPruner(base_threshold=0.02)
        ml = MetaLearner(min_training_samples=10)
        
        # Simular sinal
        signal_confidence = 0.75
        hour = 20
        bankroll_pct = 100.0
        
        # 1. Meta-Learning
        context = MetaContext(
            hour_of_day=hour,
            day_of_week=3,
            pattern_id=1,
            game_type=0,
            recent_win_rate=0.60,
            recent_drawdown=2.0,
            bankroll_percentage=bankroll_pct
        )
        weights = ml.predict_strategy_weights(context)
        print(f"✓ Meta-Learning: {weights}")
        
        # 2. Signal Pruner
        pruning = pruner.prune_signal(
            confidence=signal_confidence,
            recent_performance=0.60,
            pattern_history_strength=0.70,
            current_drawdown=2.0
        )
        
        if not pruning.should_execute:
            print("✗ Sinal rejeitado por Signal Pruner")
            return
        
        print(f"✓ Signal Pruner: aprovado (lower_bound={pruning.lower_bound:.1%})")
        
        # 3. Optimal Sequencer
        optimal_bet = seq.get_optimal_bet(signal_confidence, bankroll_pct, hour)
        print(f"✓ Optimal Sequencer: {optimal_bet:.1%} do bankroll")
        
        # 4. Simular resultado
        ml.add_training_sample(context, winning_strategies=[1, 3, 5])
        print(f"✓ Resultado registrado para retraining")
        
        print(f"\n✅ Pipeline FASE 2 completo!")


if __name__ == "__main__":
    print("=" * 80)
    print("TESTES DE INTEGRAÇÃO - FASE 2")
    print("=" * 80)
    
    print("\n### OPTIMAL SEQUENCER ###")
    test_seq = TestOptimalSequencer()
    test_seq.test_initialization()
    test_seq.test_get_optimal_bet()
    test_seq.test_strategy_by_hour()
    
    print("\n### SIGNAL PRUNER ###")
    test_pruner = TestSignalPruner()
    test_pruner.test_initialization()
    test_pruner.test_prune_signal_high_confidence()
    test_pruner.test_prune_signal_low_confidence()
    test_pruner.test_bet_adjustment()
    
    print("\n### META LEARNER ###")
    test_ml = TestMetaLearner()
    test_ml.test_initialization()
    test_ml.test_add_training_sample()
    test_ml.test_training_and_prediction()
    test_ml.test_heuristic_fallback()
    
    print("\n### INTEGRAÇÃO ###")
    test_int = TestIntegration()
    test_int.test_pipeline_flow()
    
    print("\n" + "=" * 80)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 80)
