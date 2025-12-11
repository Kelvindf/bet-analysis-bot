"""
Tipos e classes base compartilhadas
Centraliza definições de tipos para todo o sistema
"""
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional, List
from decimal import Decimal


class GameType(Enum):
    """Tipos de jogos disponíveis"""
    DOUBLE = "Double"
    CRASH = "Crash"
    MINES = "Mines"
    LUCKY = "Lucky"


class SignalType(Enum):
    """Tipos de sinais"""
    RED = "Vermelho"
    BLACK = "Preto"
    UP = "Suba"
    DOWN = "Caia"
    UNKNOWN = "Desconhecido"


class SignalStatus(Enum):
    """Estados possíveis de um sinal"""
    PENDING = "pending"      # Aguardando resultado
    WIN = "win"              # Acertou
    LOSS = "loss"            # Errou
    CANCELLED = "cancelled"  # Cancelado
    EXPIRED = "expired"      # Expirou


class StrategyResult(Enum):
    """Resultado de uma estratégia"""
    PASS = "PASS"
    WEAK = "WEAK"
    REJECT = "REJECT"


@dataclass
class Signal:
    """Sinal de aposta processado"""
    id: str
    game: GameType
    signal_type: SignalType
    confidence: float  # 0.0 a 1.0
    timestamp: datetime
    strategies_passed: int = 0
    final_confidence: float = 0.0
    bet_size: float = 0.0  # Tamanho da aposta recomendada
    
    # Resultado
    status: SignalStatus = SignalStatus.PENDING
    verified_at: Optional[datetime] = None
    
    # Metadados
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Valida valores após inicialização"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence deve estar entre 0 e 1, recebido: {self.confidence}")
        if not 0 <= self.strategies_passed <= 6:
            raise ValueError(f"Strategies_passed deve estar entre 0 e 6, recebido: {self.strategies_passed}")


@dataclass
class BlazeData:
    """Dados brutos coletados da Blaze API"""
    id: str
    game: GameType
    timestamp: datetime
    result: str  # Resultado real
    price: Optional[float] = None  # Para Crash
    data: Dict[str, Any] = field(default_factory=dict)  # Dados completos
    
    # Metadados de coleta
    collected_at: datetime = field(default_factory=datetime.now)
    source: str = "blaze_api"
    valid: bool = True


@dataclass
class PerformanceMetric:
    """Métrica de performance agregada"""
    period: str  # 'hourly', 'daily', 'weekly'
    timestamp: datetime
    total_signals: int
    win_count: int
    loss_count: int
    pending_count: int = 0
    
    @property
    def win_rate(self) -> float:
        """Taxa de acerto (%)"""
        verified = self.win_count + self.loss_count
        if verified == 0:
            return 0.0
        return self.win_count / verified
    
    @property
    def win_rate_pct(self) -> str:
        """Taxa de acerto formatada"""
        return f"{self.win_rate * 100:.1f}%"


@dataclass
class SystemHealth:
    """Saúde do sistema"""
    healthy: bool
    timestamp: datetime
    uptime_seconds: float
    last_error: Optional[str] = None
    signals_processed: int = 0
    data_collection_ok: bool = True
    telegram_ok: bool = True
    database_ok: bool = True
    memory_usage_mb: float = 0.0
    
    def is_healthy(self) -> bool:
        """Sistema está saudável?"""
        return (
            self.healthy and
            self.data_collection_ok and
            self.telegram_ok and
            self.database_ok and
            self.memory_usage_mb < 500  # Alerta se > 500MB
        )
