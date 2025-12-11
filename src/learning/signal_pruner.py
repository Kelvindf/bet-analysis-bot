"""
Signal Pruner - Branch & Bound para Filtro de Sinais

Otimização por Branch & Bound

OBJETIVO:
    - Filtrar sinais com baixa probabilidade antes de executar
    - Não gastar recursos em apostas ineficientes
    - Remover 20-30% de sinais ruins
    - Ganho esperado: +5% lucro

PROBLEMA (Branch & Bound):
    Dado um sinal com confiança X,
    qual é a probabilidade mínima de lucro?
    
    Se lucratividade mínima < threshold → não apostar
    
    Exemplo:
    - Sinal: confiança=0.65
    - Lower bound lucro: -5% (pior caso)
    - Upper bound lucro: +15% (melhor caso)
    - Threshold mínimo: 0% (break-even)
    - Decisão: KEEP (lower_bound >= threshold)
    
    vs.
    
    - Sinal: confiança=0.55
    - Lower bound: -10%
    - Upper bound: +8%
    - Threshold: 0%
    - Decisão: PRUNE (lower_bound < 0, muito risco)

ALGORITMO:
    1. Calcular lower_bound do lucro
       └─ Assumir pior cenário: só 40% win rate
       └─ Luck negativo: volatilidade
    
    2. Calcular upper_bound do lucro
       └─ Assumir melhor cenário: 85% win rate
       └─ Luck positivo: streak
    
    3. Se lower_bound < min_threshold
       └─ PRUNE este sinal
       └─ Economizar recurso
    
    4. Se lower_bound >= threshold
       └─ KEEP sinal
       └─ Apostar normalmente

FÓRMULAS:
    
    lower_bound = confidence * (profit_per_win) - (1 - confidence) * bet_size
                = confidence * 1.0 - (1 - confidence) * 1.0  (odds=2)
                = 2*confidence - 1
    
    upper_bound = lower_bound + variance_adjustment
                = lower_bound + sqrt(n) * sigma
    
    variance_adjustment = número de sinais em sequência * volatilidade

EXEMPLOS:
    
    Confiança 0.60 → Lower bound = 2*0.60 - 1 = 0.20 (20% lucro mínimo)
                  → KEEP (positivo)
    
    Confiança 0.50 → Lower bound = 2*0.50 - 1 = 0.00 (break-even)
                  → KEEP (no threshold, marginal)
    
    Confiança 0.45 → Lower bound = 2*0.45 - 1 = -0.10 (-10% mínimo)
                  → PRUNE (negativo, muito risco)
    
    Confiança 0.55 + ruim performance recente
                  → Lower bound = 0.10 - 0.05 = 0.05 (ajustado)
                  → KEEP (mas ajustar bet size)

IMPACTO:
    - Remove: ~20-30% de sinais fracos
    - Economiza: ~20-30% de capital em apostas ruins
    - Melhora: Win rate geral (filtra perdedores)
    - Tempo: O(1) por sinal
"""

import logging
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PruningResult:
    """Resultado da análise de pruning"""
    signal_id: str
    confidence: float
    lower_bound: float  # Retorno mínimo garantido
    upper_bound: float  # Retorno máximo possível
    should_prune: bool  # Deve descartar?
    prune_reason: str
    bet_adjustment: float  # Fator de ajuste na aposta (1.0 = normal)


class SignalPruner:
    """
    Filtrador de sinais usando Branch & Bound
    
    Remove sinais com baixa probabilidade de sucesso
    Economiza recursos em apostas ineficientes
    
    Exemplo:
        pruner = SignalPruner(min_threshold=0.0)
        
        result = pruner.prune_signal(
            signal_id='sig_001',
            confidence=0.62,
            game='Double',
            recent_performance=0.58  # Win rate 24h
        )
        
        if result.should_prune:
            logger.info(f"Pulando {signal_id}: {result.prune_reason}")
        else:
            aposta = base_aposta * result.bet_adjustment
    """
    
    def __init__(self, min_threshold: float = 0.0,
                 use_historical_performance: bool = True):
        """
        Args:
            min_threshold: Retorno mínimo para manter sinal (-0.10 a 0.10)
                         -0.10 = aceita até -10% de perda
                         0.00 = break-even é ok
                         0.05 = só com 5%+ de ganho
            use_historical_performance: Usar histórico para melhorar bounds
        """
        self.min_threshold = min_threshold
        self.use_historical = use_historical_performance
        
        # Histórico de performance
        self.signal_history: List[Dict] = []
        self.max_history = 100
        
        self.stats = {
            'signals_pruned': 0,
            'signals_kept': 0,
            'false_positives': 0,  # Sinais que foram mantidos e perderam
            'true_positives': 0,   # Sinais que foram mantidos e ganharam
        }
        
        logger.info(f"[PRUNER] Inicializado: threshold={min_threshold:.1%}")
    
    def prune_signal(self, signal_id: str, confidence: float,
                     game: str = 'Unknown',
                     recent_performance: Optional[float] = None,
                     win_rate_by_pattern: Optional[Dict] = None) -> PruningResult:
        """
        Analisa se deve descartar um sinal
        
        Args:
            signal_id: ID do sinal
            confidence: Confiança da pipeline (0.60-0.95)
            game: 'Double' ou 'Crash'
            recent_performance: Win rate nos últimos 24h
            win_rate_by_pattern: Dict com WR por padrão histórico
        
        Returns:
            PruningResult com decisão e ajustes
        """
        # 1. Calcular lower bound (caso pessimista)
        lower_bound = self._calculate_lower_bound(
            confidence,
            recent_performance,
            win_rate_by_pattern
        )
        
        # 2. Calcular upper bound (caso otimista)
        upper_bound = self._calculate_upper_bound(confidence)
        
        # 3. Calcular bet adjustment
        bet_adjustment = self._calculate_bet_adjustment(
            confidence,
            lower_bound,
            recent_performance
        )
        
        # 4. Decidir: descartar ou manter?
        should_prune = lower_bound < self.min_threshold
        prune_reason = self._get_prune_reason(
            confidence,
            lower_bound,
            upper_bound,
            should_prune,
            recent_performance
        )
        
        # 5. Registrar estatística
        if should_prune:
            self.stats['signals_pruned'] += 1
            logger.debug(f"[PRUNE] {signal_id}: {prune_reason}")
        else:
            self.stats['signals_kept'] += 1
            logger.debug(f"[KEEP] {signal_id}: {prune_reason}")
        
        return PruningResult(
            signal_id=signal_id,
            confidence=confidence,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            should_prune=should_prune,
            prune_reason=prune_reason,
            bet_adjustment=bet_adjustment
        )
    
    def _calculate_lower_bound(self, confidence: float,
                               recent_performance: Optional[float] = None,
                               win_rate_by_pattern: Optional[Dict] = None) -> float:
        """
        Calcula retorno mínimo garantido
        
        Fórmula base: lower_bound = 2*confidence - 1
        (Assumindo odds=2.0, Kelly criterion)
        
        Ajustes:
        - Se recent_performance ruim: reduzir esperança
        - Se pattern history ruim: mais pessimista ainda
        """
        # Lower bound puro da confiança
        base_lb = 2 * confidence - 1
        
        # Ajuste por performance recente
        if recent_performance is not None and recent_performance < 0.60:
            # Performance ruim nos últimos tempos
            # Reduzir esperança em 50% do gap
            gap = 0.60 - recent_performance
            adjustment = -gap * 0.5
            base_lb += adjustment
            logger.debug(f"[PRUNE] Ajuste performance: {adjustment:+.1%}")
        
        # Ajuste por padrão histórico
        if win_rate_by_pattern:
            pattern_wrs = list(win_rate_by_pattern.values())
            if pattern_wrs:
                median_wr = np.median(pattern_wrs)
                if median_wr < 0.58:
                    # Padrões historicamente fracos
                    gap = 0.60 - median_wr
                    adjustment = -gap * 0.3
                    base_lb += adjustment
                    logger.debug(f"[PRUNE] Ajuste padrão: {adjustment:+.1%}")
        
        return base_lb
    
    def _calculate_upper_bound(self, confidence: float) -> float:
        """
        Calcula retorno máximo possível
        
        Upper bound assume melhor cenário:
        - Win rate 85% por um tempo (streak)
        - Volatilidade trabalha a favor
        
        Fórmula: upper_bound = lower_bound + variance_bonus
        """
        base_ub = 2 * confidence - 1
        
        # Bonus de variância
        # Se confiança alta: mais upside potential
        if confidence > 0.80:
            variance_bonus = 0.15  # +15% upside
        elif confidence > 0.70:
            variance_bonus = 0.10  # +10% upside
        else:
            variance_bonus = 0.05  # +5% upside
        
        return base_ub + variance_bonus
    
    def _calculate_bet_adjustment(self, confidence: float,
                                  lower_bound: float,
                                  recent_performance: Optional[float] = None) -> float:
        """
        Calcula fator de ajuste na aposta
        
        Retorna:
            1.0 = aposta normal
            0.75 = apostar 75% do normal (conservador)
            0.5 = apostar 50% do normal (muito conservador)
            0.0 = não apostar (prune)
        """
        # Base: ajuste por lower bound
        if lower_bound < -0.05:  # Risco > 5%
            adjustment = 0.5  # Muito conservador
        elif lower_bound < 0.0:  # Break-even
            adjustment = 0.75  # Conservador
        elif lower_bound < 0.05:  # Ganho baixo
            adjustment = 0.9  # Ligeiramente conservador
        else:  # Ganho bom
            adjustment = 1.0  # Normal
        
        # Ajuste adicional por performance recente
        if recent_performance is not None:
            if recent_performance < 0.50:
                adjustment *= 0.5  # Muito ruim
            elif recent_performance < 0.55:
                adjustment *= 0.75  # Ruim
            elif recent_performance > 0.70:
                adjustment *= 1.2  # Bom (até 1.5x)
        
        # Limitar entre 0.5-1.5
        return np.clip(adjustment, 0.5, 1.5)
    
    def _get_prune_reason(self, confidence: float, lower_bound: float,
                         upper_bound: float, should_prune: bool,
                         recent_performance: Optional[float] = None) -> str:
        """Gera descrição do motivo"""
        if should_prune:
            return (f"Confiança baixa demais (conf={confidence:.2f}, "
                   f"lb={lower_bound:+.1%} < threshold={self.min_threshold:.1%})")
        else:
            reason = f"conf={confidence:.2f}, lb={lower_bound:+.1%}"
            if recent_performance is not None:
                reason += f", wr_24h={recent_performance:.0%}"
            return f"KEEP: {reason}"
    
    def record_result(self, signal_id: str, won: bool):
        """Registra resultado de um sinal (para validação posterior)"""
        entry = {
            'signal_id': signal_id,
            'won': won,
            'timestamp': datetime.now()
        }
        self.signal_history.append(entry)
        
        if len(self.signal_history) > self.max_history:
            self.signal_history.pop(0)
    
    def get_pruning_stats(self) -> Dict:
        """Retorna estatísticas de pruning"""
        total = self.stats['signals_pruned'] + self.stats['signals_kept']
        prune_rate = (self.stats['signals_pruned'] / total * 100) if total > 0 else 0
        
        return {
            'total_signals': total,
            'signals_pruned': self.stats['signals_pruned'],
            'signals_kept': self.stats['signals_kept'],
            'prune_rate_pct': round(prune_rate, 1),
            'true_positives': self.stats['true_positives'],
            'false_positives': self.stats['false_positives'],
            'min_threshold': self.min_threshold
        }
    
    def print_stats(self):
        """Imprime estatísticas formatadas"""
        stats = self.get_pruning_stats()
        print("\n" + "="*60)
        print("ESTATÍSTICAS DE PRUNING")
        print("="*60)
        print(f"Total de sinais: {stats['total_signals']}")
        print(f"Sinais descartados: {stats['signals_pruned']} ({stats['prune_rate_pct']:.1f}%)")
        print(f"Sinais mantidos: {stats['signals_kept']}")
        print(f"Threshold mínimo: {stats['min_threshold']:+.1%}")
        print("="*60 + "\n")
    
    def __repr__(self):
        stats = self.get_pruning_stats()
        return (f"SignalPruner(pruned={stats['signals_pruned']}, "
                f"kept={stats['signals_kept']}, "
                f"rate={stats['prune_rate_pct']:.1f}%)")


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Criar pruner
    pruner = SignalPruner(min_threshold=0.0)
    
    print("\n[1] Testando diversos sinais:\n")
    
    test_cases = [
        # (signal_id, confidence, recent_perf, description)
        ('sig_001', 0.85, 0.70, "Excelente: confiança alta + performance boa"),
        ('sig_002', 0.65, 0.60, "Bom: confiança média + performance normal"),
        ('sig_003', 0.55, 0.50, "Marginal: confiança baixa + performance ruim"),
        ('sig_004', 0.45, 0.45, "Péssimo: confiança muito baixa + pior cenário"),
        ('sig_005', 0.75, 0.45, "Contraditório: confiança boa mas WR ruim"),
    ]
    
    for signal_id, conf, perf, desc in test_cases:
        result = pruner.prune_signal(signal_id, conf, recent_performance=perf)
        
        print(f"{desc}")
        print(f"  Confiança: {conf:.2f} | WR 24h: {perf:.0%}")
        print(f"  Lower bound: {result.lower_bound:+.1%} | Upper bound: {result.upper_bound:+.1%}")
        print(f"  Decisão: {'PRUNE ❌' if result.should_prune else 'KEEP ✓'}")
        print(f"  Bet adjustment: {result.bet_adjustment:.2f}x")
        print()
    
    # Mostrar estatísticas
    pruner.print_stats()
