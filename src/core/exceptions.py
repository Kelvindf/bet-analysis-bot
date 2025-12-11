"""
Exceções customizadas do sistema
"""


class BetAnalysisPlatformError(Exception):
    """Exceção base"""
    pass


class ConfigurationError(BetAnalysisPlatformError):
    """Erro de configuração"""
    pass


class DataCollectionError(BetAnalysisPlatformError):
    """Erro ao coletar dados da Blaze"""
    pass


class DataValidationError(BetAnalysisPlatformError):
    """Erro ao validar dados coletados"""
    pass


class DatabaseError(BetAnalysisPlatformError):
    """Erro ao acessar banco de dados"""
    pass


class StrategyError(BetAnalysisPlatformError):
    """Erro ao processar estratégia"""
    pass


class TelegramError(BetAnalysisPlatformError):
    """Erro ao enviar mensagem Telegram"""
    pass


class CacheError(BetAnalysisPlatformError):
    """Erro de cache"""
    pass


class MonitoringError(BetAnalysisPlatformError):
    """Erro de monitoramento"""
    pass


class APIError(BetAnalysisPlatformError):
    """Erro de API externa"""
    pass


class TimeoutError(BetAnalysisPlatformError):
    """Timeout na operação"""
    pass


class RetryableError(BetAnalysisPlatformError):
    """Erro que pode ser retentado"""
    max_retries = 3
    pass
