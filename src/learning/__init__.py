"""
Learning Module - Sistema de Aprendizado Contínuo

Componentes:
- decision_cache: Memoização de decisões similares
- adaptive_optimizer: Otimizador de parâmetros dinâmicos
- optimal_sequencer: Programação dinâmica para sequências
- signal_pruner: Branch & Bound para filtro de sinais
- meta_learner: Meta-Learning para seleção de estratégia
- feedback_loop: Integração de feedback automático
- ab_tester: Framework para A/B Testing
- live_optimizer: Dashboard em tempo real
"""

from .decision_cache import DecisionCache
from .adaptive_optimizer import AdaptiveOptimizer

__all__ = [
    'DecisionCache',
    'AdaptiveOptimizer',
]
