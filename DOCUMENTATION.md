# 🎓 DOCUMENTAÇÃO COMPLETA - REFATORAÇÃO

## 📋 Índice

1. [Introdução](#introdução)
2. [Guia de Instalação](#guia-de-instalação)
3. [Arquitetura](#arquitetura)
4. [Referência de API](#referência-de-api)
5. [Exemplos de Uso](#exemplos-de-uso)
6. [Troubleshooting](#troubleshooting)

---

## Introdução

A plataforma foi refatorada em **5 fases** para melhorar:
- ✅ **Robustez**: Tratamento de erros, validação, recuperação automática
- ✅ **Persistência**: Histórico completo em banco de dados
- ✅ **Escalabilidade**: Arquitetura preparada para crescimento
- ✅ **Manutenibilidade**: Código limpo, bem documentado, testável
- ✅ **Visibilidade**: Logging estruturado, monitoramento, health checks

---

## Guia de Instalação

### 1. Instalar dependências

```bash
pip install -r requirements.txt
pip install sqlalchemy>=2.0.0  # BD
pip install psutil              # Monitoramento
pip install pytest              # Testes
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com suas credenciais
```

### 3. Inicializar banco de dados

```python
from database import init_db
Session = init_db('data/db/analysis.db')
print("✅ Banco de dados pronto!")
```

---

## Arquitetura

### Estrutura de Módulos

```
src/
├── core/                    # Tipos e abstrações
│   ├── types.py            # Enums, Dataclasses
│   ├── exceptions.py       # Exceções customizadas
│   └── decorators.py       # @retry, @cache, @timing
│
├── database/               # Persistência
│   ├── models.py           # Modelos SQLAlchemy
│   └── repository.py       # Data Access Layer
│
├── data_collection/        # Coleta de dados
│   ├── blaze_client_unified.py  # Cliente Blaze
│   └── validators.py       # Validadores de dados
│
├── config/
│   └── logger_config.py    # Logging estruturado
│
├── monitoring.py           # Health checks, alertas
└── integration.py          # Integração com main
```

### Fluxo de Dados

```
Blaze API
   ↓
BlazeClient (unified)
   ↓
Validadores
   ↓
Base de Dados (raw_data)
   ↓
Análise (strategy_pipeline)
   ↓
Sinais gerados
   ↓
BD (signals)
   ↓
Telegram
```

---

## Referência de API

### Core Types

#### Signal

```python
from core import Signal, SignalType, GameType, SignalStatus
from datetime import datetime

signal = Signal(
    id="sig_001",
    game=GameType.DOUBLE,
    signal_type=SignalType.RED,
    confidence=0.85,           # 0.0-1.0
    timestamp=datetime.now(),
    strategies_passed=4,       # 0-6
    status=SignalStatus.PENDING
)

# Atributos
signal.status = SignalStatus.WIN  # Mudar status
signal.verified_at = datetime.now()
signal.metadata = {'extra': 'info'}
```

#### BlazeData

```python
from core import BlazeData, GameType

data = BlazeData(
    id="blaze_001",
    game=GameType.DOUBLE,
    timestamp=datetime.now(),
    result="red",
    price=None,                # Para Crash
    data={'color': 'red'},     # JSON completo
    collected_at=datetime.now()
)
```

### Database

#### SignalRepository

```python
from database import SignalRepository, init_db

Session = init_db()
repo = SignalRepository(Session)

# Salvar
repo.save(signal)

# Buscar
signal = repo.get_by_id('sig_001')
pending = repo.get_pending(hours=24)

# Verificar resultado
repo.verify_result('sig_001', won=True)

# Estatísticas
stats = repo.get_stats(game='Double', hours=24)
# {
#     'total': 50,
#     'wins': 30,
#     'losses': 20,
#     'win_rate': 0.6,
#     'avg_confidence': 0.82
# }
```

#### RawDataRepository

```python
from database import RawDataRepository

repo = RawDataRepository(Session)

# Salvar dados brutos
repo.save(
    game='double',
    timestamp=datetime.now(),
    result='red',
    data={'color': 'red'},
    hash_value='abc123'
)

# Buscar
data = repo.get_latest('double', limit=100)

# Contar
counts = repo.count_by_game(hours=24)
# {'double': 150, 'crash': 140}
```

### Data Collection

#### BlazeClient

```python
from data_collection.blaze_client_unified import BlazeClient

client = BlazeClient(use_cache=True, validate=True)

# Dados do Double
double_data = client.get_double_history(limit=100)

# Dados do Crash
crash_data = client.get_crash_history(limit=100)

# Ambos
double, crash = client.get_all_data(limit=100)

# Status
health = client.get_health()
```

#### DataValidator

```python
from data_collection.validators import DataValidator

# Validar único
try:
    DataValidator.validate_blaze_data(blaze_data)
except DataValidationError as e:
    print(f"Erro: {e}")

# Validar lista
valid, errors = DataValidator.validate_data_list(data_list)

# Qualidade
quality = DataValidator.check_data_quality(data_list)
# {
#     'total': 100,
#     'completeness': 0.98,
#     'duplicates': 2,
#     'quality_score': 0.92,
#     'status': 'OK'
# }

# Deduplicar
unique = DataValidator.deduplicate(data_list)
```

### Monitoring

#### HealthChecker

```python
from monitoring import HealthChecker

checker = HealthChecker()

# Fazer check
health = checker.check(
    data_collection_ok=True,
    telegram_ok=True,
    database_ok=True,
    signals_processed=150
)

# Histórico
history = checker.get_history(last_n=10)
```

#### AlertSystem

```python
from monitoring import AlertSystem

alerts = AlertSystem()

# Detectar anomalias
problems = alerts.check_anomalies(health)

# Configurar thresholds
alerts.alert_thresholds['memory_mb'] = 300
```

#### AutoRecovery

```python
from monitoring import AutoRecovery

recovery = AutoRecovery()

# Handle error com recovery
success = recovery.handle_error(
    component='api',
    error=Exception("API indisponível"),
    recovery_func=lambda: client.test_connectivity()
)

# Reset
recovery.reset('api')
```

### Logging

#### Setup

```python
from config.logger_config import setup_logging, get_logger
import logging

# Uma vez no main
setup_logging(
    log_dir='logs',
    level=logging.INFO,
    console=True,
    structured=True  # JSON logs
)
```

#### Uso

```python
from config.logger_config import get_logger

logger = get_logger(__name__)

# Diferentes níveis
logger.debug("Informação detalhada")
logger.info("Operação completada")
logger.warning("Atenção", extra={'key': 'value'})
logger.error("Erro ocorreu", exc_info=True)
logger.critical("Falha crítica")
```

### Decoradores

#### @retry

```python
from core import retry

@retry(max_attempts=3, delay=1.0, backoff=2.0)
def fetch_from_api():
    return requests.get("http://api.com")

# Tenta 3 vezes com backoff exponencial (1s, 2s, 4s)
```

#### @cache

```python
from core import cache

@cache(ttl_seconds=300)
def expensive_operation():
    return complex_calculation()

# Resultado é cacheado por 5 minutos
```

#### @timing

```python
from core import timing

@timing
def slow_function():
    time.sleep(1)

# Registra tempo de execução no log
```

#### @validate_input

```python
from core import validate_input

@validate_input(
    confidence=lambda x: 0 <= x <= 1,
    game=lambda x: x in ['Double', 'Crash']
)
def process(confidence, game):
    pass

# Valida automaticamente
process(0.85, 'Double')  # OK
process(1.5, 'Double')   # ValueError
```

---

## Exemplos de Uso

### Exemplo 1: Coletar e Salvar Dados

```python
from data_collection.blaze_client_unified import BlazeClient
from data_collection.validators import DataValidator
from database import RawDataRepository, init_db
import logging

logging.basicConfig(level=logging.INFO)

# Coletar
client = BlazeClient()
double_data = client.get_double_history(limit=100)

# Validar
valid_data, errors = DataValidator.validate_data_list(double_data)
print(f"✅ {len(valid_data)} válidos, ❌ {len(errors)} inválidos")

# Salvar
Session = init_db()
repo = RawDataRepository(Session)

for data in valid_data:
    repo.save(
        game='double',
        timestamp=data.timestamp,
        result=data.result,
        data=data.data,
        hash_value=data.id  # Usar ID como hash
    )

print("💾 Dados salvos!")
```

### Exemplo 2: Gerar Sinal e Persistir

```python
from core import Signal, SignalType, GameType, SignalStatus
from database import SignalRepository, init_db
from datetime import datetime

# Criar sinal
signal = Signal(
    id="sig_teste_001",
    game=GameType.DOUBLE,
    signal_type=SignalType.RED,
    confidence=0.87,
    timestamp=datetime.now(),
    strategies_passed=4
)

# Salvar
Session = init_db()
repo = SignalRepository(Session)
repo.save(signal)

# Depois, verificar resultado
repo.verify_result("sig_teste_001", won=True)

# Obter stats
stats = repo.get_stats()
print(f"Taxa de acerto: {stats['win_rate']*100:.1f}%")
```

### Exemplo 3: Health Checks Automáticos

```python
from monitoring import HealthChecker, AlertSystem
import time

checker = HealthChecker()
alerts = AlertSystem()

# Loop de monitoramento
while True:
    health = checker.check(
        data_collection_ok=True,
        telegram_ok=True,
        database_ok=True,
        signals_processed=150
    )
    
    # Detectar problemas
    problems = alerts.check_anomalies(health)
    
    if problems:
        for problem in problems:
            print(f"⚠️ {problem}")
    
    # A cada 60 segundos
    time.sleep(60)
```

### Exemplo 4: Usar Decoradores

```python
from core import retry, cache, timing
import requests

@retry(max_attempts=3, delay=1.0)
@cache(ttl_seconds=300)
@timing
def fetch_blaze_api():
    """Busca com retry, cache e timing"""
    response = requests.get("https://blaze.bet.br/games/double", timeout=10)
    return response.json()

data = fetch_blaze_api()  # Tenta até 3 vezes, cacheia por 5min
```

---

## Troubleshooting

### Problema: "Blaze API não disponível"

**Solução:**
1. Verificar conexão com internet
2. Verificar se blaze.com está acessível
3. Sistema usa fallback automático (dados simulados)

```python
from data_collection.blaze_client_unified import BlazeClient

client = BlazeClient()
print(f"API disponível: {client.api_available}")

if not client.api_available:
    print("Usando fallback com dados simulados")
```

### Problema: "Erro ao salvar no banco de dados"

**Solução:**
```python
from database import init_db

# Verificar se arquivo de BD existe
import os
os.makedirs('data/db', exist_ok=True)

# Reinicializar
Session = init_db('data/db/analysis.db')
print("✅ BD pronto")
```

### Problema: "Memory leak"

**Solução:**
```python
from monitoring import HealthChecker

checker = HealthChecker()
health = checker.check()

if health.memory_usage_mb > 400:
    print(f"⚠️ Memória alta: {health.memory_usage_mb}MB")
    # Limpar cache, reiniciar conexões, etc
```

### Problema: "Sinais não estão sendo salvos"

**Solução:**
```python
from database import SignalRepository, init_db

Session = init_db()
repo = SignalRepository(Session)

# Verificar sinais pendentes
pending = repo.get_pending(hours=1)
print(f"Sinais pendentes: {len(pending)}")

# Verificar stats
stats = repo.get_stats()
print(f"Total de sinais: {stats['total']}")
```

---

## Next Steps

1. **Executar testes:** `pytest tests/ -v`
2. **Monitorar sistema:** Usar `monitoring.py` em loop
3. **Backup de dados:** Fazer backup regular do `data/db/analysis.db`
4. **Análise de performance:** Usar histórico de health checks

---

**Versão:** 2.0 (Refatoração Completa)  
**Data:** Dezembro 2025  
**Status:** ✅ Produção

