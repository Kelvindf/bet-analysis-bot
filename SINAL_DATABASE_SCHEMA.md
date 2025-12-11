# 📊 Schema de Armazenamento de Sinais no Banco de Dados

## 🎯 Overview

Cada sinal gerado pelo sistema é armazenado em detalhes no banco de dados SQLite (`data/db/analysis.db`) com todas as informações necessárias para análise, auditoria e backtesting.

---

## 📋 Estrutura de Dados - Tabela `signals`

```sql
CREATE TABLE signals (
    id VARCHAR PRIMARY KEY,                   -- ID único do sinal (ex: sig_1702300453)
    game VARCHAR NOT NULL,                    -- CRASH ou DOUBLE
    signal_type VARCHAR NOT NULL,             -- RED, GREEN, GRAY, etc
    confidence FLOAT NOT NULL,                -- Confiança 0.0-1.0
    timestamp DATETIME NOT NULL,              -- Data/hora exato
    strategies_passed INTEGER,                -- 0-6 estratégias validadas
    bet_size FLOAT,                          -- Tamanho da aposta (Kelly)
    result VARCHAR,                          -- WIN, LOSS, NULL (pendente)
    metadata JSON,                           -- Dados estruturados adicionais
    created_at DATETIME DEFAULT NOW(),       -- Criado em
    updated_at DATETIME DEFAULT NOW()        -- Atualizado em
);
```

---

## 🔍 Exemplo de Sinal Armazenado

### CRASH
```json
{
  "id": "sig_crash_1702300453",
  "game": "Crash",
  "signal_type": "RED",
  "confidence": 0.979,
  "timestamp": "2025-12-11T00:14:13",
  "strategies_passed": 3,
  "bet_size": 45.50,
  "result": null,
  "metadata": {
    "odds": 2.1,
    "kelly_fraction": 0.25,
    "bankroll": 1000.0,
    "drawdown_percent": 2.3,
    "data_source": "blaze_api",
    "colors_analyzed": 100,
    "multiplicador_esperado": "1.5x - 2.5x"
  }
}
```

### DOUBLE
```json
{
  "id": "sig_double_1702300500",
  "game": "Double",
  "signal_type": "RED",
  "confidence": 0.856,
  "timestamp": "2025-12-11T00:15:00",
  "strategies_passed": 5,
  "bet_size": 38.25,
  "result": null,
  "metadata": {
    "odds": 1.90,
    "kelly_fraction": 0.25,
    "bankroll": 1000.0,
    "drawdown_percent": 2.3,
    "data_source": "blaze_api",
    "colors_analyzed": 100,
    "cor_prevista": "Vermelho"
  }
}
```

---

## 📈 Campos Armazenados Detalhados

| Campo | Tipo | Descrição | Exemplo |
|-------|------|-----------|---------|
| **id** | VARCHAR | ID único do sinal | `sig_crash_1702300453` |
| **game** | VARCHAR | Tipo de jogo | `Crash`, `Double` |
| **signal_type** | VARCHAR | Tipo de previsão | `RED`, `GREEN`, `GRAY` |
| **confidence** | FLOAT | Nível de confiança (0.0-1.0) | `0.979` (97.9%) |
| **timestamp** | DATETIME | Hora exata da geração | `2025-12-11 00:14:13` |
| **strategies_passed** | INT | Estratégias validadas (0-6) | `3` (passou em 3 de 6) |
| **bet_size** | FLOAT | Tamanho da aposta calculado | `45.50` |
| **result** | VARCHAR | Resultado (após confirmar) | `WIN`, `LOSS`, `NULL` |
| **metadata** | JSON | Dados estruturados adicionais | (veja abaixo) |
| **created_at** | DATETIME | Quando foi criado no BD | Auto |
| **updated_at** | DATETIME | Última atualização | Auto |

---

## 🔐 Metadata - Informações Adicionais

Cada sinal armazena metadados em formato JSON:

```json
{
  "odds": 1.90,                          // Odd do jogo (1.90 para Double cores, 2.0-14.0 para Crash)
  "kelly_fraction": 0.25,                // Fração de Kelly usada
  "bankroll": 1000.0,                    // Saldo da conta naquele momento
  "drawdown_percent": 2.3,               // % de drawdown no momento
  "data_source": "blaze_api",            // Origem dos dados (API ou fallback)
  "colors_analyzed": 100,                // Quantas cores foram analisadas
  "multiplicador_esperado": "1.5x - 2.5x", // Para Crash
  "cor_prevista": "Vermelho"             // Para Double
}
```

---

## 💾 Como os Dados São Armazenados

### No Sistema (ao vivo)
```
1. Coleta de dados → BlazeDataCollectorV2
2. Análise → StatisticalAnalyzer
3. Pipeline 6 estratégias → StrategyPipeline
4. Formatação → _format_signal_for_telegram()
5. Armazenamento → repo.save(signal) em SQLite
6. Envio → TelegramBotManager.send_signals()
7. Rastreamento → ResultTracker.save_signal()
```

### Código de Persistência
```python
# Em main.py - Ciclo de análise
signal_data = {
    'game_id': 'sig_crash_1702300453',
    'game': 'Crash',
    'signal_type': 'RED',
    'confidence': 0.979,
    'strategies_passed': 3,
    'timestamp': datetime.now(),
    'bet_size': 45.50,
    'odds': 2.1,
    'kelly_fraction': 0.25,
    'bankroll': 1000.0,
    'drawdown_status': {...},
    'metadata': {...}
}

# Salvar no BD
db_signal = Signal(
    id=signal_data['game_id'],
    game=GameType.CRASH,
    signal_type=SignalType.RED,
    confidence=signal_data['confidence'],
    timestamp=signal_data['timestamp'],
    strategies_passed=signal_data['strategies_passed'],
    bet_size=signal_data['bet_size'],
    metadata={...}
)
self.repo.save(db_signal)
```

---

## 🔄 Ciclo de Vida do Sinal no BD

```
[1] CRIAÇÃO
    ├─ Gerado pelo Pipeline (6 estratégias)
    ├─ Salvo com result=NULL (pendente)
    └─ Enviado via Telegram

[2] RASTREAMENTO
    ├─ Sistema monitora o resultado
    ├─ Quando o jogo termina, compara
    └─ Atualiza result=WIN ou LOSS

[3] ANÁLISE
    ├─ Calcula estatísticas
    ├─ Atualiza win_rate
    ├─ Ajusta Kelly Criterion
    └─ Otimiza estratégias

[4] AUDITORIA
    ├─ Histórico completo
    ├─ Rastreabilidade 100%
    └─ Backtesting possível
```

---

## 📊 Consultando os Sinais

### Via Python
```python
from database import SignalRepository

repo = SignalRepository(session)

# Todos os sinais
todos = repo.get_all()

# Por tipo
crash_signals = repo.find_by_game(GameType.CRASH)
double_signals = repo.find_by_game(GameType.DOUBLE)

# Por confiança
altos = repo.find_by_confidence_min(0.80)

# Estatísticas
stats = repo.get_stats(timeframe='24h')
# Retorna: {
#   'total_signals': 150,
#   'signals_won': 95,
#   'signals_lost': 45,
#   'win_rate': 0.633,
#   'avg_confidence': 0.796,
#   'total_profit': 2450.50
# }
```

### Via SQL Direto
```sql
-- Últimos 10 sinais
SELECT * FROM signals 
ORDER BY timestamp DESC 
LIMIT 10;

-- Sinais de Crash hoje
SELECT * FROM signals 
WHERE game='Crash' 
AND DATE(timestamp) = CURDATE();

-- Taxa de vitória por confiança
SELECT 
    ROUND(confidence, 2) as conf_level,
    COUNT(*) as total,
    SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END) as wins,
    ROUND(SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END) / COUNT(*), 3) as win_rate
FROM signals
WHERE result IS NOT NULL
GROUP BY ROUND(confidence, 2)
ORDER BY conf_level DESC;

-- Sinais por hora (para análise de padrões)
SELECT 
    HOUR(timestamp) as hora,
    COUNT(*) as sinais_gerados,
    ROUND(AVG(confidence), 3) as conf_media,
    SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END) as vitorias
FROM signals
WHERE result IS NOT NULL
GROUP BY HOUR(timestamp)
ORDER BY hora;
```

---

## 🎯 Por Que Armazenar Tudo?

✅ **Auditoria** - Rastear cada decisão  
✅ **Backtesting** - Validar estratégias com dados reais  
✅ **Otimização** - Ajustar parameters baseado em histórico  
✅ **Análise** - Identificar padrões de win/loss  
✅ **Compliance** - Documentação legal de operações  
✅ **Machine Learning** - Dados para treinar novos modelos  

---

## 📁 Localização do Banco

```
bet_analysis_platform-2/
└── data/
    └── db/
        └── analysis.db  ← Arquivo SQLite (todos os sinais)
```

**Backup recomendado:** Copiar `analysis.db` regularmente para segurança!

---

## 🚀 Próximos Passos

1. ✅ Sinais sendo salvos com toda informação
2. ✅ Metadados estruturados em JSON
3. ✅ Telegram recebendo mensagens formatadas
4. ⏳ Verificação automática de resultados
5. ⏳ Dashboard de análise (em desenvolvimento)
6. ⏳ Exportação para Excel/CSV

---

**Status:** ✅ Sistema completo e funcional  
**Última atualização:** 11 de dezembro de 2025
