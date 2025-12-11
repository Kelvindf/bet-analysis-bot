"""
Modelos de banco de dados usando SQLAlchemy
Define o schema de dados
"""
from sqlalchemy import (
    create_engine,
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    Text,
    JSON,
    Index,
    UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class SignalModel(Base):
    """Modelo para sinais gerados"""
    __tablename__ = 'signals'
    
    id = Column(String(100), primary_key=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    game = Column(String(50), index=True)
    signal_type = Column(String(20))
    confidence = Column(Float)
    strategies_passed = Column(Integer, default=0)
    final_confidence = Column(Float, default=0.0)
    
    # Resultado da aposta
    status = Column(String(20), default='pending', index=True)  # pending, win, loss, cancelled
    verified_at = Column(DateTime, nullable=True)
    
    # Metadados
    metadata_json = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    def __repr__(self):
        return f"<Signal {self.id}: {self.signal_type} {self.confidence:.1%} [{self.status}]>"


class RawDataModel(Base):
    """Modelo para dados brutos coletados"""
    __tablename__ = 'raw_data'
    
    id = Column(String(100), primary_key=True)
    game = Column(String(50), index=True)
    timestamp = Column(DateTime, index=True)
    result = Column(String(50))
    price = Column(Float, nullable=True)
    
    # Dados completos (JSON)
    data_json = Column(JSON)
    
    # Metadados
    source = Column(String(100), default='blaze_api')
    valid = Column(Boolean, default=True)
    hash_value = Column(String(64), unique=True)  # Para deduplicação
    
    collected_at = Column(DateTime, default=datetime.now, index=True)
    
    def __repr__(self):
        return f"<RawData {self.id}: {self.game} at {self.timestamp}>"


class PerformanceMetricModel(Base):
    """Modelo para métricas de performance agregadas"""
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    period = Column(String(50), index=True)  # hourly, daily, weekly, monthly
    timestamp = Column(DateTime, index=True)
    
    total_signals = Column(Integer, default=0)
    win_count = Column(Integer, default=0)
    loss_count = Column(Integer, default=0)
    pending_count = Column(Integer, default=0)
    
    # Confiança
    avg_confidence = Column(Float, default=0.0)
    best_confidence = Column(Float, default=0.0)
    worst_confidence = Column(Float, default=0.0)
    
    # Estratégias
    avg_strategies = Column(Float, default=0.0)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.now)
    
    __table_args__ = (
        Index('idx_period_timestamp', 'period', 'timestamp'),
        UniqueConstraint('period', 'timestamp', name='uq_period_timestamp'),
    )
    
    def __repr__(self):
        return f"<Metric {self.period} {self.timestamp}: WR={self.win_count}/{self.total_signals}>"


class EventModel(Base):
    """Modelo para eventos (logs estruturados)"""
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    level = Column(String(20), index=True)  # INFO, WARNING, ERROR, CRITICAL
    source = Column(String(100))
    message = Column(Text)
    traceback = Column(Text, nullable=True)
    
    # Metadados
    context_json = Column(JSON, default={})
    resolved = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('idx_timestamp_level', 'timestamp', 'level'),
        Index('idx_source_timestamp', 'source', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Event {self.timestamp} [{self.level}] {self.source}>"


class CacheModel(Base):
    """Modelo para cache persistente"""
    __tablename__ = 'cache'
    
    key = Column(String(255), primary_key=True)
    value = Column(Text)
    expires_at = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Cache {self.key}>"


class SystemStateModel(Base):
    """Modelo para estado do sistema"""
    __tablename__ = 'system_state'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    healthy = Column(Boolean, default=True)
    uptime_seconds = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    
    signals_processed = Column(Integer, default=0)
    data_collection_ok = Column(Boolean, default=True)
    telegram_ok = Column(Boolean, default=True)
    database_ok = Column(Boolean, default=True)
    
    memory_usage_mb = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<SystemState {self.timestamp}: healthy={self.healthy}>"


class GameResultModel(Base):
    """Modelo para armazenar resultados reais de jogos"""
    __tablename__ = 'game_results'
    
    id = Column(String(100), primary_key=True)  # game_id_resultado
    timestamp = Column(DateTime, default=datetime.now, index=True)
    game = Column(String(50), index=True)  # Double ou Crash
    
    # Resultado real do jogo
    result = Column(String(50), index=True)  # Vermelho, Preto, Suba, Caia para Double / Preto, Suba, Caia para Crash
    price = Column(Float, nullable=True)  # Multiplicador para Crash
    odds = Column(Float, default=1.9)  # Odds do resultado
    
    # Correlação com sinal gerado (se houve)
    signal_id = Column(String(100), nullable=True, index=True)  # FK para signals.id
    signal_matched = Column(Boolean, default=False)  # Se o sinal acertou o resultado
    
    # Dados completos do resultado
    raw_data_json = Column(JSON, default={})
    
    # Análise posterior
    analyzed = Column(Boolean, default=False)
    analysis_json = Column(JSON, default={})
    
    collected_at = Column(DateTime, default=datetime.now, index=True)
    
    def __repr__(self):
        return f"<GameResult {self.id}: {self.game} {self.result}>"


def init_db(db_path: str = 'data/db/analysis.db') -> sessionmaker:
    """
    Inicializa o banco de dados
    
    Args:
        db_path: Caminho para o arquivo SQLite
    
    Returns:
        Session factory para criar sessões de BD
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    engine = create_engine(
        f'sqlite:///{db_path}',
        echo=False,
        pool_pre_ping=True  # Validar conexões antes de usar
    )
    
    # Criar todas as tabelas
    Base.metadata.create_all(engine)
    
    # Retornar factory de sessões
    return sessionmaker(bind=engine)
