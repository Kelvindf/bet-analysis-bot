═══════════════════════════════════════════════════════════════════════════════════
                    ARQUITETURA DO SISTEMA - FASES 1-3
                    Sistema de Aprendizado Contínuo & Otimização
═══════════════════════════════════════════════════════════════════════════════════

VISÃO GERAL - FLUXO DE DADOS COMPLETO

═══════════════════════════════════════════════════════════════════════════════════
FASE ATUAL (BASELINE + FASE 1)
═══════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                           SISTEMA DE SINAIS v1.0                               │
│                     (Baseline + Fase 1 Otimizações)                            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────┐
                                    │ Coleta de   │
                                    │ Dados (API) │
                                    └──────┬──────┘
                                           │
                                           ▼
                        ╔══════════════════════════════════════╗
                        ║    Decision Cache (FASE 1)           ║
                        ║   ├─ Check: Hash(game+pattern+hour) ║
                        ║   ├─ Hit → Return cached result     ║
                        ║   └─ Miss → Continue to pipeline    ║
                        ╚════════════┬═════════════════════════╝
                                     │
                                     ▼
                        ┌────────────────────────────┐
                        │   Strategy Pipeline        │
                        ├────────────────────────────┤
                        │ 1. Pattern Detection       │
                        │ 2. Technical Validation    │
                        │ 3. Confidence Filter       │
                        │ 4. Confirmation Filter     │
                        │ 5. Monte Carlo Validation  │
                        │ 6. Run Test Validation     │
                        │                            │
                        │ + Early Stopping (FASE 1)  │
                        │   └─ Stop if 4/6 passed    │
                        └────────────┬───────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────┐
                        │  Signal Validation         │
                        │  ├─ Final Confidence       │
                        │  ├─ Is Valid? (bool)       │
                        │  └─ Strategies Passed      │
                        └────────────┬───────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
        ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
        │ Telegram Send    │ │ Save Signal  │ │ Update Cache     │
        │ (Notificação)    │ │ (Database)   │ │ (Memoization)    │
        └──────────────────┘ └──────────────┘ └──────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────┐
                        │  Game Result (Real)        │
                        │  ├─ Vitória/Derrota?       │
                        │  ├─ Preço Final            │
                        │  └─ Multiplicador          │
                        └────────────┬───────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────┐
                        │  Adaptive Optimizer        │
                        │  (FASE 1)                  │
                        ├────────────────────────────┤
                        │ 1. Calcula win_rate (24h)  │
                        │ 2. Ajusta min_confidence   │
                        │ 3. Ajusta kelly_multiplier │
                        │ 4. Registra histórico      │
                        └────────────┬───────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────┐
                        │  Parametros Atualizados    │
                        │  (Para próximo sinal)      │
                        └────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════
PRÓXIMA FASE (FASE 2) - ARQUITETURA EXPANDIDA
═══════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                        SISTEMA INTELIGENTE v2.0                                │
│               (Baseline + Fase 1 + Fase 2 Otimizações)                         │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────┐
                                    │ Coleta de   │
                                    │ Dados (API) │
                                    └──────┬──────┘
                                           │
                                           ▼
                        ╔══════════════════════════════════════╗
                        ║    Decision Cache (FASE 1)           ║
                        ║    (Hit rate 15-20%)                 ║
                        ╚════════════┬═════════════════════════╝
                                     │
                                     ▼
                        ╔══════════════════════════════════════╗
                        ║  Meta-Learner (FASE 2)               ║
                        ║  ├─ Qual estratégia usar agora?      ║
                        ║  ├─ Features: hora, dia, padrão      ║
                        ║  └─ Modelo: Random Forest            ║
                        ╚════════════┬═════════════════════════╝
                                     │
                                     ▼
                        ┌────────────────────────────┐
                        │   Strategy Pipeline        │
                        │   (Weighted by Meta-Learn) │
                        ├────────────────────────────┤
                        │ 1. Pattern Detection (w=?) │
                        │ 2. Technical Validation    │
                        │ 3. Confidence Filter       │
                        │ 4. Confirmation Filter     │
                        │ 5. Monte Carlo (w=?)       │
                        │ 6. Run Test (w=?)          │
                        │                            │
                        │ + Early Stopping (FASE 1)  │
                        └────────────┬───────────────┘
                                     │
                                     ▼
                        ╔══════════════════════════════════════╗
                        ║  Branch & Bound (FASE 2)             ║
                        ║  ├─ Calcula bounds de lucro          ║
                        ║  ├─ Prune se < threshold             ║
                        ║  └─ Remove 20-30% sinais ruins       ║
                        ╚════════════┬═════════════════════════╝
                                     │
                                     ▼
                        ╔══════════════════════════════════════╗
                        ║  DP Optimal Sequencer (FASE 2)       ║
                        ║  ├─ State: (conf, bankroll%, hour)   ║
                        ║  ├─ DP Table: 10x10x24 = 2400 estados║
                        ║  └─ Retorna: aposta ótima            ║
                        ╚════════════┬═════════════════════════╝
                                     │
                                     ▼
                        ┌────────────────────────────┐
                        │  Adaptive Optimizer        │
                        │  (FASE 1)                  │
                        │  ├─ Min confidence        │
                        │  ├─ Kelly multiplier      │
                        │  └─ Strategy weights      │
                        └────────────┬───────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
        ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
        │ Telegram Send    │ │ Save Signal  │ │ Update Cache     │
        │ (Notificação)    │ │ (Database)   │ │ (Memoization)    │
        └──────────────────┘ └──────────────┘ └──────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────┐
                        │  Game Result (Real)        │
                        └────────────┬───────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────┐
                        │  Feedback Loop (FASE 3)    │
                        │  ├─ Detecta resultado      │
                        │  ├─ Atualiza histórico     │
                        │  ├─ Retreina Meta-Learner  │
                        │  └─ Ajusta parâmetros      │
                        └────────────┬───────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────┐
                        │  Parâmetros Ótimos         │
                        │  (Para próximo sinal)      │
                        └────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════
FASE 3 - ARQUITETURA COMPLETA (COM FEEDBACK LOOP)
═══════════════════════════════════════════════════════════════════════════════════

                           ┌────────────────────────┐
                           │    Coleta de Dados     │
                           └────────────┬───────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
          ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
          │ Decision Cache   │ │ Meta-Learner     │ │ A/B Testing      │
          │ (FASE 1)         │ │ (FASE 2)         │ │ (FASE 3)         │
          │ Hit: 15-20%      │ │ Accuracy: 70%+   │ │ Version A/B      │
          └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
                   │                    │                    │
                   └────────────────────┼────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────┐
                 │ Strategy Pipeline + Optimizations        │
                 ├──────────────────────────────────────────┤
                 │ ├─ Early Stopping (FASE 1)               │
                 │ ├─ Meta-Learner weights (FASE 2)         │
                 │ ├─ Branch & Bound filter (FASE 2)        │
                 │ └─ DP Optimal Sequencer (FASE 2)         │
                 └────────────┬─────────────────────────────┘
                              │
                              ▼
                 ┌──────────────────────────────────────────┐
                 │ Telegram Notification + Save             │
                 └────────────┬─────────────────────────────┘
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
         ┌────────────────┐ ┌──────────┐ ┌─────────────────────┐
         │ Telegram API   │ │ Database │ │ Live Dashboard      │
         │ (Usuário)      │ │ (Signal) │ │ (FASE 3 - RealTime) │
         └────────────────┘ └──────────┘ └─────────────────────┘
                                              ↑
                                              │
                              ┌───────────────┴───────────────┐
                              │                               │
                         Parâmetros                    Histórico de
                         Atualizados                   Ajustes
                              │                               │
                              └───────────────┬───────────────┘
                                              ▼
                        ┌──────────────────────────────────────┐
                        │ Resultado Real do Jogo               │
                        │ ├─ Vitória/Derrota                  │
                        │ ├─ Preço Final                       │
                        │ ├─ Odds Obtidas                      │
                        │ └─ Timestamp                         │
                        └──────────────┬───────────────────────┘
                                       │
                        ┌──────────────┴────────────────┐
                        │                               │
                        ▼                               ▼
            ┌────────────────────────┐   ┌─────────────────────────┐
            │ Feedback Loop (FASE 3) │   │ A/B Tester (FASE 3)     │
            ├────────────────────────┤   ├─────────────────────────┤
            │ 1. Detectar resultado  │   │ Compara:                │
            │ 2. Update histórico    │   │ - Win rate              │
            │ 3. Retreinar Meta-ML   │   │ - ROI                   │
            │ 4. Ajustar parâmetros  │   │ - Drawdown              │
            │ 5. Próximo sinal usa   │   │ - Sharpe ratio          │
            │    dados novos!        │   │                         │
            └────────────┬───────────┘   └─────────────┬───────────┘
                         │                             │
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                        ┌──────────────────────────────┐
                        │ Parâmetros 100% Otimizados   │
                        │ (Próximo sinal = mais lucro)  │
                        └──────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════
MATRIZ DE ALGORITMOS VS COMPONENTES
═══════════════════════════════════════════════════════════════════════════════════

ALGORITMO                  │ COMPONENTE                │ FASE │ GANHO
──────────────────────────┼──────────────────────────┼──────┼──────────────
Divide & Conquer          │ Strategy Pipeline        │ BASE │ Divisão
Early Stopping            │ Strategy Pipeline        │  1   │ -33% CPU
Memoization               │ Decision Cache           │  1   │ -25% tempo
Gradient Descent          │ Adaptive Optimizer       │  1   │ +8% WR
─────────────────────────────────────────────────────────────────────────
Dynamic Programming       │ DP Optimal Sequencer     │  2   │ +15-25%
Branch & Bound            │ Signal Pruner            │  2   │ +5% lucro
Meta-Learning             │ Meta-Learner Classifier  │  2   │ +10-20%
─────────────────────────────────────────────────────────────────────────
Feedback Loop             │ Feedback Loop            │  3   │ +5% lucro
A/B Testing               │ AB Tester                │  3   │ Validação
Reinforcement Learning    │ RL Agent (Future)        │  4   │ +20-30%+

═══════════════════════════════════════════════════════════════════════════════════
ESTRUTURA DE DADOS COMPARTILHADA
═════════════════════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────┐
│                   DATABASE CENTRAL                           │
├──────────────────────────────────────────────────────────────┤
│ Signals Table                                               │
│ ├─ ID, timestamp, type, confidence, strategies_passed      │
│ └─ game_id, signal_matched, etc                             │
│                                                              │
│ GameResults Table                                           │
│ ├─ ID, timestamp, game, result, price, odds                │
│ ├─ signal_id (FK), signal_matched, analyzed               │
│ └─ raw_data_json, analysis_json                             │
│                                                              │
│ PerformanceMetrics Table                                    │
│ ├─ Win rate by game/hour/pattern                            │
│ ├─ Historical performance                                   │
│ └─ Trend analysis                                           │
│                                                              │
│ ParameterHistory Table                                      │
│ ├─ Timestamp, min_confidence, kelly, weights               │
│ ├─ Win_rate, signal_count, reason                           │
│ └─ Created by: AdaptiveOptimizer                            │
│                                                              │
│ CacheEntry (In-Memory + optional persistence)              │
│ ├─ Key: hash(game+pattern+hour+trend)                       │
│ ├─ Value: (result, confidence, details)                     │
│ └─ TTL: 60 minutes                                          │
└──────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════
FLUXO DE DADOS - DETALHE PROFUNDO
═════════════════════════════════════════════════════════════════════════════════

INPUT:
  game_data = {
    'game': 'Double',
    'recent_colors': ['Vermelho', 'Preto', ...],
    'all_colors': ['Vermelho', ...] (100+),
    'prices': [100, 105, 110, ...],
    'timestamp': datetime.now()
  }

PROCESSAMENTO (FASE 1+2):
  1. Cache Check: key = hash(game, pattern, hour, trend)
     └─ Hit (15-20% casos) → Retorna resultado cacheado
     └─ Miss (80-85% casos) → Continua para pipeline
  
  2. Meta-Learner (FASE 2): Qual estratégia pesar mais?
     └─ Retorna: weights = [w1, w2, w3, w4, w5, w6]
  
  3. Strategy Pipeline com pesos:
     ├─ Strategy 1 (weight w1): Detecção de padrão
     ├─ Strategy 2 (weight w2): Validação técnica
     ├─ Early Stop Check: Se 4/6 passaram → PARE
     ├─ Strategy 3-4: Filtros
     ├─ Early Stop Check: Se 5/6 passaram → PARE
     ├─ Strategy 5-6: Validação final
     └─ Resultado: Signal com final_confidence
  
  4. Branch & Bound Filter (FASE 2):
     ├─ Calcula: lower_bound e upper_bound do lucro
     ├─ Se lower_bound < threshold → DESCARTA sinal
     └─ Resultado: Sinal filtrado
  
  5. DP Optimal Sequencer (FASE 2):
     ├─ State = (confidence, bankroll%, hour)
     ├─ DP[state] = aposta ótima
     └─ Resultado: bet_size otimizado
  
  6. Kelly Criterion + Adaptive Multiplier:
     ├─ Base Kelly = (bp - q) / b
     ├─ Final bet = Kelly * kelly_multiplier (ajustado por WR)
     └─ Resultado: aposta final

OUTPUT:
  signal = {
    'signal_type': 'Vermelho' | 'Suba',
    'confidence': 0.75-0.95,
    'bet_size': 5-50,
    'reason': 'Meta-learned + DP optimized',
    'strategies_passed': 4-6
  }

POST-EXECUTION:
  1. Save sinal no database
  2. Enviar notificação Telegram
  3. Update cache com resultado
  4. Aguardar resultado do jogo
  5. Feedback loop recebe resultado
  6. Parametros ajustados para próximo sinal
  7. Volta ao STEP 1 com melhor informação!

═════════════════════════════════════════════════════════════════════════════════
IMPACTO ESTIMADO POR FASE
═════════════════════════════════════════════════════════════════════════════════

                        BASELINE    FASE 1      FASE 2      FASE 3
                        ────────    ──────      ──────      ──────
Win Rate:               60%         68%         75%         78%
                                    (+8%)       (+15%)      (+3%)

Lucro Mensal:           12-15%      20-29%      30-45%      33-50%+
                                    (+100%)     (+50%)      (+10%)

Drawdown:               5%          4.5%        3.5%        3%
                                    (-10%)      (-22%)      (-14%)

ROI:                    1.2x        1.3x        1.5x        1.7x
                                    (+8%)       (+15%)      (+13%)

Tempo CPU:              100%        70%         60%         55%
                                    (-30%)      (-14%)      (-8%)

Inteligência:           Estática    Semi-Auto   Auto        Inteligente
Confiança:              Média       Boa         Muito Boa   Excelente

═════════════════════════════════════════════════════════════════════════════════
FIM DA ARQUITETURA
═════════════════════════════════════════════════════════════════════════════════
