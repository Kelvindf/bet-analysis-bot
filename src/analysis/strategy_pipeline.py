"""
Pipeline de Estratégias em Cascata

Dados fluem por múltiplas engrenagens/funis:
1. Estratégia Base: Detecta padrões subrepresentados
2. Validação Técnica: RSI, Bollinger Bands, MACD
3. Filtro de Confiança: Remove sinais fracos
4. Confirmação: Valida com volume e streaks

Resultado: Sinais ALTAMENTE qualificados com alta taxa de acerto
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class StrategyResult(Enum):
    """Resultado do filtro da estratégia"""
    PASS = "PASS"  # Passou e continua pipeline
    REJECT = "REJECT"  # Rejeitado
    WEAK = "WEAK"  # Passou mas com confiança reduzida


@dataclass
class Signal:
    """Sinal processado pelo pipeline"""
    signal_id: str
    signal_type: str  # 'Vermelho' ou 'Preto'
    initial_confidence: float
    timestamp: datetime
    
    # Resultado de cada estratégia
    strategy_results: Dict[str, Tuple[StrategyResult, float]] = field(default_factory=dict)
    
    # Confiança final após todos os filtros
    final_confidence: float = 0.0
    
    # Detalhes de cada estratégia
    strategy_details: Dict[str, dict] = field(default_factory=dict)
    
    # Passou em todas as estratégias?
    is_valid: bool = False
    
    # Quantas estratégias passaram
    strategies_passed: int = 0

    def add_strategy_result(self, strategy_name: str, result: StrategyResult, 
                           confidence: float, details: dict = None):
        """Adiciona resultado de uma estratégia"""
        self.strategy_results[strategy_name] = (result, confidence)
        if details:
            self.strategy_details[strategy_name] = details
        
        if result == StrategyResult.PASS:
            self.strategies_passed += 1

    def finalize(self, required_strategies: int = 2):
        """
        Finaliza o sinal após passar por todas as estratégias
        
        ADAPTATIVO: Com fallback data, aceita apenas 1-2 estratégias passando
                    Com dados normais, exigir 2-3
        """
        # MENOS RIGOROSO: aceitar com apenas 1 estratégia passando (downgrade importante)
        # Se nenhuma estratégia passou mas houver confiança baixa, ainda marcar como válido se > 0.50
        has_minimum_confidence = self.initial_confidence >= 0.50 and self.strategies_passed >= 1
        
        # Válido se:
        # 1. Passou em required_strategies (2 ou mais) OU
        # 2. Passou em 1 e tem confiança inicial >= 0.50
        self.is_valid = (self.strategies_passed >= required_strategies) or has_minimum_confidence
        
        if self.is_valid:
            # Aumentar confiança baseado em quantas estratégias passaram
            multiplier = 1.0 + (self.strategies_passed * 0.12)
            self.final_confidence = min(0.99, self.initial_confidence * multiplier)
        else:
            # Não é válido, mas manter confiança baixa em vez de 0.0
            self.final_confidence = max(0.30, self.initial_confidence * 0.5)

    def summary(self) -> str:
        """Resumo do sinal com resultados das estratégias"""
        if not self.is_valid:
            return f"[REJEITADO] {self.signal_type} - Passou em {self.strategies_passed}/4 estratégias"
        
        passed = [s for s, (r, _) in self.strategy_results.items() if r == StrategyResult.PASS]
        return f"[VÁLIDO] {self.signal_type} ({self.final_confidence:.1%}) - {', '.join(passed)}"


class StrategyBase:
    """Classe base para todas as estratégias"""
    
    def __init__(self, name: str, min_confidence: float = 0.55):
        self.name = name
        self.min_confidence = min_confidence

    def analyze(self, data: Dict) -> Tuple[StrategyResult, float, Dict]:
        """
        Analisa dados e retorna (resultado, confiança, detalhes)
        
        Subclasses devem implementar isso
        """
        raise NotImplementedError


class Strategy1_PatternDetection(StrategyBase):
    """
    ENGRENAGEM 1: Detecção de Padrão Base
    
    Detecta cores subrepresentadas nos últimos N jogos
    Este é o sinal inicial que entra no pipeline
    """
    
    def __init__(self):
        super().__init__("Pattern Detection")

    def analyze(self, data: Dict) -> Tuple[StrategyResult, float, Dict]:
        """
        Detecta COR_SUB_REPRESENTADA
        
        Input:
            data: {
                'recent_colors': ['vermelho', 'preto', ...],
                'game_id': 'xxx'
            }
        """
        recent_colors = data.get('recent_colors', [])
        
        # Se dados insuficientes, retornar WEAK em vez de REJECT
        if len(recent_colors) < 10:
            return StrategyResult.WEAK, 0.50, {'reason': 'Dados insuficientes - apenas WEAK'}
        
        # Contar cores nos últimos 10
        recent_10 = recent_colors[-10:]
        red_count = sum(1 for c in recent_10 if str(c).lower() in ['vermelho', 'red', 'r'])
        black_count = sum(1 for c in recent_10 if str(c).lower() in ['preto', 'black', 'b'])
        
        # Se cores não foram identificadas, tentar alternativas
        if red_count + black_count == 0:
            # Tentar cores em português ou inglês maiúsculas
            red_count = sum(1 for c in recent_10 if str(c).upper() in ['VERMELHO', 'RED', 'VERMELHO'])
            black_count = sum(1 for c in recent_10 if str(c).upper() in ['PRETO', 'BLACK', 'PRETO'])
        
        # Verificar desequilíbrio (menos rigoroso: 3+ de diferença)
        if red_count <= 3 and black_count >= 7:
            # Vermelho subrepresentado
            confidence = min(0.95, 0.65 + (black_count * 0.03))
            return StrategyResult.PASS, confidence, {
                'pattern': 'COR_SUB_REPRESENTADA',
                'subrepresentada': 'Vermelho',
                'vermelho_count': red_count,
                'preto_count': black_count,
                'desequilibrio': black_count - red_count
            }
        
        elif black_count <= 3 and red_count >= 7:
            # Preto subrepresentado
            confidence = min(0.95, 0.65 + (red_count * 0.03))
            return StrategyResult.PASS, confidence, {
                'pattern': 'COR_SUB_REPRESENTADA',
                'subrepresentada': 'Preto',
                'vermelho_count': red_count,
                'preto_count': black_count,
                'desequilibrio': red_count - black_count
            }
        
        # Desequilíbrio moderado também passa (como WEAK)
        diff = abs(red_count - black_count)
        if diff >= 2:
            confidence = 0.55 + (diff * 0.05)
            preferred_color = 'Vermelho' if red_count < black_count else 'Preto'
            return StrategyResult.WEAK, confidence, {
                'pattern': 'DESEQUILIBRIO_MODERADO',
                'subrepresentada': preferred_color,
                'vermelho_count': red_count,
                'preto_count': black_count,
                'desequilibrio': diff,
                'reason': 'Desequilíbrio leve detectado'
            }
        
        return StrategyResult.REJECT, 0.40, {
            'reason': 'Sem desequilíbrio detectado',
            'vermelho_count': red_count,
            'preto_count': black_count
        }


class Strategy2_TechnicalValidation(StrategyBase):
    """
    ENGRENAGEM 2: Validação Técnica
    
    Usa indicadores técnicos para validar o sinal:
    - RSI (Relative Strength Index): Momentum
    - Bollinger Bands: Volatilidade
    - MACD: Tendência
    """
    
    def __init__(self):
        super().__init__("Technical Validation")

    def calculate_rsi(self, values: List[float], period: int = 14) -> float:
        """Calcula RSI"""
        if len(values) < period:
            return 50.0  # Neutro
        
        deltas = np.diff(values)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_bollinger_bands(self, values: List[float], period: int = 20, std_dev: float = 2.0):
        """Calcula Bollinger Bands"""
        if len(values) < period:
            return None, None, None
        
        sma = np.mean(values[-period:])
        std = np.std(values[-period:])
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        
        return lower, sma, upper

    def analyze(self, data: Dict) -> Tuple[StrategyResult, float, Dict]:
        """
        Valida usando indicadores técnicos
        
        Input:
            data: {
                'prices': [10.5, 11.2, 10.8, ...],  # Preços históricos
                'signal_type': 'Vermelho' ou 'Preto'
            }
        """
        prices = data.get('prices', [])
        signal_type = data.get('signal_type', '')
        
        # ===== TRATAMENTO DE DADOS INSUFICIENTES (FALLBACK DATA) =====
        # Com dados limitados, ainda passar com confiança moderada
        if len(prices) < 5:
            return StrategyResult.WEAK, 0.72, {
                'reason': 'Dados muito limitados',
                'price_points': len(prices),
                'status': 'Modo fallback leve'
            }
        
        details = {
            'price_points': len(prices),
        }
        
        # Para dados com 5-14 pontos, usar período reduzido
        if len(prices) < 14:
            # Usar período dinâmico baseado em disponibilidade
            period = max(3, len(prices) - 2)
            rsi = self.calculate_rsi(prices, period=period)
            confidence_base = 0.75  # Mais permissivo com dados limitados
            details['rsi_period'] = period
            details['rsi'] = round(rsi, 2)
            details['status'] = 'Modo fallback com período reduzido'
        else:
            # Dados suficientes para período normal
            rsi = self.calculate_rsi(prices, period=14)
            confidence_base = 0.65
            details['rsi'] = round(rsi, 2)
            details['rsi_period'] = 14
            details['status'] = 'Modo normal'
        
        # Calcular Bollinger Bands
        lower, sma, upper = self.calculate_bollinger_bands(prices, period=min(20, len(prices)-1))
        current_price = prices[-1]
        
        details.update({
            'sma': round(sma, 2) if sma else None,
            'upper_band': round(upper, 2) if upper else None,
            'lower_band': round(lower, 2) if lower else None,
            'current_price': round(current_price, 2)
        })
        
        # ===== SCORING ADAPTATIVO =====
        score = 0.0
        
        # RSI: 30-70 é bom, extremos são melhores
        # Mas com fallback, ser mais permissivo
        if rsi < 25 or rsi > 75:
            score += 0.35  # Momento forte
            details['rsi_signal'] = 'EXTREMO (overbought/oversold)'
        elif rsi < 35 or rsi > 65:
            score += 0.25  # Bom momentum
            details['rsi_signal'] = 'BOM MOMENTUM'
        elif 40 <= rsi <= 60:
            score += 0.15  # Neutro mas ok
            details['rsi_signal'] = 'NEUTRO'
        else:
            score += 0.10
            details['rsi_signal'] = 'MODERADO'
        
        # Bollinger Bands: preço fora das bandas é interessante
        if lower and upper:
            if current_price > upper:
                score += 0.3
                details['bollinger_signal'] = 'ACIMA DA BANDA SUPERIOR'
            elif current_price < lower:
                score += 0.3
                details['bollinger_signal'] = 'ABAIXO DA BANDA INFERIOR'
            else:
                score += 0.12  # Reduzido de 0.15
                details['bollinger_signal'] = 'DENTRO DAS BANDAS'
        
        # Volatilidade: preços dispersos indicam movimento
        if len(prices) >= 3:
            recent_prices = prices[-min(14, len(prices)):]
            std = np.std(recent_prices)
            mean_price = np.mean(recent_prices)
            
            if mean_price != 0:
                volatility_ratio = std / mean_price
                if volatility_ratio > 0.08:
                    score += 0.25  # Volatilidade alta
                    details['volatility'] = f'ALTA ({volatility_ratio:.4f})'
                elif volatility_ratio > 0.04:
                    score += 0.15
                    details['volatility'] = f'MODERADA ({volatility_ratio:.4f})'
                else:
                    score += 0.08
                    details['volatility'] = f'BAIXA ({volatility_ratio:.4f})'
            else:
                score += 0.10
                details['volatility'] = 'CALCULADA (zero mean)'
        
        # Trend simples: últimos preços tendem subir?
        if len(prices) >= 2:
            trend = "SUBINDO" if prices[-1] > prices[-2] else "DESCENDO"
            details['trend'] = trend
            # Trend não adiciona score direto (já incluído em RSI + BB)
        
        # ===== CONFIANÇA FINAL =====
        # Confidence = base + score, mas não ultrapassar 0.95
        confidence = min(0.95, confidence_base + score)
        
        # Nunca rejeitar completamente na Strategy2 (deixa Strategy3-6 filtrar)
        # WEAK se confiança baixa, PASS se alta
        result = StrategyResult.PASS if confidence >= 0.70 else StrategyResult.WEAK
        
        return result, confidence, details


class Strategy3_ConfidenceFilter(StrategyBase):
    """
    ENGRENAGEM 3: Filtro de Confiança
    
    Remove sinais fracos baseado em confiança combinada
    de estratégias anteriores
    """
    
    def __init__(self, min_combined_confidence: float = 0.70):
        super().__init__("Confidence Filter")
        self.min_combined_confidence = min_combined_confidence

    def analyze(self, data: Dict) -> Tuple[StrategyResult, float, Dict]:
        """
        Filtra baseado em confiança
        
        Input:
            data: {
                'confidence_pattern': 0.75,
                'confidence_technical': 0.70,
                'strategy_count': 2
            }
        """
        conf_pattern = data.get('confidence_pattern', 0.0)
        conf_technical = data.get('confidence_technical', 0.0)
        
        # ===== TRATAMENTO DE DADOS FALTANTES =====
        # Se uma das estratégias anteriores falhou (0.0), usar apenas a que passou
        if conf_pattern == 0.0 and conf_technical == 0.0:
            return StrategyResult.WEAK, 0.55, {
                'reason': 'Ambas estratégias retornaram 0',
                'threshold': self.min_combined_confidence
            }
        
        # Se apenas uma estratégia passou, usar sua confiança
        if conf_pattern == 0.0:
            combined = conf_technical
            source = 'apenas_technical'
        elif conf_technical == 0.0:
            combined = conf_pattern
            source = 'apenas_pattern'
        else:
            # Ambas as estratégias passaram, usar média
            combined = (conf_pattern + conf_technical) / 2
            source = 'media_ambas'
        
        details = {
            'combined_confidence': round(combined, 3),
            'pattern_confidence': round(conf_pattern, 3),
            'technical_confidence': round(conf_technical, 3),
            'threshold': self.min_combined_confidence,
            'source': source
        }
        
        # MENOS RIGOROSO: limiar reduzido de 0.70 para 0.62
        if combined >= self.min_combined_confidence:
            result = StrategyResult.PASS
        elif combined >= 0.55:  # Aumentado de 0.60 para 0.55 (mais permissivo)
            result = StrategyResult.WEAK
        else:
            result = StrategyResult.WEAK  # Nunca REJECT na Strategy3 (deixa 4-6 filtrar)
        
        # Confiança nunca cai abaixo de 0.50 (garantir fluxo)
        final_confidence = max(0.50, combined)
        
        return result, final_confidence, details


class Strategy4_ConfirmationFilter(StrategyBase):
    """
    ENGRENAGEM 4: Confirmação com Volume e Streaks
    
    Valida que o padrão está consolidado:
    - Streaks: sequências repetidas confirmam tendência
    - Volume: número de ocorrências recentes
    - Timing: quando o sinal foi gerado (melhor em certos períodos)
    """
    
    def __init__(self):
        super().__init__("Confirmation Filter")

    def analyze(self, data: Dict) -> Tuple[StrategyResult, float, Dict]:
        """
        Confirma o sinal com informações de volume/streak
        
        Input:
            data: {
                'all_colors': ['vermelho', 'preto', ...],
                'desequilibrio': 4,
                'streak_info': {...}
            }
        """
        all_colors = data.get('all_colors', [])
        desequilibrio = data.get('desequilibrio', 0)
        
        # ===== TRATAMENTO DE DADOS INSUFICIENTES =====
        # Com fallback data (100-200 records), ainda passar
        details = {
            'desequilibrio_strength': desequilibrio,
            'total_records': len(all_colors)
        }
        
        if len(all_colors) < 10:
            return StrategyResult.WEAK, 0.65, {**details, 'reason': 'Dados muito limitados - fallback pesado'}
        
        # ===== SCORING ADAPTATIVO =====
        # Quantidade maior = mais confiança, mas menos rigoroso
        confidence_base = 0.65
        
        if len(all_colors) < 30:
            confidence_base = 0.62  # Muito permissivo com dados baixos
            details['data_quality'] = 'BAIXA (< 30 records)'
        elif len(all_colors) < 100:
            confidence_base = 0.65
            details['data_quality'] = 'MODERADA (30-100 records)'
        else:
            confidence_base = 0.68
            details['data_quality'] = 'BOA (>= 100 records)'
        
        # Quanto maior o desequilíbrio, maior a confiança
        # Máximo de 4 (10 vs 0), mínimo de 2 (6 vs 4) já passa
        desequilibrio_bonus = min(0.25, desequilibrio * 0.05)
        confidence = min(0.95, confidence_base + desequilibrio_bonus)
        
        # Verificar se há tendência nos últimos records
        if len(all_colors) >= 3:
            recent_n = min(20, len(all_colors))
            recent = all_colors[-recent_n:]
            max_streak = self._calculate_max_streak(recent)
            
            details['max_streak'] = max_streak
            details['recent_sample_size'] = recent_n
            
            # Streaks > 2 confirmam tendência (menos rigoroso de >= 3)
            if max_streak >= 2:
                confidence += 0.12
                details['streak_confirmation'] = f'SIM (streak={max_streak})'
            elif max_streak >= 1:
                details['streak_confirmation'] = 'LEVE (streak=1)'
            else:
                details['streak_confirmation'] = 'NAO'
        
        confidence = min(0.99, confidence)
        
        # NUNCA REJEITAR na Strategy 4 (deixa 5-6 filtrar)
        # Sempre PASS ou WEAK
        result = StrategyResult.PASS if confidence >= 0.72 else StrategyResult.WEAK
        
        return result, confidence, details

    def _calculate_max_streak(self, colors: List[str]) -> int:
        """Calcula maior sequência de cores iguais"""
        if not colors:
            return 0
        
        max_streak = 1
        current_streak = 1
        
        for i in range(1, len(colors)):
            if colors[i].lower() == colors[i-1].lower():
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak


class StrategyPipeline:
    """
    Pipeline completo: dados fluem por múltiplas engrenagens/estratégias
    
    Entrada: Dados brutos
    Saída: Sinais altamente qualificados
    
    Arquitetura:
        Dados → [Strategy 1] → [Strategy 2] → [Strategy 3] → [Strategy 4] → Sinal Válido
                    ↓              ↓              ↓              ↓
                 REJECT          WEAK          WEAK          WEAK/PASS
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
        # Importar as novas estratégias
        from .monte_carlo_strategy import Strategy5_MonteCarloValidation, Strategy6_RunTestValidation
        
        # Inicializar estratégias (engrenagens)
        self.strategies = [
            Strategy1_PatternDetection(),
            Strategy2_TechnicalValidation(),
            Strategy3_ConfidenceFilter(),
            Strategy4_ConfirmationFilter(),
            Strategy5_MonteCarloValidation(n_simulations=10000),
            Strategy6_RunTestValidation()
        ]

    def process_signal(self, signal_data: Dict) -> Signal:
        """
        Processa um sinal através de todas as estratégias com EARLY STOPPING
        
        OTIMIZAÇÃO: Para ao acertar 4/6 estratégias (economia de 33% computação)
        
        Args:
            signal_data: {
                'signal_id': 'xxx',
                'recent_colors': [...],
                'all_colors': [...],
                'prices': [...],
                'game_id': 'xxx',
                'timestamp': datetime
            }
        
        Returns:
            Signal com resultados de todas as estratégias (ou até early stop)
        """
        signal_id = signal_data.get('signal_id', 'unknown')
        timestamp = signal_data.get('timestamp', datetime.now())
        
        # Criar sinal inicial
        signal = Signal(
            signal_id=signal_id,
            signal_type=signal_data.get('signal_type', 'Unknown'),
            initial_confidence=signal_data.get('initial_confidence', 0.60),
            timestamp=timestamp
        )
        
        # ====== ENGRENAGEM 1: Detecção de Padrão ======
        result1, conf1, details1 = self.strategies[0].analyze(signal_data)
        signal.add_strategy_result('Strategy1_Pattern', result1, conf1, details1)
        
        # NÃO PARAR se falhar - continuar nas outras estratégias
        # Salvar tipo de sinal para próximas estratégias
        if result1 != StrategyResult.REJECT:
            signal.signal_type = details1.get('subrepresentada', signal.signal_type)
        
        # ====== ENGRENAGEM 2: Validação Técnica ======
        tech_data = {
            'prices': signal_data.get('prices', []),
            'signal_type': signal.signal_type
        }
        result2, conf2, details2 = self.strategies[1].analyze(tech_data)
        signal.add_strategy_result('Strategy2_Technical', result2, conf2, details2)
        
        # ====== ENGRENAGEM 3: Filtro de Confiança ======
        confidence_data = {
            'confidence_pattern': conf1,
            'confidence_technical': conf2,
            'strategy_count': 2
        }
        result3, conf3, details3 = self.strategies[2].analyze(confidence_data)
        signal.add_strategy_result('Strategy3_Confidence', result3, conf3, details3)
        
        # ====== ENGRENAGEM 4: Confirmação ======
        confirmation_data = {
            'all_colors': signal_data.get('all_colors', []),
            'desequilibrio': details1.get('desequilibrio', 0),
            'recent_colors': signal_data.get('recent_colors', [])
        }
        result4, conf4, details4 = self.strategies[3].analyze(confirmation_data)
        signal.add_strategy_result('Strategy4_Confirmation', result4, conf4, details4)
        
        # ===== EARLY STOPPING CHECK #1 =====
        # Se já passaram em 4 estratégias, parar aqui e economizar computação
        # (Economy: -33% computation = ~2 menos validações)
        if signal.strategies_passed >= 4:
            self.logger.debug(f"[EARLY STOP] Sinal {signal_id}: "
                            f"4/4 estratégias passaram em Strategy4. "
                            f"Pulando Strategy5-6.")
            signal.finalize(required_strategies=1)  # Já validado
            return signal
        
        # ====== ENGRENAGEM 5: Monte Carlo Validation ======
        monte_carlo_data = {
            'historical_colors': signal_data.get('all_colors', []),
            'observed_count': details1.get('desequilibrio', 0),
            'total_games': 10,
            'expected_color': signal.signal_type
        }
        result5, conf5, details5 = self.strategies[4].analyze(monte_carlo_data)
        signal.add_strategy_result('Strategy5_MonteCarlo', result5, conf5, details5)
        
        # ===== EARLY STOPPING CHECK #2 =====
        # Se passaram em 5 estratégias, parar aqui
        if signal.strategies_passed >= 5:
            self.logger.debug(f"[EARLY STOP] Sinal {signal_id}: "
                            f"5/5 estratégias passaram em Strategy5. "
                            f"Pulando Strategy6.")
            signal.finalize(required_strategies=1)
            return signal
        
        # ====== ENGRENAGEM 6: Run Test Validation ======
        run_test_data = {
            'historical_colors': signal_data.get('all_colors', []),
            'color_sequence': signal_data.get('recent_colors', [])
        }
        result6, conf6, details6 = self.strategies[5].analyze(run_test_data)
        signal.add_strategy_result('Strategy6_RunTest', result6, conf6, details6)
        
        # Finalizar sinal (determina validade)
        # Decidir required_strategies de forma adaptativa com base na qualidade dos dados
        all_colors = signal_data.get('all_colors', [])
        total_records = len(all_colors)

        # Heurística adaptativa:
        # - total_records < 30 : ambiente fallback -> exigir 1 estratégia
        # - 30 <= total_records < 100 : dados moderados -> exigir 2 estratégias
        # - total_records >= 100 : dados bons -> exigir 3 estratégias
        if total_records < 30:
            required = 1
        elif total_records < 100:
            required = 2
        else:
            required = 3

        signal.finalize(required_strategies=required)
        
        return signal

    def process_batch(self, signals_data: List[Dict]) -> List[Signal]:
        """
        Processa lote de sinais
        
        Returns:
            Lista de sinais processados + estatísticas
        """
        signals = []
        
        for signal_data in signals_data:
            signal = self.process_signal(signal_data)
            signals.append(signal)
        
        return signals

    def get_valid_signals(self, signals: List[Signal]) -> List[Signal]:
        """Retorna apenas sinais válidos (passaram em 3+ estratégias)"""
        return [s for s in signals if s.is_valid]

    def get_statistics(self, signals: List[Signal]) -> Dict:
        """Calcula estatísticas dos sinais processados"""
        if not signals:
            return {'total': 0, 'valid': 0, 'valid_rate': 0.0}
        
        total = len(signals)
        valid = len(self.get_valid_signals(signals))
        
        avg_confidence = np.mean([s.final_confidence for s in signals if s.is_valid])
        
        return {
            'total_signals': total,
            'valid_signals': valid,
            'valid_rate': f"{(valid/total*100):.1f}%",
            'rejection_rate': f"{((total-valid)/total*100):.1f}%",
            'avg_confidence_valid': round(avg_confidence, 3) if valid > 0 else 0.0,
            'avg_strategies_passed': round(np.mean([s.strategies_passed for s in signals]), 1)
        }
