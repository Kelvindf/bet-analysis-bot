# 🧪 Guia Prático: Testando e Validando Integração com APIs

## 1. Como Testar a Conexão com Blaze

### A. Teste Rápido no PowerShell

```powershell
# Ativar venv
.\venv\Scripts\Activate.ps1

# Testar conexão com Blaze
python -c "
import requests

# Testar endpoints potenciais da Blaze
base_url = 'https://blaze.com/api'

endpoints_para_testar = [
    '/games/crash/history',
    '/games/roulette/history',
    '/crash_games/recent',
    '/roulette_games/recent',
    '/history',
    '/status',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'application/json',
}

for endpoint in endpoints_para_testar:
    url = f'{base_url}{endpoint}'
    try:
        response = requests.get(url, headers=headers, timeout=5)
        print(f'[{response.status_code}] {url}')
        
        if response.status_code == 200:
            print(f'   Resposta: {response.json()}')
    except Exception as e:
        print(f'[ERRO] {url} - {e}')
"
```

### B. Teste Mais Completo

```python
# test_blaze_connectivity.py

import requests
import json
from datetime import datetime

def test_blaze_endpoints():
    base_url = 'https://blaze.com/api'
    
    endpoints = {
        'crash_recent': '/games/crash/history',
        'roulette_recent': '/games/roulette/history',
        'status': '/status',
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Referer': 'https://blaze.com/',
        'Origin': 'https://blaze.com'
    }
    
    print("=" * 70)
    print("TESTE DE CONECTIVIDADE - BLAZE API")
    print("=" * 70)
    
    for name, endpoint in endpoints.items():
        url = f"{base_url}{endpoint}"
        
        try:
            print(f"\n[TESTANDO] {name}")
            print(f"URL: {url}")
            
            response = requests.get(
                url, 
                headers=headers, 
                timeout=10,
                params={'limit': 10}
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"Estrutura da resposta:")
                print(f"  - Keys: {list(data.keys())}")
                
                # Mostrar primeiro registro se for lista
                if isinstance(data, list) and len(data) > 0:
                    print(f"  - Exemplo registro: {json.dumps(data[0], indent=2, default=str)}")
                elif isinstance(data, dict) and 'data' in data:
                    print(f"  - Tipo 'data': {type(data['data'])}")
                    if isinstance(data['data'], list) and len(data['data']) > 0:
                        print(f"  - Exemplo: {json.dumps(data['data'][0], indent=2, default=str)}")
                
                print("[OK] SUCESSO")
            else:
                print(f"[ERRO] Status {response.status_code}")
                print(f"Resposta: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("[ERRO] Timeout na requisição")
        except requests.exceptions.ConnectionError as e:
            print(f"[ERRO] Erro de conexão: {e}")
        except json.JSONDecodeError:
            print(f"[ERRO] Resposta não é JSON válido")
        except Exception as e:
            print(f"[ERRO] {type(e).__name__}: {e}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_blaze_endpoints()
```

### C. Teste de Taxa de Requisição

```python
# test_rate_limiting.py

import requests
import time
from datetime import datetime

def test_rate_limiting():
    """Testar rate limiting da Blaze"""
    
    url = "https://blaze.com/api/games/crash/history"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
    }
    
    print("=" * 70)
    print("TESTE DE RATE LIMITING")
    print("=" * 70)
    
    # Fazer 10 requisições em rápida sucessão
    for i in range(10):
        try:
            start = time.time()
            response = requests.get(url, headers=headers, timeout=5)
            elapsed = time.time() - start
            
            status = f"[{response.status_code}]"
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"{timestamp} - Req {i+1:2d} - {status} - {elapsed:.2f}s", end="")
            
            # Verificar rate limit headers
            if 'X-RateLimit-Remaining' in response.headers:
                remaining = response.headers['X-RateLimit-Remaining']
                print(f" - Restantes: {remaining}", end="")
            
            if 'X-RateLimit-Reset' in response.headers:
                reset = response.headers['X-RateLimit-Reset']
                print(f" - Reset: {reset}", end="")
            
            print()  # Nova linha
            
        except Exception as e:
            print(f"Req {i+1} - [ERRO] {e}")
        
        # Aguardar 1 segundo entre requisições
        if i < 9:
            time.sleep(1)
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_rate_limiting()
```

---

## 2. Validando a Resposta da API

### A. Estrutura Esperada

```python
# Teste para validar estrutura da resposta

def validate_crash_response(response_data):
    """Validar resposta do endpoint de Crash"""
    
    # Verificações básicas
    checks = {
        'response_type': isinstance(response_data, (dict, list)),
        'not_empty': len(response_data) > 0 if isinstance(response_data, list) else True,
        'has_data': 'data' in response_data if isinstance(response_data, dict) else True,
    }
    
    # Validar registros
    records = response_data if isinstance(response_data, list) else response_data.get('data', [])
    
    for i, record in enumerate(records[:3]):  # Validar primeiros 3
        print(f"\nRegistro {i+1}:")
        print(f"  Chaves: {list(record.keys())}")
        
        # Campos esperados
        expected_fields = {
            'id': (int, str),
            'crash_point': (int, float),
            'created_at': (str,),
            'timestamp': (str, int, float),
        }
        
        for field, expected_types in expected_fields.items():
            if field in record:
                value = record[field]
                is_valid = isinstance(value, expected_types)
                status = "OK" if is_valid else f"TIPO ERRADO ({type(value).__name__})"
                print(f"  - {field}: {status} ({value})")
            else:
                print(f"  - {field}: FALTANDO")

# Exemplo de uso
if __name__ == "__main__":
    import requests
    
    response = requests.get("https://blaze.com/api/games/crash/history", timeout=10)
    data = response.json()
    
    validate_crash_response(data)
```

---

## 3. Mapeando Endpoints Reais

### Template para Descoberta

```python
# discover_endpoints.py

import requests
from itertools import product

def discover_blaze_api():
    """Descobrir endpoints disponíveis na API Blaze"""
    
    base_url = "https://blaze.com"
    
    # Padrões comuns de API
    paths = [
        '/api/v1/{resource}',
        '/api/v2/{resource}',
        '/api/{resource}',
        '/{resource}',
    ]
    
    resources = [
        'games',
        'history',
        'results',
        'status',
        'crash',
        'roulette',
        'double',
        'mines',
        'limbo',
    ]
    
    endpoints = [
        'recent',
        'all',
        'latest',
        'list',
        'get',
        'history',
    ]
    
    print("Testando combinações de endpoints...\n")
    
    found_endpoints = []
    
    for path_template in paths:
        for resource in resources:
            for endpoint in endpoints:
                # Criar URL
                url = path_template.format(resource=resource)
                full_url = f"{base_url}{url}/{endpoint}"
                
                try:
                    response = requests.get(full_url, timeout=3)
                    
                    # Verificar se obteve resposta válida
                    if response.status_code in [200, 400, 403]:  # Endpoints existentes
                        found_endpoints.append({
                            'url': full_url,
                            'status': response.status_code,
                            'size': len(response.content)
                        })
                        
                        if response.status_code == 200:
                            print(f"[200] {full_url}")
                
                except:
                    pass
    
    return found_endpoints
```

---

## 4. Implementando Retry com Backoff

```python
# src/common/retry_helper.py

import requests
import time
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    backoff_factor: float = 2,
    timeout: int = 10
) -> Any:
    """
    Executar função com retry e backoff exponencial
    
    Args:
        func: Função a ser executada
        max_retries: Número máximo de tentativas
        backoff_factor: Fator de multiplicação do delay
        timeout: Timeout em segundos
    """
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Tentativa {attempt + 1}/{max_retries}")
            return func()
        
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout - Tentativa {attempt + 1}")
        
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Erro de conexão - Tentativa {attempt + 1}: {e}")
        
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                wait_time = int(e.response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited - Aguardando {wait_time}s")
                time.sleep(wait_time)
                continue
            else:
                raise
        
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            raise
        
        # Backoff exponencial
        if attempt < max_retries - 1:
            wait_time = backoff_factor ** attempt
            logger.info(f"Aguardando {wait_time}s antes da próxima tentativa")
            time.sleep(wait_time)
    
    raise Exception(f"Falha após {max_retries} tentativas")

# Exemplo de uso
def fetch_blaze_data():
    def make_request():
        response = requests.get(
            "https://blaze.com/api/games/crash/history",
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    data = retry_with_backoff(make_request, max_retries=3)
    return data
```

---

## 5. Teste Prático: Implementação Gradual

### Passo 1: Testar Endpoint Básico

```python
# test_step1_basic_endpoint.py

import requests

# Teste mais simples possível
url = "https://blaze.com/api/games/crash/history"
headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}

try:
    response = requests.get(url, headers=headers, timeout=10)
    
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    
    if response.status_code == 200:
        import json
        data = response.json()
        print(f"Resposta: {json.dumps(data, indent=2)[:500]}...")
    else:
        print(f"Erro: {response.text[:200]}")
        
except Exception as e:
    print(f"Erro: {e}")
```

### Passo 2: Validar Estrutura

```python
# test_step2_validate_structure.py

# ... após confirmar que o endpoint retorna 200

def check_structure(data):
    """Verificar estrutura da resposta"""
    
    print("Análise da estrutura:")
    print(f"Tipo: {type(data)}")
    print(f"Keys/Indices: {list(data.keys()) if isinstance(data, dict) else 'Lista'}")
    
    if isinstance(data, dict) and 'data' in data:
        records = data['data']
    elif isinstance(data, list):
        records = data
    else:
        return
    
    if records:
        first = records[0]
        print(f"\nPrimeiro registro:")
        for key, value in first.items():
            print(f"  {key}: {value} ({type(value).__name__})")
```

### Passo 3: Extrair Campo Principal

```python
# test_step3_extract_field.py

# Extrair o campo principal de resultado
def extract_results(data):
    """Extrair valores de resultado"""
    
    records = data if isinstance(data, list) else data.get('data', [])
    results = []
    
    # Tentar diferentes nomes de campo
    field_names = ['crash_point', 'result', 'value', 'outcome', 'roll']
    
    for record in records:
        for field in field_names:
            if field in record:
                results.append(record[field])
                break
    
    return results

# Usar
# results = extract_results(data)
# print(f"Resultados: {results[:10]}")
```

---

## 6. Checklist de Validação

```
✓ Endpoint retorna Status 200
✓ Content-Type é application/json
✓ JSON é válido (não corrompido)
✓ Estrutura tem campos esperados
✓ Timestamps são válidos
✓ Valores numéricos são corretos
✓ Rate limiting está documentado
✓ Autenticação (se necessária) funciona
✓ Dados são atualizados em tempo real
✓ Fallback funciona quando API está down
```

---

## 7. Próxima Etapa: Integrar Bet365

Após validar Blaze:

1. Documentar os endpoints reais
2. Criar arquivo `bet365_client.py` baseado em `blaze_client.py`
3. Adaptar:
   - URL base
   - Headers de autenticação
   - Estrutura de resposta
   - Nomes de campos
4. Testar com endpoints de teste Bet365
5. Integrar ao `main.py`

---

## Links Úteis

- [Documentação requests](https://docs.python-requests.org/)
- [Testing in Python](https://pytest.readthedocs.io/)
- [HTTP Status Codes](https://httpwg.org/specs/rfc9110.html#status.codes)

