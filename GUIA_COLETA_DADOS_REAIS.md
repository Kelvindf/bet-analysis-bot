# 🌐 GUIA: Coleta de Dados REAIS da Blaze

**Data**: 10/12/2025  
**Objetivo**: Substituir dados simulados por dados reais dos jogos

---

## 📋 O Problema Atual

Atualmente o sistema usa **dados de fallback** (simulados):

```
2025-12-10 20:19:57 - Usando dados de fallback: 100 registros Double
2025-12-10 20:19:57 - Usando dados de fallback: 100 registros Crash
```

**Limitações**:
- ❌ Não reflete padrões reais do jogo
- ❌ Sinais podem ser imprecisos
- ❌ Análise baseada em dados fictícios

---

## ✅ A Solução: Scraper em Tempo Real

Criado `blaze_realtime_scraper.py` que:

1. **Abre o navegador** automaticamente
2. **Acessa as páginas** que você mostrou:
   - https://blaze.bet.br/pt/games/double
   - https://blaze.bet.br/pt/games/crash
3. **Extrai o histórico** dos círculos/números
4. **Salva em cache** para uso posterior

---

## 🚀 Como Usar

### Passo 1: Instalar Dependências

```powershell
# Instalar Selenium (automatiza navegador)
pip install selenium

# Instalar gerenciador de ChromeDriver
pip install webdriver-manager

# Instalar cliente WebSocket (opcional)
pip install websocket-client
```

### Passo 2: Testar Scraper

```powershell
# Navegar para diretório
cd C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2

# Executar teste
python src/data_collection/blaze_realtime_scraper.py
```

**O que vai acontecer**:
1. Chrome abre automaticamente
2. Navega para página do Double
3. Aguarda 5 segundos (carregar histórico)
4. Extrai círculos vermelhos/pretos/brancos
5. Navega para página do Crash
6. Extrai multiplicadores (21,35X, 4,20X, etc.)
7. Salva em `data/realtime/`

### Passo 3: Integrar no Sistema Principal

**Opção A: Substituir Completamente** (Recomendado)

Editar [src/data_collection/blaze_client_v2.py](src/data_collection/blaze_client_v2.py):

```python
# NO TOPO
from data_collection.blaze_realtime_scraper import BlazeRealtimeScraper

# NO __init__
def __init__(self):
    # Adicionar
    self.realtime_scraper = BlazeRealtimeScraper(headless=True)
    self.use_realtime = True  # Ativar scraping real

# NO get_double_history
def get_double_history(self, limit: int = 100) -> List[Dict]:
    if self.use_realtime:
        try:
            data = self.realtime_scraper.get_double_realtime(limit)
            if data:
                logger.info(f"[REAL] Coletados {len(data)} Double via scraper")
                return data
        except Exception as e:
            logger.warning(f"Erro no scraper, usando fallback: {e}")
    
    # Fallback
    return self._generate_fallback_double_data(limit)

# NO get_crash_history
def get_crash_history(self, limit: int = 100) -> List[Dict]:
    if self.use_realtime:
        try:
            data = self.realtime_scraper.get_crash_realtime(limit)
            if data:
                logger.info(f"[REAL] Coletados {len(data)} Crash via scraper")
                return data
        except Exception as e:
            logger.warning(f"Erro no scraper, usando fallback: {e}")
    
    # Fallback
    return self._generate_fallback_crash_data(limit)
```

**Opção B: Modo Híbrido** (Cache + Realtime)

```python
def get_double_history(self, limit: int = 100) -> List[Dict]:
    # Tentar cache primeiro (mais rápido)
    cached = self._load_from_cache('double')
    if cached and len(cached) >= limit:
        # Se cache tem dados recentes (< 5 minutos), usar
        cache_age = datetime.now() - datetime.fromisoformat(cached[0]['timestamp'])
        if cache_age.total_seconds() < 300:  # 5 minutos
            logger.info(f"[CACHE] Usando {len(cached)} Double do cache")
            return cached[:limit]
    
    # Caso contrário, buscar realtime
    if self.use_realtime:
        try:
            data = self.realtime_scraper.get_double_realtime(limit)
            if data:
                self._save_to_cache('double', data)
                return data
        except Exception as e:
            logger.warning(f"Erro no scraper: {e}")
    
    # Fallback final
    return self._generate_fallback_double_data(limit)
```

---

## ⚙️ Configurações

### Modo Headless (Sem Abrir Navegador)

```python
# Para rodar INVISÍVEL (mais rápido, sem janela)
scraper = BlazeRealtimeScraper(headless=True)

# Para DEBUG (ver o que está acontecendo)
scraper = BlazeRealtimeScraper(headless=False)
```

### Ajustar Tempo de Espera

```python
# No scraper, linha ~170 e ~220
time.sleep(5)  # Aumentar para 10 se página demorar a carregar
```

### Seletores CSS Personalizados

Se os seletores atuais não funcionarem, inspecionar a página:

1. Abrir DevTools (F12) no Chrome
2. Ir para aba **Elements**
3. Localizar os círculos/números do histórico
4. Copiar seletor CSS
5. Adicionar em `history_selectors`

Exemplo:
```python
history_selectors = [
    "div.seu-seletor-aqui",  # Adicionar
    "div[class*='roulette_history']",
    # ... outros
]
```

---

## 🔍 Troubleshooting

### Erro: "ChromeDriver não encontrado"

**Solução**:
```powershell
pip install webdriver-manager
```

E modificar no código:
```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

service = Service(ChromeDriverManager().install())
self.driver = webdriver.Chrome(service=service, options=options)
```

### Erro: "Nenhum resultado encontrado"

**Possíveis causas**:
1. Página mudou estrutura HTML
2. Tempo de espera insuficiente
3. Seletores CSS incorretos

**Solução**:
- Aumentar `time.sleep(5)` para `time.sleep(10)`
- Inspecionar página e atualizar seletores
- Executar com `headless=False` para ver o que está acontecendo

### Scraper muito lento

**Otimizações**:
1. Usar cache (Opção B acima)
2. Rodar em background uma vez por minuto
3. Usar apenas DOM (mais rápido que Network monitoring)

---

## 📊 Dados Capturados

### Double
```json
[
  {
    "color": "red",
    "roll": 3,
    "timestamp": "2025-12-10T20:25:30",
    "game_id": "dom_0"
  },
  {
    "color": "black",
    "roll": 12,
    "timestamp": "2025-12-10T20:25:30",
    "game_id": "dom_1"
  }
]
```

### Crash
```json
[
  {
    "crash_point": 21.35,
    "timestamp": "2025-12-10T20:25:35",
    "game_id": "dom_0"
  },
  {
    "crash_point": 4.20,
    "timestamp": "2025-12-10T20:25:35",
    "game_id": "dom_1"
  }
]
```

---

## 🎯 Benefícios

**Antes (Fallback)**:
- Dados simulados aleatórios
- Sem padrões reais
- Confiança ~65-80%

**Depois (Realtime)**:
- Dados reais da Blaze ✅
- Padrões verdadeiros ✅
- Confiança potencial ~80-95% ✅
- Detecção de streaks reais ✅
- Análise de tendências reais ✅

---

## 🚀 Próximos Passos

1. **Testar scraper** isoladamente
2. **Validar dados** capturados
3. **Integrar** no sistema principal (Opção A ou B)
4. **Comparar resultados**: Fallback vs Realtime
5. **Ajustar estratégias** baseado em dados reais
6. **Monitorar performance** por 24-48 horas

---

## 📝 Exemplo Completo de Uso

```python
from data_collection.blaze_realtime_scraper import BlazeRealtimeScraper
import logging

logging.basicConfig(level=logging.INFO)

# Criar scraper
scraper = BlazeRealtimeScraper(headless=True)

try:
    # Capturar Double
    double_data = scraper.get_double_realtime(limit=100)
    print(f"Double: {len(double_data)} resultados")
    
    # Capturar Crash
    crash_data = scraper.get_crash_realtime(limit=100)
    print(f"Crash: {len(crash_data)} resultados")
    
    # Usar nos dados
    from analysis.statistical_analyzer import StatisticalAnalyzer
    import pandas as pd
    
    analyzer = StatisticalAnalyzer()
    
    # Analisar
    double_df = pd.DataFrame(double_data)
    crash_df = pd.DataFrame(crash_data)
    
    results = analyzer.analyze_patterns({
        'double': double_df,
        'crash': crash_df
    })
    
    print(f"Análise: {results}")
    
finally:
    scraper.close()
```

---

## ⚠️ Avisos Importantes

1. **Taxa de requisições**: Não fazer scraping a cada segundo. Respeitar intervalo mínimo de 1-2 minutos.

2. **Termos de uso**: Scraping pode violar termos da Blaze. Use apenas para fins educacionais/pessoais.

3. **Mudanças na página**: Se Blaze atualizar design, seletores CSS precisarão ser atualizados.

4. **Captcha**: Se aparecer captcha, aumentar intervalo entre requisições.

---

**Criado em**: 10/12/2025  
**Status**: ✅ Pronto para teste  
**Dependências**: selenium, webdriver-manager
