"""
Integração de Persistência no Sistema Principal
FASE 2 - Conecta repositórios ao main.py

Uso:
    from integration import integrate_persistence
    integrate_persistence(platform)
"""
import logging
from datetime import datetime
from typing import List, Dict, Any

from core import Signal, SignalStatus
from database import (
    SignalRepository, RawDataRepository, 
    PerformanceMetricRepository, EventRepository,
    CacheRepository, init_db
)
from data_collection.validators import DataValidator

logger = logging.getLogger(__name__)


class PersistenceManager:
    """Gerenciador centralizado de persistência"""
    
    def __init__(self, db_path: str = 'data/db/analysis.db'):
        """
        Inicializa manager de persistência
        
        Args:
            db_path: Caminho para banco de dados SQLite
        """
        self.db_path = db_path
        self.Session = init_db(db_path)
        
        # Inicializar repositórios
        self.signals = SignalRepository(self.Session)
        self.raw_data = RawDataRepository(self.Session)
        self.metrics = PerformanceMetricRepository(self.Session)
        self.events = EventRepository(self.Session)
        self.cache = CacheRepository(self.Session)
        
        logger.info(f"✅ Persistência inicializada: {db_path}")
    
    def save_signal(self, signal: Signal) -> bool:
        """
        Salva sinal no banco de dados
        
        Args:
            signal: Sinal a salvar
        
        Returns:
            True se sucesso
        """
        try:
            self.signals.save(signal)
            logger.debug(f"💾 Sinal salvo: {signal.id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar sinal: {e}")
            return False
    
    def save_raw_data(self, game: str, data_list: List[Dict[str, Any]]) -> bool:
        """
        Salva dados brutos coletados
        
        Args:
            game: Tipo de jogo
            data_list: Lista de dados brutos
        
        Returns:
            True se sucesso
        """
        try:
            count = 0
            for data in data_list:
                try:
                    timestamp = data.get('timestamp', datetime.now())
                    result = data.get('result', 'unknown')
                    
                    # Criar hash para deduplicação
                    import hashlib
                    hash_value = hashlib.md5(
                        str(data).encode()
                    ).hexdigest()
                    
                    self.raw_data.save(
                        game=game,
                        timestamp=timestamp,
                        result=result,
                        data=data,
                        hash_value=hash_value,
                        price=data.get('price')
                    )
                    count += 1
                except Exception as e:
                    logger.debug(f"Erro ao salvar dado: {e}")
                    continue
            
            logger.info(f"💾 {count}/{len(data_list)} registros brutos salvos ({game})")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao salvar dados brutos: {e}")
            return False
    
    def verify_signal_result(self, signal_id: str, won: bool) -> bool:
        """
        Verifica resultado de um sinal
        
        Args:
            signal_id: ID do sinal
            won: True se ganhou, False se perdeu
        
        Returns:
            True se sucesso
        """
        try:
            self.signals.verify_result(signal_id, won)
            status = "WIN" if won else "LOSS"
            logger.info(f"✅ Resultado registrado: {signal_id} → {status}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao verificar resultado: {e}")
            return False
    
    def get_pending_signals(self, hours: int = 24) -> List[Signal]:
        """
        Obtém sinais pendentes de verificação
        
        Args:
            hours: Últimas N horas
        
        Returns:
            Lista de sinais pendentes
        """
        try:
            return self.signals.get_pending(hours=hours)
        except Exception as e:
            logger.error(f"❌ Erro ao buscar sinais pendentes: {e}")
            return []
    
    def get_performance_stats(self, game: str = None, hours: int = 24) -> Dict[str, Any]:
        """
        Obtém estatísticas de performance
        
        Args:
            game: Filtrar por jogo (opcional)
            hours: Últimas N horas
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            return self.signals.get_stats(game=game, hours=hours)
        except Exception as e:
            logger.error(f"❌ Erro ao obter stats: {e}")
            return {}
    
    def record_event(self, level: str, source: str, message: str, 
                    traceback: str = None, context: Dict = None) -> bool:
        """
        Registra evento (log estruturado)
        
        Args:
            level: INFO, WARNING, ERROR, CRITICAL
            source: Origem do evento
            message: Mensagem
            traceback: Traceback (opcional)
            context: Contexto JSON (opcional)
        
        Returns:
            True se sucesso
        """
        try:
            self.events.save(level, source, message, traceback, context)
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao registrar evento: {e}")
            return False
    
    def get_health_check(self) -> Dict[str, Any]:
        """
        Verifica saúde do sistema de persistência
        
        Returns:
            Dicionário com status de saúde
        """
        try:
            stats = self.signals.get_stats(hours=24)
            
            return {
                'database_ok': True,
                'signals_count': stats.get('total', 0),
                'win_rate': stats.get('win_rate', 0),
                'last_updated': datetime.now().isoformat(),
                'status': 'OK'
            }
        except Exception as e:
            logger.error(f"❌ Erro em health check: {e}")
            return {
                'database_ok': False,
                'error': str(e),
                'status': 'ERROR'
            }


def integrate_persistence(platform_instance):
    """
    Integra persistência na instância do BetAnalysisPlatform
    
    Args:
        platform_instance: Instância do BetAnalysisPlatform
    
    Exemplo:
        from main import BetAnalysisPlatform
        from integration import integrate_persistence
        
        platform = BetAnalysisPlatform()
        integrate_persistence(platform)
        platform.run()
    """
    # Inicializar manager de persistência
    platform_instance.persistence = PersistenceManager()
    
    # Patchear método de envio de sinais para auto-salvar
    original_send_signals = platform_instance.bot_manager.send_signals
    
    def send_signals_with_persistence(signals: List[Dict]):
        """Enveloper que salva sinais antes de enviar"""
        # Salvar cada sinal no BD
        for signal_dict in signals:
            try:
                signal = Signal(
                    id=signal_dict.get('game_id', f"sig_{datetime.now().timestamp()}"),
                    game=signal_dict.get('game'),
                    signal_type=signal_dict.get('signal_type'),
                    confidence=signal_dict.get('confidence', 0.0),
                    timestamp=datetime.now(),
                    strategies_passed=signal_dict.get('strategies_passed', 0),
                    metadata=signal_dict
                )
                platform_instance.persistence.save_signal(signal)
            except Exception as e:
                logger.warning(f"Erro ao salvar sinal: {e}")
        
        # Chamar método original
        return original_send_signals(signals)
    
    # Substituir método
    platform_instance.bot_manager.send_signals = send_signals_with_persistence
    
    logger.info("✅ Persistência integrada ao sistema")
    
    return platform_instance
