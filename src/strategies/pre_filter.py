#!/usr/bin/env python3
"""
Pre-Filter Validation Module - Tier 2 Enhancement

Valida sinais ANTES de serem processados:
1. Volume Check - Verifica se há volume suficiente
2. Trend Confirmation - Confirma alinhamento com trend
3. Risk/Reward - Valida razão risco-recompensa
4. Volatility Check - Valida volatilidade
5. Time Filters - Valida horários favoráveis

Status: BETA (Implementação Tier 2)
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class PreFilter:
    """
    Pre-Filter Validation para sinais.
    
    Attributes:
        min_volume: Volume mínimo requerido
        min_trend_bars: Número mínimo de barras para confirmar trend
        min_risk_reward_ratio: Razão mínima de risco-recompensa
        max_volatility: Volatilidade máxima permitida
        enabled_filters: Quais filtros estão ativos
    """
    
    def __init__(
        self,
        min_volume: float = 100.0,
        min_trend_bars: int = 3,
        min_risk_reward_ratio: float = 1.5,
        max_volatility: float = 5.0,
        enable_volume_check: bool = True,
        enable_trend_check: bool = True,
        enable_risk_check: bool = True,
        enable_volatility_check: bool = True,
        enable_time_filter: bool = False,
        state_path: str = 'logs/pre_filter_state.json'
    ):
        """Inicializa Pre-Filter com configurações."""
        self.min_volume = min_volume
        self.min_trend_bars = min_trend_bars
        self.min_risk_reward_ratio = min_risk_reward_ratio
        self.max_volatility = max_volatility
        
        self.enabled_filters = {
            'volume': enable_volume_check,
            'trend': enable_trend_check,
            'risk_reward': enable_risk_check,
            'volatility': enable_volatility_check,
            'time': enable_time_filter
        }
        
        self.state_path = state_path
        self.stats = {
            'signals_checked': 0,
            'signals_passed': 0,
            'signals_rejected': 0,
            'rejections_by_filter': {
                'volume': 0,
                'trend': 0,
                'risk_reward': 0,
                'volatility': 0,
                'time': 0
            },
            'last_update': None
        }
        
        self._load_state()
        logger.info(f"[Pre-Filter] Inicializado com {sum(self.enabled_filters.values())}/5 filtros ativos")
    
    def validate_signal(
        self,
        signal: Dict,
        market_data: Optional[Dict] = None
    ) -> Tuple[bool, str, Dict]:
        """
        Valida um sinal contra todos os filtros ativos.
        
        Args:
            signal: Dict com dados do sinal (estratégia, confiança, etc)
            market_data: Dict com dados de mercado (volume, preço, etc)
        
        Returns:
            (passou, motivo_rejeição, detalhes_validação)
        """
        self.stats['signals_checked'] += 1
        
        validation_details = {
            'timestamp': datetime.now().isoformat(),
            'signal_id': signal.get('id', 'unknown'),
            'strategy': signal.get('strategy', 'unknown'),
            'filters_checked': []
        }
        
        # Volume Check
        if self.enabled_filters['volume']:
            passed, reason = self._check_volume(market_data or {})
            validation_details['filters_checked'].append({
                'filter': 'volume',
                'passed': passed,
                'reason': reason
            })
            if not passed:
                self.stats['rejections_by_filter']['volume'] += 1
                self.stats['signals_rejected'] += 1
                self._save_state()
                return False, f"Volume insuficiente: {reason}", validation_details
        
        # Trend Check
        if self.enabled_filters['trend']:
            passed, reason = self._check_trend(market_data or {}, signal)
            validation_details['filters_checked'].append({
                'filter': 'trend',
                'passed': passed,
                'reason': reason
            })
            if not passed:
                self.stats['rejections_by_filter']['trend'] += 1
                self.stats['signals_rejected'] += 1
                self._save_state()
                return False, f"Trend não confirmado: {reason}", validation_details
        
        # Risk/Reward Check
        if self.enabled_filters['risk_reward']:
            passed, reason = self._check_risk_reward(signal, market_data or {})
            validation_details['filters_checked'].append({
                'filter': 'risk_reward',
                'passed': passed,
                'reason': reason
            })
            if not passed:
                self.stats['rejections_by_filter']['risk_reward'] += 1
                self.stats['signals_rejected'] += 1
                self._save_state()
                return False, f"Risk/Reward inadequado: {reason}", validation_details
        
        # Volatility Check
        if self.enabled_filters['volatility']:
            passed, reason = self._check_volatility(market_data or {})
            validation_details['filters_checked'].append({
                'filter': 'volatility',
                'passed': passed,
                'reason': reason
            })
            if not passed:
                self.stats['rejections_by_filter']['volatility'] += 1
                self.stats['signals_rejected'] += 1
                self._save_state()
                return False, f"Volatilidade alta: {reason}", validation_details
        
        # Time Filter
        if self.enabled_filters['time']:
            passed, reason = self._check_time()
            validation_details['filters_checked'].append({
                'filter': 'time',
                'passed': passed,
                'reason': reason
            })
            if not passed:
                self.stats['rejections_by_filter']['time'] += 1
                self.stats['signals_rejected'] += 1
                self._save_state()
                return False, f"Horário desfavorável: {reason}", validation_details
        
        # Todas as validações passaram
        self.stats['signals_passed'] += 1
        self._save_state()
        return True, "Todos os filtros passaram", validation_details
    
    def _check_volume(self, market_data: Dict) -> Tuple[bool, str]:
        """Verifica volume suficiente."""
        volume = market_data.get('volume', 0)
        if volume >= self.min_volume:
            return True, f"Volume OK: {volume:.2f}"
        return False, f"Volume baixo: {volume:.2f} < {self.min_volume:.2f}"
    
    def _check_trend(self, market_data: Dict, signal: Dict) -> Tuple[bool, str]:
        """Verifica alinhamento com trend."""
        trend = market_data.get('trend', 'UNKNOWN')
        signal_direction = signal.get('direction', 'UNKNOWN')
        
        # Trend deve estar alinhado com sinal
        if trend == 'UP' and signal_direction in ['UP', 'GREEN']:
            return True, f"Trend UP, Sinal {signal_direction} - Alinhados"
        elif trend == 'DOWN' and signal_direction in ['DOWN', 'RED']:
            return True, f"Trend DOWN, Sinal {signal_direction} - Alinhados"
        elif trend == 'FLAT':
            return True, f"Trend FLAT - Permitido"
        
        return False, f"Trend {trend} desalinhado com Sinal {signal_direction}"
    
    def _check_risk_reward(self, signal: Dict, market_data: Dict) -> Tuple[bool, str]:
        """Verifica razão risco-recompensa."""
        # Simulação simples: confiança como proxy para reward
        confidence = signal.get('confidence', 0.5)
        expected_reward = confidence * 100  # % ganho esperado
        
        # Risco = 1-confidence
        risk = (1 - confidence) * 100
        
        if risk > 0:
            ratio = expected_reward / risk
        else:
            ratio = float('inf')
        
        if ratio >= self.min_risk_reward_ratio:
            return True, f"R/R OK: {ratio:.2f} >= {self.min_risk_reward_ratio}"
        return False, f"R/R baixo: {ratio:.2f} < {self.min_risk_reward_ratio}"
    
    def _check_volatility(self, market_data: Dict) -> Tuple[bool, str]:
        """Verifica volatilidade."""
        volatility = market_data.get('volatility', 0)
        
        if volatility <= self.max_volatility:
            return True, f"Volatilidade OK: {volatility:.2f}%"
        return False, f"Volatilidade alta: {volatility:.2f}% > {self.max_volatility}%"
    
    def _check_time(self) -> Tuple[bool, str]:
        """Verifica horários favoráveis (mercado aberto, etc)."""
        now = datetime.now()
        hour = now.hour
        
        # Exemplo: Trading apenas 09:00-17:00 (horário de mercado)
        if 9 <= hour < 17:
            return True, f"Horário favorável: {hour}:00"
        return False, f"Horário desfavorável: {hour}:00 (fora de 09:00-17:00)"
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas de validação."""
        stats = self.stats.copy()
        if self.stats['signals_checked'] > 0:
            stats['pass_rate'] = (self.stats['signals_passed'] / self.stats['signals_checked']) * 100
        else:
            stats['pass_rate'] = 0.0
        stats['last_update'] = datetime.now().isoformat()
        return stats
    
    def reset_stats(self):
        """Reseta estatísticas."""
        self.stats = {
            'signals_checked': 0,
            'signals_passed': 0,
            'signals_rejected': 0,
            'rejections_by_filter': {
                'volume': 0,
                'trend': 0,
                'risk_reward': 0,
                'volatility': 0,
                'time': 0
            },
            'last_update': None
        }
        self._save_state()
    
    def _load_state(self):
        """Carrega estado anterior de JSON."""
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.stats = saved.get('stats', self.stats)
                    logger.debug(f"[Pre-Filter] Estado carregado: {self.stats['signals_checked']} sinais checados")
            except Exception as e:
                logger.warning(f"[Pre-Filter] Erro ao carregar estado: {e}")
    
    def _save_state(self):
        """Salva estado em JSON."""
        try:
            os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'stats': self.stats,
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"[Pre-Filter] Erro ao salvar estado: {e}")


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Inicializar pre-filter
    pf = PreFilter(
        min_volume=50.0,
        min_risk_reward_ratio=1.5,
        enable_volume_check=True,
        enable_trend_check=True,
        enable_risk_check=True,
        enable_volatility_check=True
    )
    
    # Teste 1: Sinal válido
    signal1 = {
        'id': 'sig001',
        'strategy': 'RSI_Strategy',
        'direction': 'UP',
        'confidence': 0.85
    }
    market_data1 = {
        'volume': 150.0,
        'trend': 'UP',
        'volatility': 2.5,
        'price': 100.0
    }
    
    passed, reason, details = pf.validate_signal(signal1, market_data1)
    print(f"Sinal 1: {'✅ PASSED' if passed else '❌ REJECTED'} - {reason}")
    
    # Teste 2: Sinal com volume baixo
    signal2 = {
        'id': 'sig002',
        'strategy': 'MACD_Strategy',
        'direction': 'DOWN',
        'confidence': 0.60
    }
    market_data2 = {
        'volume': 20.0,  # Muito baixo
        'trend': 'DOWN',
        'volatility': 3.0,
        'price': 99.0
    }
    
    passed, reason, details = pf.validate_signal(signal2, market_data2)
    print(f"Sinal 2: {'✅ PASSED' if passed else '❌ REJECTED'} - {reason}")
    
    # Estatísticas
    stats = pf.get_stats()
    print(f"\nEstatísticas: {stats['signals_passed']}/{stats['signals_checked']} passaram ({stats['pass_rate']:.1f}%)")
