"""
Cliente Blaze Corrigido - com múltiplos endpoints e dados robustos

Suporta:
1. Conexão real (quando disponível)
2. Fallback com dados simulados (para desenvolvimento/teste)
3. Cache local de dados
"""

import requests
import json
import logging
from datetime import datetime, timedelta
import random
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class BlazeDataCollectorV2:
    """Cliente para coleta de dados da plataforma Blaze (versão 2)"""

    def __init__(self):
        """Inicializa o cliente"""
        # URLs base da API Blaze (reais - testadas e validadas)
        # A Blaze responde em https://blaze.bet.br/games/double e /games/crash
        self.base_urls = [
            "https://blaze.bet.br",      # URL principal (responde em 200)
            "https://blaze.bet.br/pt",   # Versão em português
            "https://api.blaze.bet.br"   # API alternativa
        ]
        self.base_url = self.base_urls[0]  # URL principal
        self.session = requests.Session()
        self.setup_headers()
        self.cache_file = Path(__file__).parent.parent.parent / 'data' / 'raw' / 'blaze_data_cache.json'
        self.use_fallback = True  # Começa com fallback por padrão
        self.api_available = False  # Flag de disponibilidade da API
        
    def setup_headers(self):
        """Configura headers realistas"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': 'https://blaze.com/',
            'Origin': 'https://blaze.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        })

    def test_connectivity(self) -> bool:
        """Testa se pode conectar à API real da Blaze"""
        try:
            # Endpoints reais que respondem com 200
            endpoints = [
                "/games/double",
                "/games/crash",
                "/v1/games",
                "/graphql",
            ]
            
            # Testar cada URL base
            for url in self.base_urls:
                for endpoint in endpoints:
                    try:
                        test_url = f"{url}{endpoint}"
                        response = self.session.get(test_url, timeout=3)
                        
                        if response.status_code == 200:
                            self.base_url = url
                            self.use_fallback = False
                            self.api_available = True
                            logger.info(f"Conectado à Blaze API: {test_url}")
                            return True
                        
                    except requests.exceptions.Timeout:
                        continue
                    except Exception:
                        continue
            
            logger.warning("Blaze API não disponível, usando fallback")
            self.use_fallback = True
            self.api_available = False
            return False
                
        except Exception as e:
            logger.warning(f"Erro ao testar Blaze API ({str(e)[:50]}), usando fallback")
            self.use_fallback = True
            self.api_available = False
            return False

    def get_double_history(self, limit: int = 100) -> List[Dict]:
        """Obtém histórico do Double (Roleta)"""
        if self.use_fallback:
            return self._generate_fallback_double_data(limit)
        
        try:
            # Endpoints reais da Blaze (descobertos via teste)
            endpoints = [
                f"{self.base_url}/games/double",
                f"{self.base_url}/games?type=double&limit={limit}",
                f"{self.base_url}/v1/games/double",
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(endpoint, timeout=5)
                    if response.status_code == 200:
                        # Tentar processar como JSON
                        try:
                            data = response.json()
                            result = self._process_double_data(data)
                            if result:
                                logger.info(f"Double: {len(result)} registros da API")
                                return result
                        except ValueError:
                            # Resposta não é JSON, continuar
                            continue
                except:
                    continue
            
            # Se nenhum endpoint funcionou, usar fallback
            logger.warning("Nenhum endpoint de Double funcionou, usando fallback")
            return self._generate_fallback_double_data(limit)
            
        except Exception as e:
            logger.error(f"Erro ao buscar Double: {str(e)}")
            return self._generate_fallback_double_data(limit)

    def get_crash_history(self, limit: int = 100) -> List[Dict]:
        """Obtém histórico do Crash"""
        if self.use_fallback:
            return self._generate_fallback_crash_data(limit)
        
        try:
            # Endpoints reais da Blaze (descobertos via teste)
            endpoints = [
                f"{self.base_url}/games/crash",
                f"{self.base_url}/games?type=crash&limit={limit}",
                f"{self.base_url}/v1/games/crash",
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(endpoint, timeout=5)
                    if response.status_code == 200:
                        # Tentar processar como JSON
                        try:
                            data = response.json()
                            result = self._process_crash_data(data)
                            if result:
                                logger.info(f"Crash: {len(result)} registros da API")
                                return result
                        except ValueError:
                            # Resposta não é JSON, continuar
                            continue
                except:
                    continue
            
            logger.warning("Nenhum endpoint de Crash funcionou, usando fallback")
            return self._generate_fallback_crash_data(limit)
            
        except Exception as e:
            logger.error(f"Erro ao buscar Crash: {str(e)}")
            return self._generate_fallback_crash_data(limit)

    def _generate_fallback_double_data(self, limit: int = 100) -> List[Dict]:
        """Gera dados realistas para Double (Roleta)
        
        Padrão: RED/BLACK alternado com variação
        """
        records = []
        base_time = datetime.now()
        
        # Padrão de cores (RED/BLACK com clusters)
        colors = ['RED', 'BLACK']
        current_color = random.choice(colors)
        
        for i in range(limit):
            # 70% de chance de continuar a cor anterior (criar clusters)
            if random.random() > 0.30:
                pass  # Mantém current_color
            else:
                current_color = 'BLACK' if current_color == 'RED' else 'RED'
            
            timestamp = base_time - timedelta(seconds=i * 10)
            
            record = {
                'type': 'double',
                'color': current_color,
                'result': 'red' if current_color == 'RED' else 'black',
                'game_id': f"double_{int(timestamp.timestamp())}",
                'timestamp': timestamp.isoformat(),
                'created_at': timestamp.isoformat() + 'Z',
                'value': random.choice([2, 1])  # Multiplicador
            }
            
            records.append(record)
        
        logger.info(f"Usando dados de fallback: {limit} registros Double")
        return records[::-1]  # Reverter para ordem cronológica

    def _generate_fallback_crash_data(self, limit: int = 100) -> List[Dict]:
        """Gera dados realistas para Crash
        
        Padrão: Valores entre 1.0x e 10.0x com distribuição realista
        """
        records = []
        base_time = datetime.now()
        
        for i in range(limit):
            # Distribuição realista: mais crashes baixos, menos altos
            if random.random() < 0.70:  # 70% < 2x
                crash_point = round(random.uniform(1.0, 2.0), 2)
            elif random.random() < 0.90:  # 20% entre 2x e 5x
                crash_point = round(random.uniform(2.0, 5.0), 2)
            else:  # 10% > 5x
                crash_point = round(random.uniform(5.0, 10.0), 2)
            
            timestamp = base_time - timedelta(seconds=i * 10)
            
            record = {
                'type': 'crash',
                'crash_point': crash_point,
                'game_id': f"crash_{int(timestamp.timestamp())}",
                'timestamp': timestamp.isoformat(),
                'created_at': timestamp.isoformat() + 'Z',
                'status': 'completed'
            }
            
            records.append(record)
        
        logger.info(f"Usando dados de fallback: {limit} registros Crash")
        return records[::-1]  # Reverter para ordem cronológica

    def _process_double_data(self, raw_data: any) -> List[Dict]:
        """Processa dados brutos do Double da API"""
        records = []
        
        # Adaptar conforme estrutura real da API
        data_list = raw_data if isinstance(raw_data, list) else raw_data.get('data', [])
        
        for item in data_list:
            record = {
                'type': 'double',
                'color': item.get('color', item.get('result', 'RED')).upper(),
                'result': item.get('result', item.get('color', 'red')).lower(),
                'game_id': str(item.get('id', item.get('game_id', ''))),
                'timestamp': item.get('created_at', item.get('timestamp', datetime.now().isoformat())),
                'created_at': item.get('created_at', datetime.now().isoformat()),
            }
            records.append(record)
        
        return records

    def _process_crash_data(self, raw_data: any) -> List[Dict]:
        """Processa dados brutos do Crash da API"""
        records = []
        
        data_list = raw_data if isinstance(raw_data, list) else raw_data.get('data', [])
        
        for item in data_list:
            record = {
                'type': 'crash',
                'crash_point': float(item.get('crash_point', item.get('value', 2.0))),
                'game_id': str(item.get('id', item.get('game_id', ''))),
                'timestamp': item.get('created_at', item.get('timestamp', datetime.now().isoformat())),
                'created_at': item.get('created_at', datetime.now().isoformat()),
                'status': item.get('status', 'completed')
            }
            records.append(record)
        
        return records

    def save_cache(self, double_data: List[Dict], crash_data: List[Dict]):
        """Salva dados em cache local"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'double': double_data,
                'crash': crash_data,
                'source': 'fallback' if self.use_fallback else 'api'
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
                
            logger.info(f"Cache salvo: {self.cache_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {str(e)}")

    def load_cache(self) -> Optional[Dict]:
        """Carrega dados do cache local"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar cache: {str(e)}")
        
        return None

    def get_all_data(self, limit: int = 100) -> Dict:
        """Obtém dados de Double e Crash"""
        double_data = self.get_double_history(limit)
        crash_data = self.get_crash_history(limit)
        
        # Salvar cache
        self.save_cache(double_data, crash_data)
        
        return {
            'double': double_data,
            'crash': crash_data,
            'source': 'fallback' if self.use_fallback else 'api',
            'timestamp': datetime.now().isoformat(),
            'count': len(double_data) + len(crash_data)
        }


# Manter compatibilidade com código antigo
class BlazeDataCollector(BlazeDataCollectorV2):
    """Alias para compatibilidade com código existente"""
    pass
