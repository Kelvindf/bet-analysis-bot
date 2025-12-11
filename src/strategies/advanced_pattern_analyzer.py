"""
Analisador Avançado de Padrões
================================

Melhorias nas estratégias:
1. Análise de Volume Dinâmico
2. Detecção de Tendências Multi-timeframe
3. Padrões de Sequência Avançados
4. Score de Confiança Adaptativo
5. Filtro de Volatilidade Inteligente

Uso:
    analyzer = AdvancedPatternAnalyzer()
    result = analyzer.analyze(historical_data)
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class PatternSignal:
    """Sinal avançado com contexto rico"""
    signal_type: str  # 'Vermelho', 'Preto', 'Branco'
    confidence: float  # 0.0 - 1.0
    strength: str  # 'FRACO', 'MODERADO', 'FORTE', 'MUITO_FORTE'
    
    # Análises que suportam o sinal
    volume_score: float
    trend_score: float
    sequence_score: float
    volatility_score: float
    
    # Contexto
    current_streak: int
    expected_reversal: bool
    risk_level: str  # 'BAIXO', 'MEDIO', 'ALTO'
    
    # Recomendações
    suggested_stake: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    
    # Timestamp
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'signal_type': self.signal_type,
            'confidence': round(self.confidence, 3),
            'strength': self.strength,
            'volume_score': round(self.volume_score, 3),
            'trend_score': round(self.trend_score, 3),
            'sequence_score': round(self.sequence_score, 3),
            'volatility_score': round(self.volatility_score, 3),
            'current_streak': self.current_streak,
            'expected_reversal': self.expected_reversal,
            'risk_level': self.risk_level,
            'suggested_stake': round(self.suggested_stake, 2),
            'stop_loss': round(self.stop_loss, 2) if self.stop_loss else None,
            'take_profit': round(self.take_profit, 2) if self.take_profit else None,
            'timestamp': self.timestamp.isoformat()
        }


class AdvancedPatternAnalyzer:
    """Analisador avançado de padrões com múltiplos indicadores"""
    
    def __init__(self, min_confidence: float = 0.65):
        self.min_confidence = min_confidence
        self.history: List[PatternSignal] = []
        
        # Configurações adaptativas
        self.config = {
            'volume_weight': 0.25,
            'trend_weight': 0.30,
            'sequence_weight': 0.25,
            'volatility_weight': 0.20,
            
            # Thresholds
            'high_volume_threshold': 1.5,  # 1.5x média
            'trend_confirmation_periods': [5, 10, 20],
            'max_volatility': 0.15,  # 15% de volatilidade máxima
            'reversal_streak_min': 3,  # Min streak para esperar reversão
        }
        
        logger.info("[OK] AdvancedPatternAnalyzer inicializado")
    
    def analyze(self, data: pd.DataFrame) -> Optional[PatternSignal]:
        """
        Análise avançada com múltiplos indicadores
        
        Args:
            data: DataFrame com colunas ['color', 'roll', 'timestamp']
        
        Returns:
            PatternSignal ou None se não houver sinal válido
        """
        if data.empty or len(data) < 10:
            logger.warning("Dados insuficientes para análise avançada")
            return None
        
        try:
            # 1. Análise de Volume
            volume_score, volume_details = self._analyze_volume(data)
            
            # 2. Análise de Tendência
            trend_score, trend_details = self._analyze_trend(data)
            
            # 3. Análise de Sequência
            sequence_score, sequence_details = self._analyze_sequence(data)
            
            # 4. Análise de Volatilidade
            volatility_score, volatility_details = self._analyze_volatility(data)
            
            # 5. Calcular Confiança Final (Média Ponderada)
            confidence = self._calculate_weighted_confidence(
                volume_score, trend_score, sequence_score, volatility_score
            )
            
            # 6. Determinar Tipo de Sinal
            signal_type = self._determine_signal_type(data, trend_details, sequence_details)
            
            # 7. Avaliar Força do Sinal
            strength = self._evaluate_strength(confidence)
            
            # 8. Calcular Nível de Risco
            risk_level = self._calculate_risk_level(volatility_score, sequence_details)
            
            # 9. Sugestões de Gestão de Banca
            suggested_stake = self._calculate_stake(confidence, risk_level)
            stop_loss, take_profit = self._calculate_risk_reward(confidence)
            
            # Criar sinal
            signal = PatternSignal(
                signal_type=signal_type,
                confidence=confidence,
                strength=strength,
                volume_score=volume_score,
                trend_score=trend_score,
                sequence_score=sequence_score,
                volatility_score=volatility_score,
                current_streak=sequence_details.get('current_streak', 0),
                expected_reversal=sequence_details.get('expected_reversal', False),
                risk_level=risk_level,
                suggested_stake=suggested_stake,
                stop_loss=stop_loss,
                take_profit=take_profit,
                timestamp=datetime.now()
            )
            
            # Adicionar ao histórico
            self.history.append(signal)
            
            # Log detalhado
            logger.info(f"[SINAL AVANÇADO] {signal_type} - Confiança: {confidence:.1%}")
            logger.info(f"  Volume: {volume_score:.2f} | Tendência: {trend_score:.2f} | "
                       f"Sequência: {sequence_score:.2f} | Volatilidade: {volatility_score:.2f}")
            logger.info(f"  Força: {strength} | Risco: {risk_level} | Stake: {suggested_stake:.1%}")
            
            # Retornar apenas se confiança > mínimo
            if confidence >= self.min_confidence:
                return signal
            else:
                logger.warning(f"Sinal descartado - Confiança {confidence:.1%} < {self.min_confidence:.1%}")
                return None
                
        except Exception as e:
            logger.error(f"Erro na análise avançada: {str(e)}")
            return None
    
    def _analyze_volume(self, data: pd.DataFrame) -> Tuple[float, dict]:
        """
        Analisa volume de apostas
        
        Volume alto = Mais confiabilidade
        """
        details = {}
        
        # Simular volume baseado em frequência de jogos
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            time_diffs = data['timestamp'].diff().dt.total_seconds()
            avg_interval = time_diffs.mean()
            recent_interval = time_diffs.tail(5).mean()
            
            # Intervalo menor = Volume maior
            volume_ratio = avg_interval / (recent_interval + 1)
            details['volume_ratio'] = volume_ratio
            details['avg_interval_sec'] = avg_interval
            details['recent_interval_sec'] = recent_interval
        else:
            volume_ratio = 1.0
            details['volume_ratio'] = 1.0
        
        # Score: 0.0 - 1.0
        # Volume alto (ratio > threshold) = Score alto
        threshold = self.config['high_volume_threshold']
        if volume_ratio >= threshold:
            score = min(1.0, 0.7 + (volume_ratio - threshold) * 0.15)
            details['status'] = 'VOLUME_ALTO'
        elif volume_ratio >= 1.0:
            score = 0.5 + (volume_ratio - 1.0) * 0.4
            details['status'] = 'VOLUME_NORMAL'
        else:
            score = 0.3 + volume_ratio * 0.2
            details['status'] = 'VOLUME_BAIXO'
        
        return score, details
    
    def _analyze_trend(self, data: pd.DataFrame) -> Tuple[float, dict]:
        """
        Analisa tendências multi-timeframe
        
        Confirma tendência em múltiplos períodos
        """
        details = {}
        scores = []
        
        # Converter cores para valores numéricos
        color_map = {'red': 1, 'black': -1, 'white': 0}
        data['color_value'] = data['color'].map(
            lambda x: color_map.get(x.lower(), 0)
        )
        
        periods = self.config['trend_confirmation_periods']
        
        for period in periods:
            if len(data) >= period:
                recent = data.tail(period)
                trend_sum = recent['color_value'].sum()
                
                # Normalizar por período
                trend_normalized = trend_sum / period
                
                # Score baseado na força da tendência
                trend_score = abs(trend_normalized)
                scores.append(trend_score)
                
                details[f'trend_{period}'] = {
                    'sum': trend_sum,
                    'normalized': round(trend_normalized, 3),
                    'score': round(trend_score, 3)
                }
        
        # Média dos scores
        final_score = np.mean(scores) if scores else 0.5
        
        # Determinar direção dominante
        if scores:
            last_trend = data.tail(periods[0])['color_value'].sum()
            details['direction'] = 'RED' if last_trend > 0 else 'BLACK' if last_trend < 0 else 'NEUTRO'
        else:
            details['direction'] = 'NEUTRO'
        
        return final_score, details
    
    def _analyze_sequence(self, data: pd.DataFrame) -> Tuple[float, dict]:
        """
        Analisa padrões de sequência
        
        Detecta streaks e probabilidade de reversão
        """
        details = {}
        
        # Calcular streak atual
        current_color = data.iloc[-1]['color']
        current_streak = 1
        
        for i in range(len(data) - 2, -1, -1):
            if data.iloc[i]['color'] == current_color:
                current_streak += 1
            else:
                break
        
        details['current_color'] = current_color
        details['current_streak'] = current_streak
        
        # Streak longo sugere reversão iminente
        reversal_threshold = self.config['reversal_streak_min']
        expected_reversal = current_streak >= reversal_threshold
        details['expected_reversal'] = expected_reversal
        
        # Score baseado em probabilidade de reversão
        # Streaks longos têm maior probabilidade de reverter
        if current_streak >= 5:
            sequence_score = 0.85  # Muito provável reverter
        elif current_streak >= reversal_threshold:
            sequence_score = 0.70  # Provável reverter
        elif current_streak == 2:
            sequence_score = 0.55  # Pode continuar ou reverter
        else:
            sequence_score = 0.50  # Neutro
        
        details['sequence_score_explanation'] = (
            f"Streak de {current_streak} {current_color} - "
            f"{'Alta' if expected_reversal else 'Baixa'} probabilidade de reversão"
        )
        
        return sequence_score, details
    
    def _analyze_volatility(self, data: pd.DataFrame) -> Tuple[float, dict]:
        """
        Analisa volatilidade dos resultados
        
        Baixa volatilidade = Padrão mais previsível
        """
        details = {}
        
        # Calcular frequência de mudanças de cor
        data['color_changed'] = (data['color'] != data['color'].shift(1)).astype(int)
        change_rate = data['color_changed'].tail(20).mean()
        
        details['change_rate'] = change_rate
        details['stability'] = 1 - change_rate
        
        # Score: Baixa volatilidade = Alto score
        # Ideal: 30-50% de mudanças (padrão estável mas não rígido)
        if 0.3 <= change_rate <= 0.5:
            volatility_score = 0.85  # Ideal
        elif 0.2 <= change_rate < 0.3 or 0.5 < change_rate <= 0.6:
            volatility_score = 0.70  # Bom
        elif change_rate < 0.2 or change_rate > 0.6:
            volatility_score = 0.50  # Muito volátil ou muito estável
        else:
            volatility_score = 0.40  # Errático
        
        max_vol = self.config['max_volatility']
        if change_rate > (1 - max_vol) or change_rate < max_vol:
            details['status'] = 'ALTA_VOLATILIDADE'
        else:
            details['status'] = 'VOLATILIDADE_NORMAL'
        
        return volatility_score, details
    
    def _calculate_weighted_confidence(self, volume: float, trend: float, 
                                      sequence: float, volatility: float) -> float:
        """Calcula confiança final com pesos"""
        weights = self.config
        
        confidence = (
            volume * weights['volume_weight'] +
            trend * weights['trend_weight'] +
            sequence * weights['sequence_weight'] +
            volatility * weights['volatility_weight']
        )
        
        # Normalizar para 0.0 - 1.0
        return min(1.0, max(0.0, confidence))
    
    def _determine_signal_type(self, data: pd.DataFrame, 
                               trend_details: dict, 
                               sequence_details: dict) -> str:
        """Determina o tipo de sinal a sugerir"""
        current_color = sequence_details['current_color']
        expected_reversal = sequence_details['expected_reversal']
        trend_direction = trend_details.get('direction', 'NEUTRO')
        
        # Se espera reversão, sugerir cor oposta
        if expected_reversal:
            if current_color.lower() == 'red':
                return 'Preto'
            elif current_color.lower() == 'black':
                return 'Vermelho'
            else:
                return 'Vermelho' if trend_direction == 'BLACK' else 'Preto'
        
        # Caso contrário, seguir a tendência
        if trend_direction == 'RED':
            return 'Vermelho'
        elif trend_direction == 'BLACK':
            return 'Preto'
        else:
            # Neutro: escolher baseado no padrão histórico
            color_counts = data['color'].tail(20).value_counts()
            if 'red' in color_counts and color_counts.get('red', 0) > color_counts.get('black', 0):
                return 'Vermelho'
            else:
                return 'Preto'
    
    def _evaluate_strength(self, confidence: float) -> str:
        """Avalia força do sinal"""
        if confidence >= 0.85:
            return 'MUITO_FORTE'
        elif confidence >= 0.75:
            return 'FORTE'
        elif confidence >= 0.65:
            return 'MODERADO'
        else:
            return 'FRACO'
    
    def _calculate_risk_level(self, volatility_score: float, 
                              sequence_details: dict) -> str:
        """Calcula nível de risco"""
        current_streak = sequence_details.get('current_streak', 0)
        
        # Volatilidade alta ou streak muito longo = Risco alto
        if volatility_score < 0.5 or current_streak > 6:
            return 'ALTO'
        elif volatility_score < 0.7 or current_streak >= 4:
            return 'MEDIO'
        else:
            return 'BAIXO'
    
    def _calculate_stake(self, confidence: float, risk_level: str) -> float:
        """
        Calcula stake sugerido (% da banca)
        
        Kelly Criterion simplificado
        """
        base_stake = 0.02  # 2% base
        
        # Ajustar por confiança
        confidence_multiplier = 1 + (confidence - 0.65) * 2
        
        # Ajustar por risco
        risk_multipliers = {
            'BAIXO': 1.5,
            'MEDIO': 1.0,
            'ALTO': 0.5
        }
        risk_multiplier = risk_multipliers.get(risk_level, 1.0)
        
        stake = base_stake * confidence_multiplier * risk_multiplier
        
        # Limitar entre 1% e 5%
        return min(0.05, max(0.01, stake))
    
    def _calculate_risk_reward(self, confidence: float) -> Tuple[Optional[float], Optional[float]]:
        """Calcula stop-loss e take-profit"""
        # Para apostas binárias, adaptar conceito
        # Stop-loss: quantas perdas consecutivas antes de parar
        # Take-profit: quantos ganhos consecutivos
        
        if confidence >= 0.80:
            stop_loss = 2.0  # Permitir 2 perdas
            take_profit = 5.0  # Alvo 5 ganhos
        elif confidence >= 0.70:
            stop_loss = 1.5
            take_profit = 3.0
        else:
            stop_loss = 1.0
            take_profit = 2.0
        
        return stop_loss, take_profit
    
    def get_performance_stats(self) -> dict:
        """Retorna estatísticas de performance"""
        if not self.history:
            return {'total_signals': 0}
        
        df = pd.DataFrame([s.to_dict() for s in self.history])
        
        return {
            'total_signals': len(self.history),
            'avg_confidence': df['confidence'].mean(),
            'strength_distribution': df['strength'].value_counts().to_dict(),
            'risk_distribution': df['risk_level'].value_counts().to_dict(),
            'avg_suggested_stake': df['suggested_stake'].mean(),
            'signals_by_type': df['signal_type'].value_counts().to_dict()
        }
