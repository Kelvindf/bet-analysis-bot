"""
Repository Pattern - Data Access Layer
Abstração para acesso ao banco de dados
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from contextlib import contextmanager
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import desc, func, and_

from .models import (
    SignalModel, RawDataModel, PerformanceMetricModel,
    EventModel, CacheModel, SystemStateModel, GameResultModel
)
from core.types import Signal, SignalStatus
from core.exceptions import DatabaseError


class Repository:
    """Classe base para repositórios"""
    
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager para sessões do BD"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise DatabaseError(f"Erro de banco de dados: {str(e)}") from e
        finally:
            session.close()


class SignalRepository(Repository):
    """Operações com sinais"""
    
    def save(self, signal: Signal) -> None:
        """Salva um sinal no BD"""
        with self.get_session() as session:
            model = SignalModel(
                id=signal.id,
                timestamp=signal.timestamp,
                game=signal.game.value,
                signal_type=signal.signal_type.value,
                confidence=signal.confidence,
                strategies_passed=signal.strategies_passed,
                final_confidence=signal.final_confidence,
                status=signal.status.value,
                metadata_json=signal.metadata
            )
            session.add(model)
    
    def get_by_id(self, signal_id: str) -> Optional[Signal]:
        """Recupera um sinal por ID"""
        with self.get_session() as session:
            model = session.query(SignalModel).filter_by(id=signal_id).first()
            return self._model_to_signal(model) if model else None
    
    def get_pending(self, hours: int = 24) -> List[Signal]:
        """Retorna sinais pendentes das últimas N horas"""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self.get_session() as session:
            models = session.query(SignalModel).filter(
                and_(
                    SignalModel.status == 'pending',
                    SignalModel.timestamp > cutoff
                )
            ).all()
            return [self._model_to_signal(m) for m in models]
    
    def verify_result(self, signal_id: str, won: bool) -> None:
        """Registra resultado de um sinal"""
        with self.get_session() as session:
            signal = session.query(SignalModel).filter_by(id=signal_id).first()
            if signal:
                signal.status = 'win' if won else 'loss'
                signal.verified_at = datetime.now()
    
    def get_stats(self, game: Optional[str] = None, hours: int = 24) -> Dict[str, Any]:
        """Calcula estatísticas de sinais"""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self.get_session() as session:
            query = session.query(SignalModel).filter(
                SignalModel.timestamp > cutoff
            )
            
            if game:
                query = query.filter_by(game=game)
            
            # Contar resultados
            total = query.count()
            wins = query.filter_by(status='win').count()
            losses = query.filter_by(status='loss').count()
            pending = query.filter_by(status='pending').count()
            
            # Confiança média
            avg_confidence = session.query(
                func.avg(SignalModel.confidence)
            ).filter(SignalModel.timestamp > cutoff).scalar() or 0.0
            
            return {
                'total': total,
                'wins': wins,
                'losses': losses,
                'pending': pending,
                'win_rate': wins / (wins + losses) if (wins + losses) > 0 else 0,
                'avg_confidence': float(avg_confidence)
            }
    
    def get_recent(self, limit: int = 10) -> List[Signal]:
        """Retorna N sinais mais recentes verificados"""
        with self.get_session() as session:
            models = session.query(SignalModel).filter(
                SignalModel.status.in_(['win', 'loss'])
            ).order_by(desc(SignalModel.verified_at)).limit(limit).all()
            return [self._model_to_signal(m) for m in models]
    
    @staticmethod
    def _model_to_signal(model: SignalModel) -> Signal:
        """Converte modelo SQLAlchemy para Signal"""
        from core.types import GameType, SignalType
        
        return Signal(
            id=model.id,
            game=GameType(model.game),
            signal_type=SignalType(model.signal_type),
            confidence=model.confidence,
            timestamp=model.timestamp,
            strategies_passed=model.strategies_passed,
            final_confidence=model.final_confidence,
            status=SignalStatus(model.status),
            verified_at=model.verified_at,
            metadata=model.metadata_json
        )


class RawDataRepository(Repository):
    """Operações com dados brutos"""
    
    def save(self, game: str, timestamp: datetime, result: str,
             data: Dict[str, Any], hash_value: str,
             price: Optional[float] = None) -> None:
        """Salva dados brutos coletados"""
        with self.get_session() as session:
            model = RawDataModel(
                id=f"{game}_{timestamp.timestamp()}",
                game=game,
                timestamp=timestamp,
                result=result,
                price=price,
                data_json=data,
                hash_value=hash_value
            )
            session.add(model)
    
    def get_latest(self, game: str, limit: int = 100) -> List[Dict]:
        """Retorna dados brutos mais recentes"""
        with self.get_session() as session:
            models = session.query(RawDataModel).filter_by(
                game=game
            ).order_by(desc(RawDataModel.timestamp)).limit(limit).all()
            
            return [m.data_json for m in models]
    
    def count_by_game(self, hours: int = 24) -> Dict[str, int]:
        """Conta dados coletados por jogo"""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self.get_session() as session:
            results = session.query(
                RawDataModel.game,
                func.count(RawDataModel.id)
            ).filter(
                RawDataModel.collected_at > cutoff
            ).group_by(RawDataModel.game).all()
            
            return {game: count for game, count in results}


class PerformanceMetricRepository(Repository):
    """Operações com métricas de performance"""
    
    def save(self, period: str, metrics: Dict[str, Any]) -> None:
        """Salva métrica agregada"""
        with self.get_session() as session:
            model = PerformanceMetricModel(
                period=period,
                timestamp=datetime.now(),
                total_signals=metrics.get('total', 0),
                win_count=metrics.get('wins', 0),
                loss_count=metrics.get('losses', 0),
                pending_count=metrics.get('pending', 0),
                avg_confidence=metrics.get('avg_confidence', 0.0),
                best_confidence=metrics.get('best_confidence', 0.0),
                worst_confidence=metrics.get('worst_confidence', 0.0),
                avg_strategies=metrics.get('avg_strategies', 0.0)
            )
            session.add(model)
    
    def get_latest(self, period: str, limit: int = 10) -> List[Dict]:
        """Retorna métricas mais recentes"""
        with self.get_session() as session:
            models = session.query(PerformanceMetricModel).filter_by(
                period=period
            ).order_by(desc(PerformanceMetricModel.timestamp)).limit(limit).all()
            
            return [{
                'timestamp': m.timestamp,
                'win_rate': m.win_count / (m.win_count + m.loss_count) if (m.win_count + m.loss_count) > 0 else 0,
                'total': m.total_signals,
                'wins': m.win_count
            } for m in models]


class EventRepository(Repository):
    """Operações com eventos (logs estruturados)"""
    
    def save(self, level: str, source: str, message: str,
             traceback: Optional[str] = None, context: Optional[Dict] = None) -> None:
        """Registra um evento"""
        with self.get_session() as session:
            model = EventModel(
                level=level,
                source=source,
                message=message,
                traceback=traceback,
                context_json=context or {}
            )
            session.add(model)
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict]:
        """Retorna erros recentes"""
        with self.get_session() as session:
            models = session.query(EventModel).filter(
                EventModel.level.in_(['ERROR', 'CRITICAL'])
            ).order_by(desc(EventModel.timestamp)).limit(limit).all()
            
            return [{
                'timestamp': m.timestamp,
                'level': m.level,
                'source': m.source,
                'message': m.message
            } for m in models]


class CacheRepository(Repository):
    """Operações com cache persistente"""
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Define valor em cache"""
        import json
        with self.get_session() as session:
            # Deletar se existe
            session.query(CacheModel).filter_by(key=key).delete()
            
            # Inserir novo
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            model = CacheModel(
                key=key,
                value=json.dumps(value) if not isinstance(value, str) else value,
                expires_at=expires_at
            )
            session.add(model)
    
    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache"""
        import json
        with self.get_session() as session:
            model = session.query(CacheModel).filter_by(key=key).first()
            
            if not model:
                return None
            
            # Verificar expiração
            if model.expires_at < datetime.now():
                session.delete(model)
                return None
            
            try:
                return json.loads(model.value)
            except:
                return model.value
    
    def clear_expired(self) -> int:
        """Remove entradas expiradas"""
        with self.get_session() as session:
            count = session.query(CacheModel).filter(
                CacheModel.expires_at < datetime.now()
            ).delete()
            return count


class GameResultRepository(Repository):
    """Operações com resultados de jogos"""
    
    def save(self, game_result: Dict[str, Any]) -> None:
        """Salva um resultado de jogo"""
        with self.get_session() as session:
            model = GameResultModel(
                id=game_result.get('id', f"result_{game_result.get('timestamp', datetime.now())}"),
                timestamp=game_result.get('timestamp', datetime.now()),
                game=game_result.get('game', 'Unknown'),
                result=game_result.get('result', 'Unknown'),
                price=game_result.get('price'),
                odds=game_result.get('odds', 1.9),
                signal_id=game_result.get('signal_id'),
                signal_matched=game_result.get('signal_matched', False),
                raw_data_json=game_result.get('raw_data', {}),
                analyzed=game_result.get('analyzed', False),
                analysis_json=game_result.get('analysis', {})
            )
            session.add(model)
    
    def get_by_id(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Recupera um resultado por ID"""
        with self.get_session() as session:
            model = session.query(GameResultModel).filter(
                GameResultModel.id == result_id
            ).first()
            
            if not model:
                return None
            
            return {
                'id': model.id,
                'timestamp': model.timestamp,
                'game': model.game,
                'result': model.result,
                'price': model.price,
                'odds': model.odds,
                'signal_id': model.signal_id,
                'signal_matched': model.signal_matched,
                'raw_data': model.raw_data_json,
                'analyzed': model.analyzed,
                'analysis': model.analysis_json
            }
    
    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retorna todos os resultados (últimos N registros)"""
        with self.get_session() as session:
            models = session.query(GameResultModel).order_by(
                desc(GameResultModel.timestamp)
            ).limit(limit).all()
            
            return [
                {
                    'id': m.id,
                    'timestamp': m.timestamp,
                    'game': m.game,
                    'result': m.result,
                    'signal_matched': m.signal_matched,
                    'signal_id': m.signal_id
                }
                for m in models
            ]
    
    def get_by_signal(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """Recupera resultado associado a um sinal"""
        with self.get_session() as session:
            model = session.query(GameResultModel).filter(
                GameResultModel.signal_id == signal_id
            ).first()
            
            if not model:
                return None
            
            return {
                'id': model.id,
                'timestamp': model.timestamp,
                'game': model.game,
                'result': model.result,
                'signal_matched': model.signal_matched,
                'price': model.price,
                'odds': model.odds
            }
    
    def get_unanalyzed(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Retorna resultados não analisados"""
        with self.get_session() as session:
            models = session.query(GameResultModel).filter(
                GameResultModel.analyzed == False
            ).order_by(GameResultModel.timestamp).limit(limit).all()
            
            return [
                {
                    'id': m.id,
                    'timestamp': m.timestamp,
                    'game': m.game,
                    'result': m.result,
                    'signal_id': m.signal_id,
                    'signal_matched': m.signal_matched,
                    'raw_data': m.raw_data_json
                }
                for m in models
            ]
    
    def update_analysis(self, result_id: str, analysis: Dict[str, Any]) -> None:
        """Atualiza análise de um resultado"""
        with self.get_session() as session:
            model = session.query(GameResultModel).filter(
                GameResultModel.id == result_id
            ).first()
            
            if model:
                model.analyzed = True
                model.analysis_json = analysis
    
    def get_win_rate_by_game(self, game: str, hours: int = 24) -> Dict[str, float]:
        """Calcula taxa de vitória para um jogo nos últimas N horas"""
        with self.get_session() as session:
            since = datetime.now() - timedelta(hours=hours)
            
            total = session.query(func.count(GameResultModel.id)).filter(
                and_(
                    GameResultModel.game == game,
                    GameResultModel.timestamp >= since,
                    GameResultModel.signal_id.isnot(None)  # Apenas com sinais
                )
            ).scalar()
            
            wins = session.query(func.count(GameResultModel.id)).filter(
                and_(
                    GameResultModel.game == game,
                    GameResultModel.timestamp >= since,
                    GameResultModel.signal_matched == True
                )
            ).scalar()
            
            if total == 0:
                return {'win_rate': 0.0, 'total': 0, 'wins': 0}
            
            return {
                'win_rate': wins / total,
                'total': total,
                'wins': wins
            }
    
    def get_results_by_timeframe(self, game: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Retorna resultados de um jogo nos últimas N horas"""
        with self.get_session() as session:
            since = datetime.now() - timedelta(hours=hours)
            
            models = session.query(GameResultModel).filter(
                and_(
                    GameResultModel.game == game,
                    GameResultModel.timestamp >= since
                )
            ).order_by(GameResultModel.timestamp).all()
            
            return [
                {
                    'id': m.id,
                    'timestamp': m.timestamp,
                    'result': m.result,
                    'signal_id': m.signal_id,
                    'signal_matched': m.signal_matched,
                    'price': m.price
                }
                for m in models
            ]
