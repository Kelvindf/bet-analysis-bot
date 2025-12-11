"""
Decoradores úteis para o sistema
"""
import functools
import logging
import time
from typing import Callable, Any, Optional
from .exceptions import RetryableError

logger = logging.getLogger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorador para retry com backoff exponencial
    
    Uso:
        @retry(max_attempts=3, delay=1.0)
        def api_call():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except RetryableError as e:
                    if attempt == max_attempts:
                        logger.error(f"Falhou após {max_attempts} tentativas: {func.__name__}")
                        raise
                    
                    logger.warning(
                        f"Tentativa {attempt}/{max_attempts} falhou para {func.__name__}. "
                        f"Aguardando {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1
        
        return wrapper
    return decorator


def timing(func: Callable) -> Callable:
    """
    Decorador para medir tempo de execução
    
    Uso:
        @timing
        def slow_function():
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        
        logger.debug(f"{func.__name__} levou {elapsed:.2f}s")
        return result
    
    return wrapper


def log_errors(logger_instance: Optional[logging.Logger] = None):
    """
    Decorador para registrar erros
    
    Uso:
        @log_errors()
        def risky_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log = logger_instance or logger
                log.error(
                    f"Erro em {func.__name__}: {str(e)}",
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def cache(ttl_seconds: int = 300):
    """
    Decorador para cache com TTL
    
    Uso:
        @cache(ttl_seconds=600)
        def expensive_function(arg1, arg2):
            ...
    """
    cache_dict = {}
    cache_times = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Criar chave de cache
            key = (func.__name__, args, tuple(sorted(kwargs.items())))
            
            # Verificar se está em cache e não expirou
            if key in cache_dict:
                cached_time = cache_times.get(key, 0)
                if time.time() - cached_time < ttl_seconds:
                    return cache_dict[key]
            
            # Executar e cachear
            result = func(*args, **kwargs)
            cache_dict[key] = result
            cache_times[key] = time.time()
            
            return result
        
        return wrapper
    return decorator


def validate_input(**validators):
    """
    Decorador para validar inputs
    
    Uso:
        @validate_input(
            confidence=lambda x: 0 <= x <= 1,
            signal_type=lambda x: x in ['Vermelho', 'Preto']
        )
        def process_signal(confidence, signal_type):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Validar kwargs
            for param, validator in validators.items():
                if param in kwargs:
                    value = kwargs[param]
                    if not validator(value):
                        raise ValueError(
                            f"Validação falhou para {param}={value} na função {func.__name__}"
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
