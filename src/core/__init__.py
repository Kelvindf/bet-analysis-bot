"""
Inicialização do módulo core
"""
from .types import (
    GameType,
    SignalType,
    SignalStatus,
    StrategyResult,
    Signal,
    BlazeData,
    PerformanceMetric,
    SystemHealth
)
from .exceptions import (
    BetAnalysisPlatformError,
    ConfigurationError,
    DataCollectionError,
    DataValidationError,
    DatabaseError,
    StrategyError,
    TelegramError,
    CacheError,
    MonitoringError
)
from .decorators import (
    retry,
    timing,
    log_errors,
    cache,
    validate_input
)

__all__ = [
    # Types
    'GameType',
    'SignalType',
    'SignalStatus',
    'StrategyResult',
    'Signal',
    'BlazeData',
    'PerformanceMetric',
    'SystemHealth',
    # Exceptions
    'BetAnalysisPlatformError',
    'ConfigurationError',
    'DataCollectionError',
    'DataValidationError',
    'DatabaseError',
    'StrategyError',
    'TelegramError',
    'CacheError',
    'MonitoringError',
    # Decorators
    'retry',
    'timing',
    'log_errors',
    'cache',
    'validate_input'
]
