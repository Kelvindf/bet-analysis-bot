═══════════════════════════════════════════════════════════════════════════════════
                    GUIA DE INTEGRAÇÃO - FASE 1
               Early Stopping + Cache + Adaptive Optimizer
═══════════════════════════════════════════════════════════════════════════════════

Este documento contém instruções passo-a-passo para integrar as 3 otimizações da
Fase 1 no main.py e no pipeline de análise.

═══════════════════════════════════════════════════════════════════════════════════
PARTE 1: INTEGRAÇÃO DO DECISION CACHE
═══════════════════════════════════════════════════════════════════════════════════

OBJETIVO: Reutilizar decisões de sinais similares

PASSO 1: Adicionar imports no topo de src/main.py

Antes:
    from analysis.strategy_pipeline import StrategyPipeline
    
Depois:
    from analysis.strategy_pipeline import StrategyPipeline
    from learning.decision_cache import DecisionCache
    from learning.adaptive_optimizer import AdaptiveOptimizer

PASSO 2: Inicializar cache no __init__ de BlazeAnalyzerBot

Localizar em __init__:
    def __init__(self, test_mode: bool = False):
        self.logger = logging.getLogger(__name__)
        self.pipeline = StrategyPipeline()
        ...

Adicionar após self.pipeline:
    # Inicializar cache de decisões
    self.decision_cache = DecisionCache(max_entries=10000, ttl_minutes=60)
    
    # Inicializar otimizador de parâmetros
    self.param_optimizer = AdaptiveOptimizer(
        repo=None,  # Será setado depois
        base_confidence=0.75
    )
    
    self.logger.info("[MAIN] Cache de decisões inicializado")
    self.logger.info("[MAIN] Otimizador de parâmetros inicializado")

PASSO 3: Modificar process_signals() para usar cache

Localizar a função que processa sinais (usar grep: "def process_signals")

Exemplo do código ANTES:
    def process_signals(self, signals_data):
        signals = []
        for signal_data in signals_data:
            signal = self.pipeline.process_signal(signal_data)
            signals.append(signal)
        return signals

Mudança DEPOIS (adicionar cache check):
    def process_signals(self, signals_data):
        signals = []
        for signal_data in signals_data:
            game = signal_data.get('game', 'Unknown')
            pattern = signal_data.get('pattern', '')
            hour = datetime.now().hour
            
            # Verificar cache primeiro
            cached = self.decision_cache.get(
                game=game,
                pattern=pattern,
                hour=hour,
                trend=signal_data.get('trend', ''),
                game_type=signal_data.get('game_type', '')
            )
            
            if cached:
                # Cache hit - reutilizar resultado
                result, confidence, details = cached
                self.logger.debug(f"[CACHE HIT] {game}/{pattern} → {result}")
                # Criar objeto Signal com cache result
                # (você pode optimizar isso depois)
            else:
                # Cache miss - processar normalmente
                signal = self.pipeline.process_signal(signal_data)
                
                # Armazenar no cache para futuro
                if signal.is_valid:
                    self.decision_cache.set(
                        game=game,
                        pattern=pattern,
                        hour=hour,
                        result='PASS' if signal.is_valid else 'WEAK',
                        confidence=signal.final_confidence,
                        details=signal.strategy_details,
                        trend=signal_data.get('trend', ''),
                        game_type=signal_data.get('game_type', '')
                    )
            
            signals.append(signal)
        
        # Limpar cache expirado a cada 100 sinais
        if len(signals) % 100 == 0:
            expired = self.decision_cache.clear_expired()
            if expired > 0:
                self.logger.info(f"[CACHE] Removidas {expired} entradas expiradas")
        
        return signals

═══════════════════════════════════════════════════════════════════════════════════
PARTE 2: INTEGRAÇÃO DO ADAPTIVE OPTIMIZER
═══════════════════════════════════════════════════════════════════════════════════

OBJETIVO: Ajustar parâmetros automaticamente baseado em performance

PASSO 1: Setar repository no otimizador (em __init__)

Após inicializar self.param_optimizer:
    # Settar repository para que optimizer possa acessar dados
    if hasattr(self, 'result_repo'):
        self.param_optimizer.repo = self.result_repo
        self.logger.info("[OPTIMIZER] Repository conectado ao otimizador")

PASSO 2: Chamar optimize() no run_analysis_cycle()

Localizar run_analysis_cycle():
    def run_analysis_cycle(self):
        # ... código existente ...
        raw_data = self.collector.collect_game_data()
        signals = self.process_signals(raw_data)
        # ... mais código ...

Adicionar ANTES de process_signals:
    # Atualizar parâmetros adaptativos (a cada 100 sinais)
    if hasattr(self, 'signal_count'):
        self.signal_count += 1
    else:
        self.signal_count = 1
    
    if self.signal_count % 100 == 0:
        try:
            updates = self.param_optimizer.optimize('Double', hours_lookback=24)
            self.logger.info(f"[OPTIMIZER] Parâmetros atualizados: {updates}")
            
            # Atualizar thresholds no pipeline
            # TODO: Implementar setters no pipeline para usar novo min_confidence
            
        except Exception as e:
            self.logger.error(f"[OPTIMIZER] Erro ao otimizar: {e}")

Adicionar APÓS process_signals:
    # A cada ciclo, registrar estatísticas de otimização
    if self.signal_count % 500 == 0:
        self.param_optimizer.print_history(last_n=5)
        self.decision_cache.print_stats()

═══════════════════════════════════════════════════════════════════════════════════
PARTE 3: VALIDAÇÃO E TESTES
═══════════════════════════════════════════════════════════════════════════════════

TESTE 1: Validar que Early Stopping está funcionando

Arquivo: src/analysis/strategy_pipeline.py
Verificar: Logs contêm "[EARLY STOP]"

Código para debug:
    from src.analysis.strategy_pipeline import StrategyPipeline
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    pipeline = StrategyPipeline()
    
    # Simular sinal que passa em 4 estratégias
    signal_data = {
        'signal_id': 'test_001',
        'signal_type': 'Vermelho',
        'initial_confidence': 0.75,
        'recent_colors': ['vermelho'] * 10 + ['preto'] * 5,
        'all_colors': ['vermelho'] * 100 + ['preto'] * 50,
        'prices': [100, 105, 110, 115, 120],
        'timestamp': datetime.now()
    }
    
    signal = pipeline.process_signal(signal_data)
    print(f"Sinal válido: {signal.is_valid}")
    print(f"Estratégias passaram: {signal.strategies_passed}")
    # Procurar por "[EARLY STOP]" nos logs

TESTE 2: Validar que Decision Cache está funcionando

Código para debug:
    from src.learning.decision_cache import DecisionCache
    
    cache = DecisionCache(ttl_minutes=60)
    
    # Primeiro acesso = MISS
    result1 = cache.get('Double', 'VermelhoPorSaida', 19)
    print(f"Primeiro acesso: {result1}")  # Deve ser None
    
    # Armazenar no cache
    cache.set('Double', 'VermelhoPorSaida', 19, 'PASS', 0.85)
    
    # Segundo acesso = HIT
    result2 = cache.get('Double', 'VermelhoPorSaida', 19)
    print(f"Segundo acesso: {result2}")  # Deve ser tuple
    
    # Ver estatísticas
    cache.print_stats()
    # Esperado: hit_rate = 50% (1 hit em 2 requisições)

TESTE 3: Validar que Adaptive Optimizer está funcionando

Código para debug:
    from src.learning.adaptive_optimizer import AdaptiveOptimizer
    
    optimizer = AdaptiveOptimizer(base_confidence=0.75)
    
    # Teste 1: Win rate baixo (40%)
    optimizer._adjust_confidence_threshold(0.40)
    print(f"WR=40% → min_confidence = {optimizer.min_confidence:.2f}")
    
    # Deve ser < 0.75 (mais permissivo)
    assert optimizer.min_confidence < 0.75
    
    # Teste 2: Win rate alto (75%)
    optimizer2 = AdaptiveOptimizer(base_confidence=0.75)
    optimizer2._adjust_confidence_threshold(0.75)
    print(f"WR=75% → min_confidence = {optimizer2.min_confidence:.2f}")
    
    # Deve ser > 0.75 (mais seletivo)
    assert optimizer2.min_confidence > 0.75
    
    optimizer.print_current_params()

═══════════════════════════════════════════════════════════════════════════════════
PARTE 4: MONITORAMENTO E MÉTRICAS
═══════════════════════════════════════════════════════════════════════════════════

ADICIONAR ao run_analysis_cycle() ou em novo método monitor_optimizations():

    def monitor_optimizations(self):
        """Monitora performance das otimizações"""
        stats = {
            'cache': self.decision_cache.get_stats(),
            'optimizer': self.param_optimizer._get_current_params(),
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"[MONITOR] Cache hit rate: {stats['cache']['hit_rate_pct']:.1f}%")
        self.logger.info(f"[MONITOR] Min confidence: {stats['optimizer']['min_confidence']:.2%}")
        self.logger.info(f"[MONITOR] Kelly multiplier: {stats['optimizer']['kelly_multiplier']:.2f}x")
        
        return stats

Chamar a cada ciclo:
    stats = self.monitor_optimizations()

═══════════════════════════════════════════════════════════════════════════════════
PARTE 5: PRÓXIMOS PASSOS
═══════════════════════════════════════════════════════════════════════════════════

DEPOIS DE INTEGRAR FASE 1:

1. Testar durante 24 horas com dados reais
2. Validar ganhos estimados vs ganhos reais
3. Ajustar sensibilidades se necessário
4. Ir para FASE 2 (DP + Branch & Bound + Meta-Learning)

MÉTRICAS A ACOMPANHAR:
├─ Cache hit rate (target: 15-20%)
├─ Min confidence (deve variar 60-90%)
├─ Kelly multiplier (deve variar 0.5-2.0)
├─ Win rate (deve aumentar +8-12%)
└─ Lucro mensal (deve aumentar +8-14%)

═══════════════════════════════════════════════════════════════════════════════════
CHECKLIST DE INTEGRAÇÃO
═══════════════════════════════════════════════════════════════════════════════════

[ ] Adicionar imports (DecisionCache, AdaptiveOptimizer)
[ ] Inicializar self.decision_cache em __init__
[ ] Inicializar self.param_optimizer em __init__
[ ] Modificar process_signals() para usar cache.get()
[ ] Adicionar cache.set() após process_signal()
[ ] Chamar cache.clear_expired() a cada 100 sinais
[ ] Adicionar self.param_optimizer.repo = self.result_repo
[ ] Chamar self.param_optimizer.optimize() a cada 100 sinais
[ ] Adicionar monitor_optimizations() para logs
[ ] Testar cada componente individualmente
[ ] Testar fluxo completo
[ ] Validar ganhos
[ ] Documentar resultados
[ ] Passar para FASE 2

═══════════════════════════════════════════════════════════════════════════════════
CÓDIGO COMPLETO - EXEMPLO DE INTEGRAÇÃO
═══════════════════════════════════════════════════════════════════════════════════

(Localizado no arquivo src/main.py após linhas 60-120)

```python
from learning.decision_cache import DecisionCache
from learning.adaptive_optimizer import AdaptiveOptimizer

class BlazeAnalyzerBot:
    def __init__(self, test_mode: bool = False):
        self.logger = logging.getLogger(__name__)
        self.pipeline = StrategyPipeline()
        
        # FASE 1: Cache + Optimizer
        self.decision_cache = DecisionCache(max_entries=10000, ttl_minutes=60)
        self.param_optimizer = AdaptiveOptimizer(base_confidence=0.75)
        self.signal_count = 0
        
        # ... resto do __init__ ...
        
    def run_analysis_cycle(self):
        # Incrementar contador de sinais
        self.signal_count += 1
        
        # Coletar dados
        raw_data = self.collector.collect_game_data()
        
        # FASE 1: Otimizar parâmetros
        if self.signal_count % 100 == 0:
            try:
                updates = self.param_optimizer.optimize('Double', hours_lookback=24)
                self.logger.info(f"[PHASE1] Parâmetros: conf={updates['min_confidence']:.2f}, "
                               f"kelly={updates['kelly_multiplier']:.2f}")
            except Exception as e:
                self.logger.error(f"[PHASE1] Erro: {e}")
        
        # Processar sinais com cache
        signals = self.process_signals_with_cache(raw_data)
        
        # ... resto da função ...
    
    def process_signals_with_cache(self, signals_data):
        """Processa sinais com cache de decisões"""
        signals = []
        
        for signal_data in signals_data:
            game = signal_data.get('game', 'Unknown')
            pattern = signal_data.get('pattern', '')
            hour = datetime.now().hour
            
            # Verificar cache
            cached = self.decision_cache.get(game, pattern, hour)
            
            if cached:
                self.logger.debug(f"[CACHE HIT] {game}/{pattern}")
                # TODO: Criar Signal object de cache hit
            else:
                # Processar normalmente
                signal = self.pipeline.process_signal(signal_data)
                
                # Armazenar em cache
                if signal.is_valid:
                    self.decision_cache.set(
                        game, pattern, hour,
                        'PASS', signal.final_confidence,
                        signal.strategy_details
                    )
                
                signals.append(signal)
        
        # Limpar expirados
        if self.signal_count % 100 == 0:
            self.decision_cache.clear_expired()
            self.decision_cache.print_stats()
        
        return signals
```

═══════════════════════════════════════════════════════════════════════════════════
FIM DO GUIA DE INTEGRAÇÃO
═══════════════════════════════════════════════════════════════════════════════════
