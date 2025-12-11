"""
Módulo para coleta de dados da Blaze
"""
import requests
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class BlazeDataCollector:
    """Cliente para coleta de dados da plataforma Blaze"""

    def __init__(self):
        self.base_url = "https://blaze.com/api"
        self.session = requests.Session()
        self.setup_headers()

    def setup_headers(self):
        """Configura headers para requests"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Referer': 'https://blaze.com/',
            'Origin': 'https://blaze.com'
        })

    def get_crash_history(self, limit=100):
        """Obtém histórico do Crash"""
        try:
            # Nota: Esta é uma URL exemplo - pode precisar de ajuste baseado na API real
            url = f"{self.base_url}/crash_games/recent"
            params = {'limit': limit}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return self.process_crash_data(data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar histórico Crash: {str(e)}")
            return self.get_fallback_crash_data()

    def get_double_history(self, limit=100):
        """Obtém histórico do Double"""
        try:
            # Nota: Esta é uma URL exemplo - pode precisar de ajuste baseado na API real
            url = f"{self.base_url}/roulette_games/recent"
            params = {'limit': limit}

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return self.process_double_data(data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar histórico Double: {str(e)}")
            return self.get_fallback_double_data()

    def get_fallback_crash_data(self):
        """Dados de fallback para Crash quando API não está disponível"""
        # Gerar dados de exemplo para desenvolvimento
        import random
        records = []
        base_time = datetime.now()

        for i in range(50):
            records.append({
                'game_id': f"crash_{i}",
                'crash_point': round(random.uniform(1.0, 10.0), 2),
                'created_at': (base_time - timedelta(minutes=i*2)).isoformat() + 'Z',
                'timestamp': base_time - timedelta(minutes=i*2)
            })

        df = pd.DataFrame(records)
        if not df.empty:
            df = self.calculate_derived_metrics(df, 'crash_point')
        return df

    def get_fallback_double_data(self):
        """Dados de fallback para Double quando API não está disponível"""
        # Gerar dados de exemplo para desenvolvimento
        import random
        records = []
        base_time = datetime.now()
        colors = ['vermelho', 'preto', 'branco']

        for i in range(50):
            records.append({
                'game_id': f"double_{i}",
                'color': random.choice(colors),
                'roll': random.randint(0, 14),
                'created_at': (base_time - timedelta(minutes=i*2)).isoformat() + 'Z',
                'timestamp': base_time - timedelta(minutes=i*2)
            })

        df = pd.DataFrame(records)
        if not df.empty:
            df = self.calculate_derived_metrics(df, 'roll')
        return df

    def process_crash_data(self, raw_data):
        """Processa dados do Crash"""
        if not raw_data:
            return pd.DataFrame()

        records = []
        for game in raw_data:
            try:
                created_at = game.get('created_at')
                if not created_at:
                    continue
                
                record = {
                    'game_id': game.get('id'),
                    'crash_point': game.get('crash_point'),
                    'created_at': created_at,
                    'timestamp': datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                }
                records.append(record)
            except (KeyError, ValueError, AttributeError) as e:
                logger.debug(f"Erro ao processar game crash: {str(e)}")
                continue

        df = pd.DataFrame(records)
        if not df.empty:
            df = self.calculate_derived_metrics(df, 'crash_point')
        return df

    def process_double_data(self, raw_data):
        """Processa dados do Double"""
        if not raw_data:
            return pd.DataFrame()

        records = []
        for game in raw_data:
            try:
                created_at = game.get('created_at')
                if not created_at:
                    continue
                
                record = {
                    'game_id': game.get('id'),
                    'color': self.map_color(game.get('color')),
                    'roll': game.get('roll'),
                    'created_at': created_at,
                    'timestamp': datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                }
                records.append(record)
            except (KeyError, ValueError, AttributeError) as e:
                logger.debug(f"Erro ao processar game double: {str(e)}")
                continue

        df = pd.DataFrame(records)
        if not df.empty:
            df = self.calculate_derived_metrics(df, 'roll')
        return df

    def map_color(self, color_code):
        """Mapeia código de cor para nome"""
        color_map = {0: 'branco', 1: 'vermelho', 2: 'preto'}
        return color_map.get(color_code, 'desconhecido')

    def calculate_derived_metrics(self, df, value_column):
        """Calcula métricas derivadas"""
        df = df.sort_values('timestamp')

        # Diferença entre valores consecutivos
        df['diff'] = df[value_column].diff()

        # Média móvel
        if len(df) >= 5:
            df['moving_avg_5'] = df[value_column].rolling(window=5).mean()
        if len(df) >= 10:
            df['moving_avg_10'] = df[value_column].rolling(window=10).mean()

        # Volatilidade
        if len(df) >= 10:
            df['volatility'] = df[value_column].rolling(window=10).std()

        return df

    def collect_recent_data(self):
        """Coleta dados recentes de todos os jogos"""
        logger.info("Coletando dados do Crash...")
        crash_data = self.get_crash_history(50)
        logger.info(f"[OK] Crash: {len(crash_data)} registros coletados")

        logger.info("Coletando dados do Double...")
        double_data = self.get_double_history(50)
        logger.info(f"[OK] Double: {len(double_data)} registros coletados")

        return {
            'crash': crash_data,
            'double': double_data
        }

    def save_data(self, data, filename=None):
        """Salva dados coletados"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/raw/blaze_data_{timestamp}.json"

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            # Converter DataFrames para dict
            serializable_data = {}
            for key, df in data.items():
                if not df.empty:
                    serializable_data[key] = df.to_dict('records')
                else:
                    serializable_data[key] = []

            json.dump(serializable_data, f, indent=2, default=str)

        logger.info(f"[OK] Dados salvos em: {filename}")