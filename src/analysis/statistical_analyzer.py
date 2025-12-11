"""
Módulo de análise estatística para geração de sinais
"""
import pandas as pd
import numpy as np
from scipy import stats
import logging
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class StatisticalAnalyzer:
    """Analisador estatístico para padrões de apostas"""

    def __init__(self):
        self.min_confidence = 0.65  # Confiança mínima para sinal

    def analyze_patterns(self, data):
        """Analisa padrões nos dados coletados"""
        analysis_results = {}

        try:
            # Análise do Crash
            if 'crash' in data and not data['crash'].empty:
                logger.info("Analisando padroes do Crash...")
                analysis_results['crash'] = self.analyze_crash_patterns(data['crash'])
                logger.info("[OK] Analise do Crash concluida")

            # Análise do Double
            if 'double' in data and not data['double'].empty:
                logger.info("Analisando padroes do Double...")
                analysis_results['double'] = self.analyze_double_patterns(data['double'])
                logger.info("[OK] Analise do Double concluida")

        except Exception as e:
            logger.error(f"Erro na analise de padroes: {str(e)}")

        return analysis_results

    def analyze_crash_patterns(self, df):
        """Analisa padrões específicos do Crash"""
        if df.empty or len(df) < 10:
            return {"error": "Dados insuficientes para análise"}

        analysis = {}

        try:
            # Estatísticas básicas
            analysis['basic_stats'] = {
                'mean': float(df['crash_point'].mean()),
                'median': float(df['crash_point'].median()),
                'std': float(df['crash_point'].std()),
                'min': float(df['crash_point'].min()),
                'max': float(df['crash_point'].max())
            }

            # Padrões de sequência
            analysis['sequences'] = self.analyze_crash_sequences(df)

            # Tendências temporais
            analysis['trends'] = self.analyze_trends(df, 'crash_point')

            # Anomalias
            analysis['anomalies'] = self.detect_anomalies(df, 'crash_point')

        except Exception as e:
            logger.error(f"Erro na análise do Crash: {str(e)}")
            analysis['error'] = str(e)

        return analysis

    def analyze_double_patterns(self, df):
        """Analisa padrões específicos do Double"""
        if df.empty or len(df) < 10:
            return {"error": "Dados insuficientes para análise"}

        analysis = {}

        try:
            # Frequência de cores
            color_counts = df['color'].value_counts()
            analysis['color_frequency'] = color_counts.to_dict()

            # Padrões de sequência de cores
            analysis['color_sequences'] = self.analyze_color_sequences(df)

            # Estatísticas dos números
            analysis['roll_stats'] = {
                'mean': float(df['roll'].mean()),
                'std': float(df['roll'].std()),
                'min': int(df['roll'].min()),
                'max': int(df['roll'].max())
            }

            # Probabilidades
            total = len(df)
            analysis['probabilities'] = {
                color: count / total for color, count in color_counts.items()
            }

        except Exception as e:
            logger.error(f"Erro na análise do Double: {str(e)}")
            analysis['error'] = str(e)

        return analysis

    def analyze_crash_sequences(self, df):
        """Analisa sequências no Crash"""
        sequences = {}

        # Identifica crashes baixos (menos que 2x)
        low_crashes = df[df['crash_point'] < 2.0]
        sequences['low_crash_count'] = len(low_crashes)
        sequences['low_crash_percentage'] = float(len(low_crashes) / len(df))

        # Verifica sequências de crashes baixos
        df['is_low'] = df['crash_point'] < 2.0
        sequences['current_low_streak'] = self.get_current_streak(df, 'is_low')

        # Sequências de crashes altos
        high_crashes = df[df['crash_point'] > 5.0]
        sequences['high_crash_count'] = len(high_crashes)
        sequences['high_crash_percentage'] = float(len(high_crashes) / len(df))

        return sequences

    def analyze_color_sequences(self, df):
        """Analisa sequências de cores no Double"""
        sequences = {}

        # Sequências de cores iguais
        df['color_shift'] = df['color'] != df['color'].shift(1)
        df['streak_id'] = df['color_shift'].cumsum()

        streaks = df.groupby('streak_id').agg({
            'color': 'first',
            'game_id': 'count'
        }).rename(columns={'game_id': 'streak_length'})

        sequences['current_streak'] = streaks.iloc[-1].to_dict() if not streaks.empty else {}
        sequences['max_streak'] = streaks.loc[streaks['streak_length'].idxmax()].to_dict() if not streaks.empty else {}
        sequences['all_streaks'] = streaks.to_dict('records')

        return sequences

    def analyze_trends(self, df, column):
        """Analisa tendências temporais"""
        trends = {}

        if len(df) >= 5:
            # Tendência linear recente
            recent_data = df.tail(5)
            x = np.arange(len(recent_data))
            y = recent_data[column].values

            slope, _, r_value, _, _ = stats.linregress(x, y)

            trends['recent_slope'] = float(slope)
            trends['recent_correlation'] = float(r_value)
            trends['trend_direction'] = 'alta' if slope > 0 else 'baixa' if slope < 0 else 'estável'

        return trends

    def detect_anomalies(self, df, column):
        """Detecta anomalias estatísticas"""
        anomalies = {}

        if len(df) >= 10:
            recent_data = df[column].tail(10).values
            if len(recent_data) >= 3:  # Mínimo para cálculo de z-score
                z_scores = np.abs(stats.zscore(recent_data))
                anomaly_indices = np.where(z_scores > 2)[0]

                anomalies['count'] = len(anomaly_indices)
                anomalies['positions'] = anomaly_indices.tolist()
                anomalies['values'] = recent_data[anomaly_indices].tolist() if len(anomaly_indices) > 0 else []

        return anomalies

    def get_current_streak(self, df, condition_column):
        """Calcula a sequência atual baseada em condição"""
        if df.empty:
            return 0

        current_streak = 0
        for i in range(len(df)-1, -1, -1):
            if df.iloc[i][condition_column]:
                current_streak += 1
            else:
                break

        return current_streak

    def generate_signals(self, analysis_results):
        """Gera sinais baseados na análise"""
        signals = []

        try:
            # Sinais para Crash
            if 'crash' in analysis_results and 'error' not in analysis_results['crash']:
                crash_signals = self.generate_crash_signals(analysis_results['crash'])
                signals.extend(crash_signals)

            # Sinais para Double
            if 'double' in analysis_results and 'error' not in analysis_results['double']:
                double_signals = self.generate_double_signals(analysis_results['double'])
                signals.extend(double_signals)

            logger.info(f"[*] {len(signals)} sinal(is) gerado(s)")

        except Exception as e:
            logger.error(f"Erro na geracao de sinais: {str(e)}")

        return signals

    def generate_crash_signals(self, crash_analysis):
        """Gera sinais específicos para Crash"""
        signals = []

        # Sinal baseado em sequência de crashes baixos
        sequences = crash_analysis.get('sequences', {})
        current_low_streak = sequences.get('current_low_streak', 0)

        if current_low_streak >= 3:
            confidence = min(0.7 + (current_low_streak * 0.1), 0.9)
            signals.append({
                'game': 'Crash',
                'signal': 'ALERTA_CRASH_BAIXO',
                'message': f"Sequência de {current_low_streak} crashes baixos consecutivos (< 2.0x)",
                'confidence': confidence,
                'timestamp': datetime.now()
            })

        # Sinal baseado em anomalia
        anomalies = crash_analysis.get('anomalies', {})
        if anomalies.get('count', 0) > 0:
            signals.append({
                'game': 'Crash',
                'signal': 'ANOMALIA_DETECTADA',
                'message': f"Detectadas {anomalies['count']} anomalias estatísticas recentes",
                'confidence': 0.75,
                'timestamp': datetime.now()
            })

        # Sinal baseado em tendência
        trends = crash_analysis.get('trends', {})
        if trends.get('recent_slope', 0) > 0.5:
            signals.append({
                'game': 'Crash',
                'signal': 'TENDENCIA_ALTA',
                'message': f"Tendência de alta detectada (slope: {trends['recent_slope']:.2f})",
                'confidence': 0.68,
                'timestamp': datetime.now()
            })

        return signals

    def generate_double_signals(self, double_analysis):
        """Gera sinais específicos para Double"""
        signals = []

        # Sinal baseado em sequência de cores
        sequences = double_analysis.get('color_sequences', {})
        current_streak = sequences.get('current_streak', {})
        streak_length = current_streak.get('streak_length', 0)
        streak_color = current_streak.get('color', '')

        if streak_length >= 4:
            confidence = min(0.6 + (streak_length * 0.08), 0.85)
            signals.append({
                'game': 'Double',
                'signal': 'SEQUENCIA_COR_LONGA',
                'message': f"Sequência de {streak_length} cores {streak_color} consecutivas",
                'confidence': confidence,
                'timestamp': datetime.now()
            })

        # Sinal baseado em frequência de cores
        color_freq = double_analysis.get('color_frequency', {})
        total_games = sum(color_freq.values())

        for color, count in color_freq.items():
            frequency = count / total_games
            if frequency < 0.2 and total_games >= 20:  # Cor sub-representada
                signals.append({
                    'game': 'Double',
                    'signal': 'COR_SUB_REPRESENTADA',
                    'message': f"Cor {color} apareceu apenas {count} vezes ({frequency:.1%}) - pode normalizar",
                    'confidence': 0.65,
                    'timestamp': datetime.now()
                })

        # Sinal baseado em probabilidades
        probabilities = double_analysis.get('probabilities', {})
        for color, prob in probabilities.items():
            if prob > 0.5 and total_games >= 15:  # Cor super-representada
                signals.append({
                    'game': 'Double',
                    'signal': 'COR_SUPER_REPRESENTADA',
                    'message': f"Cor {color} com frequência alta ({prob:.1%}) - possível reversão",
                    'confidence': 0.7,
                    'timestamp': datetime.now()
                })

        return signals