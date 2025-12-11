"""
Sistema de Health Checks e Monitoramento
FASE 3 - Robustez do Sistema
"""
import logging
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List
import traceback

from core import SystemHealth
from config.logger_config import get_logger

logger = get_logger(__name__)


class HealthChecker:
    """Verifica saúde do sistema"""
    
    def __init__(self, initial_uptime: float = 0.0):
        """
        Inicializa health checker
        
        Args:
            initial_uptime: Tempo de uptime inicial (segundos)
        """
        self.start_time = datetime.now()
        self.last_error = None
        self.error_count = 0
        self.check_history: List[SystemHealth] = []
    
    def check(self,
              data_collection_ok: bool = True,
              telegram_ok: bool = True,
              database_ok: bool = True,
              signals_processed: int = 0) -> SystemHealth:
        """
        Realiza check de saúde completo
        
        Args:
            data_collection_ok: Coleta de dados está OK?
            telegram_ok: Telegram está OK?
            database_ok: Banco de dados está OK?
            signals_processed: Sinais processados
        
        Returns:
            SystemHealth com status
        """
        try:
            uptime = (datetime.now() - self.start_time).total_seconds()
            memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            healthy = (
                data_collection_ok and
                telegram_ok and
                database_ok and
                memory < 500  # Alert se > 500MB
            )
            
            health = SystemHealth(
                healthy=healthy,
                timestamp=datetime.now(),
                uptime_seconds=uptime,
                last_error=self.last_error,
                signals_processed=signals_processed,
                data_collection_ok=data_collection_ok,
                telegram_ok=telegram_ok,
                database_ok=database_ok,
                memory_usage_mb=memory
            )
            
            self.check_history.append(health)
            
            # Manter apenas últimos 100 checks
            if len(self.check_history) > 100:
                self.check_history = self.check_history[-100:]
            
            self._log_health(health)
            return health
            
        except Exception as e:
            logger.error(f"Erro em health check: {e}")
            self.last_error = str(e)
            self.error_count += 1
            
            return SystemHealth(
                healthy=False,
                timestamp=datetime.now(),
                uptime_seconds=(datetime.now() - self.start_time).total_seconds(),
                last_error=str(e)
            )
    
    def _log_health(self, health: SystemHealth):
        """Registra status de saúde"""
        status_icon = "✅" if health.healthy else "⚠️"
        
        logger.info(
            f"{status_icon} HEALTH CHECK | "
            f"Uptime: {self._format_uptime(health.uptime_seconds)} | "
            f"Memory: {health.memory_usage_mb:.1f}MB | "
            f"Signals: {health.signals_processed} | "
            f"API: {'OK' if health.data_collection_ok else 'ERROR'} | "
            f"TG: {'OK' if health.telegram_ok else 'ERROR'} | "
            f"DB: {'OK' if health.database_ok else 'ERROR'}"
        )
    
    def _format_uptime(self, seconds: float) -> str:
        """Formata uptime para string legível"""
        hours = int(seconds) // 3600
        minutes = (int(seconds) % 3600) // 60
        return f"{hours}h {minutes}m"
    
    def get_history(self, last_n: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna histórico de health checks
        
        Args:
            last_n: Últimos N checks
        
        Returns:
            Lista de dicts com histórico
        """
        return [
            {
                'timestamp': h.timestamp.isoformat(),
                'healthy': h.healthy,
                'uptime': self._format_uptime(h.uptime_seconds),
                'memory_mb': round(h.memory_usage_mb, 1),
                'signals': h.signals_processed,
                'components': {
                    'data_collection': h.data_collection_ok,
                    'telegram': h.telegram_ok,
                    'database': h.database_ok
                }
            }
            for h in self.check_history[-last_n:]
        ]


class AlertSystem:
    """Sistema de alertas para anomalias"""
    
    def __init__(self, telegram_manager=None):
        """
        Inicializa sistema de alertas
        
        Args:
            telegram_manager: Manager do Telegram (opcional)
        """
        self.telegram = telegram_manager
        self.alert_thresholds = {
            'memory_mb': 400,
            'error_rate': 0.1,  # 10%
            'signal_gap_minutes': 30,
            'failed_requests': 5
        }
        self.alerts_sent: List[Dict[str, Any]] = []
    
    def check_anomalies(self, health: SystemHealth) -> List[str]:
        """
        Detecta anomalias no health check
        
        Args:
            health: SystemHealth a analisar
        
        Returns:
            Lista de alertas detectados
        """
        alerts = []
        
        # Memory
        if health.memory_usage_mb > self.alert_thresholds['memory_mb']:
            alerts.append(
                f"⚠️ Memory Alert: {health.memory_usage_mb:.1f}MB "
                f"(threshold: {self.alert_thresholds['memory_mb']}MB)"
            )
        
        # Componentes down
        if not health.data_collection_ok:
            alerts.append("❌ Data Collection: DOWN")
        if not health.telegram_ok:
            alerts.append("❌ Telegram: DOWN")
        if not health.database_ok:
            alerts.append("❌ Database: DOWN")
        
        # Registrar alertas
        for alert in alerts:
            self._send_alert(alert)
        
        return alerts
    
    def _send_alert(self, alert_message: str):
        """
        Envia alerta via Telegram se disponível
        
        Args:
            alert_message: Mensagem de alerta
        """
        try:
            logger.warning(alert_message)
            
            # Enviar via Telegram se disponível
            if self.telegram:
                try:
                    self.telegram.send_signal({
                        'signal': 'SYSTEM ALERT',
                        'confidence': 1.0,
                        'message': alert_message
                    })
                except:
                    pass  # Falha silenciosa se Telegram não estiver disponível
            
            # Registrar no histórico
            self.alerts_sent.append({
                'timestamp': datetime.now(),
                'message': alert_message
            })
            
            # Manter apenas últimos 100
            if len(self.alerts_sent) > 100:
                self.alerts_sent = self.alerts_sent[-100:]
                
        except Exception as e:
            logger.error(f"Erro ao enviar alerta: {e}")


class AutoRecovery:
    """Sistema de recuperação automática"""
    
    def __init__(self):
        """Inicializa sistema de recuperação"""
        self.recovery_history: List[Dict[str, Any]] = []
        self.retry_counts: Dict[str, int] = {}
    
    def handle_error(self, component: str, error: Exception, 
                    recovery_func=None) -> bool:
        """
        Trata erro e tenta recuperação
        
        Args:
            component: Nome do componente
            error: Exception
            recovery_func: Função para recuperação (opcional)
        
        Returns:
            True se recuperação bem-sucedida
        """
        retry_count = self.retry_counts.get(component, 0)
        max_retries = 3
        
        logger.warning(
            f"Error em {component}: {str(error)[:100]}\n"
            f"Tentativa {retry_count + 1}/{max_retries}"
        )
        
        if retry_count < max_retries:
            try:
                if recovery_func:
                    recovery_func()
                
                self.retry_counts[component] = retry_count + 1
                
                # Se recuperou, resetar contador
                logger.info(f"✅ {component} recuperado")
                self.retry_counts[component] = 0
                
                return True
            except Exception as recovery_error:
                logger.error(f"Falha na recuperação de {component}: {recovery_error}")
                return False
        else:
            logger.critical(f"❌ {component} falhou após {max_retries} tentativas")
            self.recovery_history.append({
                'component': component,
                'timestamp': datetime.now(),
                'error': str(error),
                'status': 'FAILED'
            })
            return False
    
    def reset(self, component: str = None):
        """
        Reseta retry counter
        
        Args:
            component: Component a resetar (None = todos)
        """
        if component:
            self.retry_counts[component] = 0
        else:
            self.retry_counts.clear()
