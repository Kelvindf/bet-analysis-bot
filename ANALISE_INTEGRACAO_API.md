# 📊 Análise de Integração com Plataformas - Arquitetura de APIs

## Situação Atual: Blaze

### Status da Integração Blaze

#### ✅ O que está implementado:
1. **Cliente HTTP básico** (`BlazeDataCollector`)
   - Usa `requests` para comunicação
   - Headers configurados corretamente (User-Agent, Origin, Referer)
   - Session gerenciada para manter cookies
   - Tratamento de timeout (10s)

2. **Endpoints de coleta**
   - `GET /api/crash_games/recent` - Histórico do Crash
   - `GET /api/roulette_games/recent` - Histórico do Double/Roulette

3. **Processamento de dados**
   - Parse de resposta JSON
   - Conversão para pandas DataFrame
   - Cálculo de métricas derivadas (diff, média móvel, volatilidade)
   - Timestamp normalizado

4. **Fallback**
   - Dados simulados quando API indisponível
   - Permite teste sem conexão real

---

## ⚠️ Problemas Identificados

### 1. **URLs Endpoints Não Confirmadas**
```python
# Comentário no código indica que são exemplos
# url = f"{self.base_url}/crash_games/recent"  # ← Pode estar incorreta
```

**Ação necessária:** Validar URLs reais da API Blaze

### 2. **Sem Autenticação/API Key**
```python
# Não há implementação de:
# - Autenticação por token
# - API keys
# - OAuth
# - Session token
```

**Ação necessária:** Implementar autenticação real

### 3. **Sem Tratamento de Rate Limiting**
```python
# Sem:
# - Retry com backoff exponencial
# - Throttling
# - Queue de requisições
```

**Ação necessária:** Adicionar rate limiting

### 4. **Sem Validação de Resposta**
```python
# Sem verificar:
# - Statuscode 200 (só faz raise_for_status)
# - Estrutura JSON esperada
# - Campos obrigatórios
# - Tipos de dados
```

**Ação necessária:** Adicionar validação rigorosa

### 5. **Dados de Fallback Aleatórios**
```python
# Usa random.uniform() e random.choice()
# Não reflete padrões reais das plataformas
```

**Ação necessária:** Usar dados de fallback mais realistas

---

## 🏗️ Arquitetura Proposta para Múltiplas Plataformas

### Estrutura Recomendada:

```
src/
├── data_collection/
│   ├── __init__.py
│   ├── base_client.py              ← Classe abstrata
│   ├── blaze_client.py             ← Implementação Blaze
│   ├── bet365_client.py            ← Implementação Bet365
│   ├── other_client.py             ← Futura integração
│   └── collector_factory.py        ← Factory pattern
├── common/
│   ├── api_models.py               ← Modelos compartilhados
│   ├── exceptions.py               ← Exceções customizadas
│   └── rate_limiter.py             ← Rate limiting
└── config/
    ├── platform_config.py          ← Configuração por plataforma
    └── settings.py                 ← Settings globais
```

---

## 💡 Design Pattern: Factory + Abstract Base Class

### 1. Classe Base Abstrata

```python
# src/data_collection/base_client.py

from abc import ABC, abstractmethod
from typing import Dict, List
import pandas as pd
from datetime import datetime

class BasePlatformClient(ABC):
    """Classe base para todos os clientes de plataforma"""
    
    def __init__(self, config: Dict):
        self.name = config.get('name')
        self.base_url = config.get('base_url')
        self.api_key = config.get('api_key')
        self.timeout = config.get('timeout', 10)
        self.max_retries = config.get('max_retries', 3)
        self.session = self._create_session()
    
    @abstractmethod
    def _create_session(self):
        """Criar e configurar sessão HTTP"""
        pass
    
    @abstractmethod
    def _setup_headers(self):
        """Configurar headers específicos da plataforma"""
        pass
    
    @abstractmethod
    def _authenticate(self):
        """Autenticar na plataforma"""
        pass
    
    @abstractmethod
    def get_game_history(self, game_type: str, limit: int = 100) -> pd.DataFrame:
        """Obter histórico de um jogo específico"""
        pass
    
    @abstractmethod
    def validate_response(self, response: dict) -> bool:
        """Validar estrutura da resposta"""
        pass
    
    @abstractmethod
    def process_data(self, raw_data: dict) -> pd.DataFrame:
        """Processar dados brutos para DataFrame"""
        pass
    
    def health_check(self) -> bool:
        """Verificar se plataforma está acessível"""
        pass
```

---

## 🔧 Implementação Específica: Blaze

### Versão Melhorada

```python
# src/data_collection/blaze_client.py

import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from .base_client import BasePlatformClient
from ..common.exceptions import APIError, AuthenticationError

logger = logging.getLogger(__name__)

class BlazeClient(BasePlatformClient):
    """Cliente para plataforma Blaze"""
    
    GAME_TYPES = {
        'crash': '/games/crash/history',
        'double': '/games/roulette/history',
        'mines': '/games/mines/history',
        'limbo': '/games/limbo/history',
    }
    
    def _create_session(self):
        session = requests.Session()
        self._setup_headers()
        return session
    
    def _setup_headers(self):
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Referer': 'https://blaze.com/',
            'Origin': 'https://blaze.com'
        })
    
    def _authenticate(self):
        """Autenticar se necessário"""
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
    
    def get_game_history(self, game_type: str, limit: int = 100) -> pd.DataFrame:
        """Obter histórico do jogo"""
        if game_type not in self.GAME_TYPES:
            raise ValueError(f"Tipo de jogo inválido: {game_type}")
        
        endpoint = self.GAME_TYPES[game_type]
        
        for attempt in range(self.max_retries):
            try:
                url = f"{self.base_url}{endpoint}"
                params = {'limit': limit}
                
                response = self.session.get(
                    url, 
                    params=params, 
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Validar resposta
                if not self.validate_response(data):
                    logger.error(f"Resposta inválida para {game_type}")
                    continue
                
                # Processar dados
                df = self.process_data(data, game_type)
                logger.info(f"[OK] {self.name} - {game_type}: {len(df)} registros")
                return df
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout na tentativa {attempt + 1}/{self.max_retries}")
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Erro de conexão: {e}")
            except Exception as e:
                logger.error(f"Erro ao buscar {game_type}: {e}")
        
        logger.warning(f"Usando fallback para {game_type}")
        return self._get_fallback_data(game_type)
    
    def validate_response(self, response: dict) -> bool:
        """Validar estrutura da resposta"""
        # Validar campo obrigatório
        if 'data' not in response and 'records' not in response:
            return False
        
        # Validar que não é erro
        if response.get('error') or response.get('status') == 'error':
            return False
        
        return True
    
    def process_data(self, raw_data: dict, game_type: str) -> pd.DataFrame:
        """Processar dados brutos"""
        records = raw_data.get('data', raw_data.get('records', []))
        
        if not records:
            return pd.DataFrame()
        
        processed = []
        for record in records:
            processed_record = {
                'platform': 'blaze',
                'game_type': game_type,
                'game_id': record.get('id'),
                'timestamp': self._parse_timestamp(record.get('created_at')),
                'result': record.get('crash_point') or record.get('roll'),
            }
            processed.append(processed_record)
        
        df = pd.DataFrame(processed)
        
        # Adicionar métricas
        df = self._calculate_metrics(df)
        
        return df
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp em diferentes formatos"""
        formats = [
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%d %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str.rstrip('Z'), fmt.rstrip('Z'))
            except ValueError:
                continue
        
        raise ValueError(f"Formato timestamp desconhecido: {timestamp_str}")
    
    def _calculate_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcular métricas derivadas"""
        if df.empty:
            return df
        
        df = df.sort_values('timestamp')
        
        # Diferença
        df['diff'] = df['result'].diff()
        
        # Médias móveis
        df['moving_avg_5'] = df['result'].rolling(5, min_periods=1).mean()
        df['moving_avg_10'] = df['result'].rolling(10, min_periods=1).mean()
        
        # Volatilidade
        df['volatility'] = df['result'].rolling(10, min_periods=1).std()
        
        # Streaks (sequências)
        df['streak'] = (df['result'].diff() != 0).cumsum()
        
        return df
    
    def _get_fallback_data(self, game_type: str) -> pd.DataFrame:
        """Dados realistas para fallback"""
        import random
        
        records = []
        for i in range(50):
            timestamp = datetime.now() - timedelta(minutes=i*2)
            
            if game_type == 'crash':
                result = round(random.gauss(2.5, 1.2), 2)  # Distribuição mais realista
            elif game_type == 'double':
                result = random.choice(['vermelho', 'preto', 'branco'])
            else:
                result = random.randint(1, 100)
            
            records.append({
                'platform': 'blaze',
                'game_type': game_type,
                'game_id': f"{game_type}_{i}",
                'timestamp': timestamp,
                'result': result,
            })
        
        df = pd.DataFrame(records)
        return self._calculate_metrics(df)
    
    def health_check(self) -> bool:
        """Verificar se plataforma está acessível"""
        try:
            response = self.session.get(
                f"{self.base_url}/status",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
```

---

## 🎯 Implementação Bet365 (Exemplo)

```python
# src/data_collection/bet365_client.py

from .base_client import BasePlatformClient
import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Bet365Client(BasePlatformClient):
    """Cliente para plataforma Bet365"""
    
    GAME_TYPES = {
        'live_betting': '/api/live-betting',
        'prematch': '/api/prematch-betting',
        'cashout': '/api/cashout',
    }
    
    def _create_session(self):
        session = requests.Session()
        self._setup_headers()
        self._authenticate()
        return session
    
    def _setup_headers(self):
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
    
    def _authenticate(self):
        """Autenticar na Bet365"""
        if not self.api_key:
            raise AuthenticationError("API key necessária para Bet365")
        
        # Implementar login/token específico da Bet365
        auth_url = f"{self.base_url}/auth/login"
        
        try:
            response = self.session.post(
                auth_url,
                json={'api_key': self.api_key},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            token = response.json().get('token')
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
            
            logger.info("[OK] Autenticação Bet365 bem-sucedida")
        except Exception as e:
            raise AuthenticationError(f"Falha na autenticação Bet365: {e}")
    
    def get_game_history(self, game_type: str, limit: int = 100) -> pd.DataFrame:
        """Obter histórico específico da Bet365"""
        # Implementação específica da Bet365
        pass
    
    def validate_response(self, response: dict) -> bool:
        """Validar resposta específica da Bet365"""
        return 'data' in response and response.get('code') == 200
    
    def process_data(self, raw_data: dict, game_type: str) -> pd.DataFrame:
        """Processar dados da Bet365"""
        # Implementação específica
        pass
```

---

## 🏭 Factory Pattern

```python
# src/data_collection/collector_factory.py

from typing import Dict, List
from .blaze_client import BlazeClient
from .bet365_client import Bet365Client
from .base_client import BasePlatformClient

class CollectorFactory:
    """Factory para criar clientes de plataforma"""
    
    CLIENTS = {
        'blaze': BlazeClient,
        'bet365': Bet365Client,
        # 'other_platform': OtherClient,
    }
    
    @staticmethod
    def create(platform: str, config: Dict) -> BasePlatformClient:
        """Criar cliente para plataforma específica"""
        if platform not in CollectorFactory.CLIENTS:
            raise ValueError(f"Plataforma desconhecida: {platform}")
        
        client_class = CollectorFactory.CLIENTS[platform]
        return client_class(config)
    
    @staticmethod
    def create_all(config_dict: Dict) -> List[BasePlatformClient]:
        """Criar múltiplos clientes"""
        clients = []
        
        for platform, config in config_dict.items():
            try:
                client = CollectorFactory.create(platform, config)
                clients.append(client)
            except Exception as e:
                logger.error(f"Falha ao criar cliente {platform}: {e}")
        
        return clients
```

---

## ⚙️ Configuração Multi-Plataforma

```python
# src/config/platform_config.py

PLATFORM_CONFIGS = {
    'blaze': {
        'name': 'Blaze',
        'base_url': 'https://blaze.com/api',
        'api_key': None,  # Blaze não requer autenticação
        'timeout': 10,
        'max_retries': 3,
        'rate_limit': {
            'requests_per_minute': 60,
            'backoff_factor': 2,
        },
        'enabled': True,
    },
    'bet365': {
        'name': 'Bet365',
        'base_url': 'https://api.bet365.com',
        'api_key': 'YOUR_API_KEY_HERE',  # Configurar via variável de ambiente
        'timeout': 15,
        'max_retries': 5,
        'rate_limit': {
            'requests_per_minute': 30,
            'backoff_factor': 3,
        },
        'enabled': False,  # Desabilitado até configuração real
    },
}

# Função para carregamento de ambiente
import os

def get_platform_config(platform: str) -> dict:
    config = PLATFORM_CONFIGS.get(platform, {})
    
    # Sobrescrever com variáveis de ambiente
    api_key_env = os.getenv(f'{platform.upper()}_API_KEY')
    if api_key_env:
        config['api_key'] = api_key_env
    
    return config
```

---

## 📝 Configuração .env Sugerida

```bash
# Blaze (atual)
BLAZE_API_URL=https://blaze.com/api
BLAZE_ENABLED=true

# Bet365 (para integração futura)
BET365_API_URL=https://api.bet365.com
BET365_API_KEY=seu_api_key_aqui
BET365_ENABLED=false

# Rate limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BACKOFF_FACTOR=2

# Geral
DATA_COLLECTION_TIMEOUT=10
DATA_COLLECTION_MAX_RETRIES=3
```

---

## 🔗 Integração no main.py

```python
# src/main.py (alterações)

from data_collection.collector_factory import CollectorFactory
from config.platform_config import get_platform_config

class BetAnalysisPlatform:
    def __init__(self):
        load_dotenv()
        self.settings = Settings()
        self.setup_directories()
        
        # Carregar clientes de plataforma dinamicamente
        self.collectors = self._init_collectors()
    
    def _init_collectors(self):
        """Inicializar clientes de todas as plataformas habilitadas"""
        collectors = {}
        platforms = ['blaze', 'bet365']  # Adicionar mais conforme necessário
        
        for platform in platforms:
            config = get_platform_config(platform)
            
            if config.get('enabled', False):
                try:
                    collector = CollectorFactory.create(platform, config)
                    collectors[platform] = collector
                    logger.info(f"[OK] {platform} inicializado")
                except Exception as e:
                    logger.error(f"[ERRO] Falha ao inicializar {platform}: {e}")
        
        return collectors
    
    def collect_data(self):
        """Coletar dados de todas as plataformas"""
        all_data = {}
        
        for platform, collector in self.collectors.items():
            try:
                logger.info(f"[*] Coletando de {platform}...")
                
                # Coletar diferentes tipos de jogos
                game_types = ['crash', 'double']  # Específico por plataforma
                platform_data = {}
                
                for game_type in game_types:
                    try:
                        data = collector.get_game_history(game_type, limit=100)
                        platform_data[game_type] = data
                    except Exception as e:
                        logger.error(f"Erro coletando {game_type}: {e}")
                
                all_data[platform] = platform_data
                
            except Exception as e:
                logger.error(f"[ERRO] Falha ao coletar de {platform}: {e}")
        
        return all_data
```

---

## 🧪 Testes Unitários

```python
# tests/test_blaze_client.py

import pytest
import pandas as pd
from src.data_collection.blaze_client import BlazeClient

@pytest.fixture
def blaze_config():
    return {
        'name': 'Blaze',
        'base_url': 'https://blaze.com/api',
        'api_key': None,
        'timeout': 10,
    }

def test_blaze_client_creation(blaze_config):
    client = BlazeClient(blaze_config)
    assert client.name == 'Blaze'

def test_health_check(blaze_config):
    client = BlazeClient(blaze_config)
    # Testar com mock
    assert isinstance(client.health_check(), bool)

def test_process_data(blaze_config):
    client = BlazeClient(blaze_config)
    raw_data = {
        'data': [
            {'id': '1', 'crash_point': 2.5, 'created_at': '2025-12-04T10:00:00Z'},
            {'id': '2', 'crash_point': 3.2, 'created_at': '2025-12-04T10:01:00Z'},
        ]
    }
    
    df = client.process_data(raw_data, 'crash')
    assert len(df) == 2
    assert 'moving_avg_5' in df.columns
```

---

## ✅ Checklist de Integração

### Para cada nova plataforma:
- [ ] Documentar endpoints reais
- [ ] Implementar classe específica (herdar de BasePlatformClient)
- [ ] Configurar autenticação corretamente
- [ ] Implementar rate limiting específico
- [ ] Validar estrutura de resposta
- [ ] Testar com dados reais (mock)
- [ ] Adicionar testes unitários
- [ ] Configurar variáveis de ambiente
- [ ] Documentar diferenças de dados
- [ ] Implementar tratamento de erros específicos

---

## 📚 Próximos Passos

1. **Validar URLs reais da Blaze** - Confirmar endpoints corretos
2. **Implementar autenticação real** - Se necessário
3. **Adicionar rate limiting** - Com backoff exponencial
4. **Integrar Bet365** - Usar estrutura proposta
5. **Adicionar testes** - Para cada plataforma
6. **Documentar APIs** - Manter Wiki atualizada
7. **Monitoramento** - Health checks periódicos

---

## 🎯 Sumário

**Status Atual:**
- ✅ Estrutura básica funcional para Blaze
- ⚠️ Endpoints podem não estar corretos
- ❌ Sem autenticação implementada
- ❌ Sem rate limiting
- ⚠️ Sem validação rigorosa

**Recomendação:**
Implementar padrão Factory + Abstract Base Class para facilitar adição de novas plataformas e garantir consistência.
