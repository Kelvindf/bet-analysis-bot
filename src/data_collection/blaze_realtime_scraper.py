"""
Blaze Real-Time Scraper
========================

Captura dados REAIS da Blaze usando:
1. Selenium (navegador automatizado)
2. Interceptação de Network Requests
3. WebSocket listeners
4. DOM parsing

Funciona com as páginas que você abriu:
- https://blaze.bet.br/pt/games/double
- https://blaze.bet.br/pt/games/crash
"""

import logging
import time
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class BlazeRealtimeScraper:
    """
    Scraper que captura dados reais da Blaze em tempo real
    
    Métodos:
    - WebSocket: Intercepta mensagens websocket da Blaze
    - Network: Monitora requisições XHR/Fetch
    - DOM: Extrai do HTML renderizado
    """
    
    def __init__(self, headless: bool = True):
        """
        Inicializa scraper
        
        Args:
            headless: Se True, roda sem abrir navegador visível
        """
        self.headless = headless
        self.driver = None
        self.double_history = []
        self.crash_history = []
        self.websocket_data = []
        
        # URLs
        self.urls = {
            'double': 'https://blaze.bet.br/pt/games/double',
            'crash': 'https://blaze.bet.br/pt/games/crash'
        }
        
        # Cache
        self.cache_dir = Path(__file__).parent.parent.parent / 'data' / 'realtime'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("[Blaze Realtime Scraper] Inicializado")
    
    def setup_driver(self):
        """Configura Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Opções do Chrome
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Habilitar logging de performance (captura network)
            options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_cdp_cmd('Network.enable', {})
            
            logger.info("[OK] WebDriver configurado")
            return True
            
        except ImportError:
            logger.error("Selenium não instalado. Execute: pip install selenium")
            return False
        except Exception as e:
            logger.error(f"Erro ao configurar WebDriver: {str(e)}")
            return False
    
    def capture_network_requests(self) -> List[Dict]:
        """Captura requisições de rede (XHR/Fetch) que trazem dados dos jogos"""
        try:
            logs = self.driver.get_log('performance')
            requests_data = []
            
            for log in logs:
                try:
                    message = json.loads(log['message'])['message']
                    
                    # Procurar por requisições relevantes
                    if message['method'] == 'Network.responseReceived':
                        response = message['params']['response']
                        url = response.get('url', '')
                        
                        # Filtrar apenas URLs de dados dos jogos
                        if any(keyword in url.lower() for keyword in ['double', 'crash', 'history', 'recent', 'api', 'websocket']):
                            requests_data.append({
                                'url': url,
                                'status': response.get('status'),
                                'timestamp': datetime.now().isoformat()
                            })
                            logger.debug(f"[Network] Capturado: {url}")
                
                except Exception as e:
                    continue
            
            return requests_data
            
        except Exception as e:
            logger.error(f"Erro ao capturar network: {str(e)}")
            return []
    
    def scrape_double_from_dom(self) -> List[Dict]:
        """
        Extrai histórico do Double diretamente do DOM
        
        O histórico aparece como círculos com classes tipo:
        - 'red' (vermelho)
        - 'black' (preto)
        - 'white' (branco)
        """
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Aguardar carregamento
            time.sleep(3)
            
            # Buscar elementos do histórico
            # Na screenshot vejo "GIROS ANTERIORES" com círculos
            history_selectors = [
                "div[class*='roulette_history']",
                "div[class*='history']",
                "div[class*='previous']",
                "div[class*='giros']",
                "[data-testid='history']",
                ".history-item",
                ".roulette-result"
            ]
            
            double_data = []
            
            for selector in history_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"[Double DOM] Encontrado {len(elements)} elementos com '{selector}'")
                        
                        for i, elem in enumerate(elements[:100]):  # Limitar a 100
                            try:
                                # Extrair classes
                                classes = elem.get_attribute('class') or ''
                                text = elem.text
                                
                                # Detectar cor
                                color = 'unknown'
                                if 'red' in classes.lower() or 'vermelho' in classes.lower():
                                    color = 'red'
                                elif 'black' in classes.lower() or 'preto' in classes.lower():
                                    color = 'black'
                                elif 'white' in classes.lower() or 'branco' in classes.lower():
                                    color = 'white'
                                
                                # Tentar extrair número
                                roll = None
                                if text.isdigit():
                                    roll = int(text)
                                
                                if color != 'unknown' or roll is not None:
                                    double_data.append({
                                        'color': color,
                                        'roll': roll,
                                        'timestamp': datetime.now().isoformat(),
                                        'game_id': f"dom_{i}"
                                    })
                            
                            except Exception as e:
                                continue
                
                except Exception as e:
                    continue
            
            if double_data:
                logger.info(f"[OK] Capturados {len(double_data)} resultados do Double via DOM")
                return double_data
            else:
                logger.warning("[Double DOM] Nenhum resultado encontrado")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao extrair Double do DOM: {str(e)}")
            return []
    
    def scrape_crash_from_dom(self) -> List[Dict]:
        """
        Extrai histórico do Crash diretamente do DOM
        
        Na screenshot vejo valores como:
        21,35X, 4,20X, 1,09X, etc.
        """
        try:
            from selenium.webdriver.common.by import By
            
            time.sleep(3)
            
            # Buscar histórico de crash
            crash_selectors = [
                "div[class*='crash_history']",
                "div[class*='history']",
                "div[class*='previous']",
                "div[class*='anterior']",
                "[data-testid='crash-history']",
                ".crash-result",
                ".history-value"
            ]
            
            crash_data = []
            
            for selector in crash_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"[Crash DOM] Encontrado {len(elements)} elementos com '{selector}'")
                        
                        for i, elem in enumerate(elements[:100]):
                            try:
                                text = elem.text.strip()
                                
                                # Procurar por padrão de multiplicador: "X.XXX" ou "X,XXX"
                                import re
                                match = re.search(r'([\d,\.]+)x', text.lower())
                                
                                if match:
                                    crash_point_str = match.group(1).replace(',', '.')
                                    try:
                                        crash_point = float(crash_point_str)
                                        
                                        crash_data.append({
                                            'crash_point': crash_point,
                                            'timestamp': datetime.now().isoformat(),
                                            'game_id': f"dom_{i}"
                                        })
                                    except ValueError:
                                        continue
                            
                            except Exception as e:
                                continue
                
                except Exception as e:
                    continue
            
            if crash_data:
                logger.info(f"[OK] Capturados {len(crash_data)} resultados do Crash via DOM")
                return crash_data
            else:
                logger.warning("[Crash DOM] Nenhum resultado encontrado")
                return []
                
        except Exception as e:
            logger.error(f"Erro ao extrair Crash do DOM: {str(e)}")
            return []
    
    def get_double_realtime(self, limit: int = 100) -> List[Dict]:
        """
        Captura dados REAIS do Double
        
        Returns:
            Lista de dicionários com 'color', 'roll', 'timestamp'
        """
        try:
            if not self.driver:
                if not self.setup_driver():
                    logger.error("Não foi possível configurar WebDriver")
                    return []
            
            # Navegar para página do Double
            logger.info(f"[Double] Navegando para {self.urls['double']}...")
            self.driver.get(self.urls['double'])
            
            # Aguardar carregamento
            time.sleep(5)
            
            # Capturar via DOM
            double_data = self.scrape_double_from_dom()
            
            # Capturar network requests
            network_data = self.capture_network_requests()
            
            # Salvar em cache
            if double_data:
                cache_file = self.cache_dir / 'double_realtime.json'
                with open(cache_file, 'w') as f:
                    json.dump(double_data[:limit], f, indent=2)
                logger.info(f"[OK] Cache salvo: {cache_file}")
            
            return double_data[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao capturar Double realtime: {str(e)}")
            return []
    
    def get_crash_realtime(self, limit: int = 100) -> List[Dict]:
        """
        Captura dados REAIS do Crash
        
        Returns:
            Lista de dicionários com 'crash_point', 'timestamp'
        """
        try:
            if not self.driver:
                if not self.setup_driver():
                    logger.error("Não foi possível configurar WebDriver")
                    return []
            
            # Navegar para página do Crash
            logger.info(f"[Crash] Navegando para {self.urls['crash']}...")
            self.driver.get(self.urls['crash'])
            
            # Aguardar carregamento
            time.sleep(5)
            
            # Capturar via DOM
            crash_data = self.scrape_crash_from_dom()
            
            # Salvar em cache
            if crash_data:
                cache_file = self.cache_dir / 'crash_realtime.json'
                with open(cache_file, 'w') as f:
                    json.dump(crash_data[:limit], f, indent=2)
                logger.info(f"[OK] Cache salvo: {cache_file}")
            
            return crash_data[:limit]
            
        except Exception as e:
            logger.error(f"Erro ao capturar Crash realtime: {str(e)}")
            return []
    
    def close(self):
        """Fecha o navegador"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("[OK] WebDriver fechado")
            except Exception as e:
                logger.error(f"Erro ao fechar driver: {str(e)}")


# ============================================================
# ALTERNATIVA: Captura via Browser DevTools Protocol
# ============================================================

class BlazeDevToolsScraper:
    """
    Scraper que usa Chrome DevTools Protocol
    Mais leve que Selenium, captura WebSocket messages
    """
    
    def __init__(self):
        self.ws_messages = []
        logger.info("[Blaze DevTools Scraper] Inicializado")
    
    def connect_websocket(self):
        """Conecta ao WebSocket da Blaze para receber dados em tempo real"""
        try:
            import websocket
            
            # WebSocket da Blaze (descobrir via DevTools Network)
            ws_url = "wss://api.blaze.bet.br/ws"  # URL hipotética
            
            def on_message(ws, message):
                try:
                    data = json.loads(message)
                    self.ws_messages.append(data)
                    logger.debug(f"[WebSocket] Mensagem: {data}")
                except:
                    pass
            
            def on_error(ws, error):
                logger.error(f"[WebSocket] Erro: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                logger.info("[WebSocket] Conexão fechada")
            
            def on_open(ws):
                logger.info("[OK] WebSocket conectado")
            
            ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Rodar em thread separada
            import threading
            wst = threading.Thread(target=ws.run_forever)
            wst.daemon = True
            wst.start()
            
            return True
            
        except ImportError:
            logger.error("websocket-client não instalado. Execute: pip install websocket-client")
            return False
        except Exception as e:
            logger.error(f"Erro ao conectar WebSocket: {str(e)}")
            return False


# ============================================================
# HELPER: Instalação de dependências
# ============================================================

def install_dependencies():
    """Instala dependências necessárias"""
    import subprocess
    import sys
    
    packages = [
        'selenium',
        'webdriver-manager',
        'websocket-client'
    ]
    
    print("Instalando dependências para scraping realtime...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} instalado")
        except Exception as e:
            print(f"❌ Erro ao instalar {package}: {str(e)}")


if __name__ == "__main__":
    # Teste rápido
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("TESTE: Blaze Realtime Scraper")
    print("="*60)
    
    scraper = BlazeRealtimeScraper(headless=False)  # headless=False para ver o navegador
    
    try:
        # Capturar Double
        print("\n[1/2] Capturando Double...")
        double_data = scraper.get_double_realtime(limit=50)
        print(f"✅ Capturados {len(double_data)} resultados do Double")
        if double_data:
            print(f"Exemplo: {double_data[0]}")
        
        # Capturar Crash
        print("\n[2/2] Capturando Crash...")
        crash_data = scraper.get_crash_realtime(limit=50)
        print(f"✅ Capturados {len(crash_data)} resultados do Crash")
        if crash_data:
            print(f"Exemplo: {crash_data[0]}")
        
    finally:
        scraper.close()
    
    print("\n" + "="*60)
    print("✅ TESTE CONCLUÍDO")
    print("="*60)
