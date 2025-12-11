"""
Enriquecedor de Sinais para Telegram
=====================================

Cria mensagens ricas com emojis, contexto e recomendações

Exemplo:
    🎯 SINAL FORTE - VERMELHO
    
    📊 Análise:
    • Confiança: 87.5% ⭐⭐⭐⭐
    • Força: MUITO FORTE
    • Risco: BAIXO 🟢
    
    📈 Indicadores:
    • Volume: 0.92 (Alto)
    • Tendência: 0.85 (Forte)
    • Sequência: Streak 4 Preto → Reversão esperada
    • Volatilidade: 0.78 (Estável)
    
    💰 Gestão de Banca:
    • Stake sugerido: 3.5% da banca
    • Stop-loss: Após 2 perdas
    • Take-profit: 5 ganhos consecutivos
    
    ⏰ 10/12/2025 20:15:30
"""

from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TelegramMessageEnricher:
    """Enriquece mensagens do Telegram com contexto e formatação"""
    
    # Emojis por categoria
    EMOJIS = {
        'signal': {
            'Vermelho': '🔴',
            'Preto': '⚫',
            'Branco': '⚪'
        },
        'strength': {
            'MUITO_FORTE': '💪💪💪',
            'FORTE': '💪💪',
            'MODERADO': '💪',
            'FRACO': '⚠️'
        },
        'risk': {
            'BAIXO': '🟢',
            'MEDIO': '🟡',
            'ALTO': '🔴'
        },
        'stars': {
            5: '⭐⭐⭐⭐⭐',
            4: '⭐⭐⭐⭐',
            3: '⭐⭐⭐',
            2: '⭐⭐',
            1: '⭐'
        },
        'indicators': {
            'volume': '📊',
            'trend': '📈',
            'sequence': '🔄',
            'volatility': '📉'
        },
        'money': '💰',
        'time': '⏰',
        'stats': '📋',
        'rocket': '🚀',
        'fire': '🔥',
        'target': '🎯',
        'check': '✅',
        'warning': '⚠️',
        'chart': '📊'
    }
    
    def __init__(self):
        self.message_history = []
        logger.info("[OK] TelegramMessageEnricher inicializado")
    
    def create_rich_signal_message(self, signal_data: dict) -> str:
        """
        Cria mensagem rica para sinal
        
        Args:
            signal_data: Dicionário com dados do sinal (de PatternSignal.to_dict())
        
        Returns:
            Mensagem formatada em Markdown
        """
        try:
            # Extrair dados
            signal_type = signal_data.get('signal_type', 'Unknown')
            confidence = signal_data.get('confidence', 0.0)
            strength = signal_data.get('strength', 'FRACO')
            risk_level = signal_data.get('risk_level', 'MEDIO')
            
            # Scores individuais
            volume_score = signal_data.get('volume_score', 0.0)
            trend_score = signal_data.get('trend_score', 0.0)
            sequence_score = signal_data.get('sequence_score', 0.0)
            volatility_score = signal_data.get('volatility_score', 0.0)
            
            # Contexto
            current_streak = signal_data.get('current_streak', 0)
            expected_reversal = signal_data.get('expected_reversal', False)
            
            # Gestão de banca
            suggested_stake = signal_data.get('suggested_stake', 0.02)
            stop_loss = signal_data.get('stop_loss')
            take_profit = signal_data.get('take_profit')
            
            # Timestamp
            timestamp_str = signal_data.get('timestamp', datetime.now().isoformat())
            timestamp = datetime.fromisoformat(timestamp_str)
            
            # === CONSTRUIR MENSAGEM ===
            
            # Header
            signal_emoji = self.EMOJIS['signal'].get(signal_type, '🎲')
            strength_emoji = self.EMOJIS['strength'].get(strength, '⚠️')
            stars = self._get_stars(confidence)
            
            message = f"{self.EMOJIS['target']} *SINAL {strength}* - {signal_emoji} *{signal_type.upper()}*\n\n"
            
            # Análise principal
            message += f"{self.EMOJIS['chart']} *Análise:*\n"
            message += f"• Confiança: *{confidence:.1%}* {stars}\n"
            message += f"• Força: *{strength}* {strength_emoji}\n"
            
            risk_emoji = self.EMOJIS['risk'].get(risk_level, '🟡')
            message += f"• Risco: *{risk_level}* {risk_emoji}\n\n"
            
            # Indicadores técnicos
            message += f"{self.EMOJIS['indicators']['volume']} *Indicadores:*\n"
            message += f"• Volume: {volume_score:.2f} {self._score_label(volume_score)}\n"
            message += f"• Tendência: {trend_score:.2f} {self._score_label(trend_score)}\n"
            
            # Sequência com contexto
            reversal_text = "→ Reversão esperada" if expected_reversal else ""
            message += f"• Sequência: Streak {current_streak} {reversal_text}\n"
            message += f"• Volatilidade: {volatility_score:.2f} {self._volatility_label(volatility_score)}\n\n"
            
            # Gestão de banca
            message += f"{self.EMOJIS['money']} *Gestão de Banca:*\n"
            message += f"• Stake sugerido: *{suggested_stake:.1%}* da banca\n"
            
            if stop_loss:
                message += f"• Stop-loss: Após {int(stop_loss)} perdas\n"
            if take_profit:
                message += f"• Take-profit: {int(take_profit)} ganhos consecutivos\n"
            
            # Footer com timestamp
            time_str = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            message += f"\n{self.EMOJIS['time']} {time_str}"
            
            # Adicionar ao histórico
            self.message_history.append({
                'message': message,
                'signal_type': signal_type,
                'confidence': confidence,
                'timestamp': timestamp
            })
            
            return message
            
        except Exception as e:
            logger.error(f"Erro ao criar mensagem rica: {str(e)}")
            # Fallback para mensagem simples
            return self._create_simple_message(signal_data)
    
    def create_simple_signal_message(self, signal_type: str, confidence: float) -> str:
        """
        Cria mensagem simples (compatível com código atual)
        
        Args:
            signal_type: 'Vermelho', 'Preto', etc.
            confidence: 0.0 - 1.0
        
        Returns:
            Mensagem formatada
        """
        signal_emoji = self.EMOJIS['signal'].get(signal_type, '🎲')
        stars = self._get_stars(confidence)
        
        message = f"{self.EMOJIS['target']} *SINAL* - {signal_emoji} *{signal_type.upper()}*\n\n"
        message += f"• Confiança: *{confidence:.1%}* {stars}\n"
        message += f"{self.EMOJIS['time']} {datetime.now().strftime('%H:%M:%S')}"
        
        return message
    
    def create_performance_summary(self, stats: dict) -> str:
        """
        Cria mensagem de resumo de performance
        
        Args:
            stats: Estatísticas de performance (de AdvancedPatternAnalyzer.get_performance_stats())
        
        Returns:
            Mensagem formatada
        """
        try:
            total = stats.get('total_signals', 0)
            avg_conf = stats.get('avg_confidence', 0.0)
            avg_stake = stats.get('avg_suggested_stake', 0.0)
            
            message = f"{self.EMOJIS['stats']} *RESUMO DE PERFORMANCE*\n\n"
            message += f"• Total de sinais: *{total}*\n"
            message += f"• Confiança média: *{avg_conf:.1%}*\n"
            message += f"• Stake médio: *{avg_stake:.1%}*\n\n"
            
            # Distribuição de força
            strength_dist = stats.get('strength_distribution', {})
            if strength_dist:
                message += "*Força dos sinais:*\n"
                for strength, count in strength_dist.items():
                    emoji = self.EMOJIS['strength'].get(strength, '•')
                    pct = (count / total * 100) if total > 0 else 0
                    message += f"{emoji} {strength}: {count} ({pct:.1f}%)\n"
                message += "\n"
            
            # Distribuição de risco
            risk_dist = stats.get('risk_distribution', {})
            if risk_dist:
                message += "*Níveis de risco:*\n"
                for risk, count in risk_dist.items():
                    emoji = self.EMOJIS['risk'].get(risk, '•')
                    pct = (count / total * 100) if total > 0 else 0
                    message += f"{emoji} {risk}: {count} ({pct:.1f}%)\n"
            
            message += f"\n{self.EMOJIS['time']} {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            return message
            
        except Exception as e:
            logger.error(f"Erro ao criar resumo de performance: {str(e)}")
            return f"{self.EMOJIS['warning']} Erro ao gerar resumo"
    
    def create_alert_message(self, alert_type: str, message_text: str) -> str:
        """
        Cria mensagem de alerta
        
        Args:
            alert_type: 'info', 'warning', 'error', 'success'
            message_text: Texto do alerta
        
        Returns:
            Mensagem formatada
        """
        emoji_map = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅',
            'fire': self.EMOJIS['fire'],
            'rocket': self.EMOJIS['rocket']
        }
        
        emoji = emoji_map.get(alert_type, 'ℹ️')
        return f"{emoji} {message_text}"
    
    def _get_stars(self, confidence: float) -> str:
        """Retorna estrelas baseado na confiança"""
        if confidence >= 0.90:
            return self.EMOJIS['stars'][5]
        elif confidence >= 0.80:
            return self.EMOJIS['stars'][4]
        elif confidence >= 0.70:
            return self.EMOJIS['stars'][3]
        elif confidence >= 0.60:
            return self.EMOJIS['stars'][2]
        else:
            return self.EMOJIS['stars'][1]
    
    def _score_label(self, score: float) -> str:
        """Label descritivo para score"""
        if score >= 0.85:
            return "(Excelente)"
        elif score >= 0.70:
            return "(Bom)"
        elif score >= 0.55:
            return "(Moderado)"
        else:
            return "(Fraco)"
    
    def _volatility_label(self, score: float) -> str:
        """Label para volatilidade"""
        if score >= 0.80:
            return "(Muito estável)"
        elif score >= 0.65:
            return "(Estável)"
        elif score >= 0.50:
            return "(Moderada)"
        else:
            return "(Alta)"
    
    def _create_simple_message(self, signal_data: dict) -> str:
        """Mensagem simples de fallback"""
        signal_type = signal_data.get('signal_type', 'Unknown')
        confidence = signal_data.get('confidence', 0.0)
        return self.create_simple_signal_message(signal_type, confidence)
    
    def get_last_messages(self, count: int = 5) -> list:
        """Retorna últimas N mensagens enviadas"""
        return self.message_history[-count:] if self.message_history else []
    
    def clear_history(self):
        """Limpa histórico de mensagens"""
        self.message_history.clear()
        logger.info("Histórico de mensagens limpo")
