"""
Sistema de logging estruturado com múltiplos handlers
"""
import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

# Cores para console
class ColoredFormatter(logging.Formatter):
    """Formatter com cores para console"""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[41m',   # Red background
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


class JsonFormatter(logging.Formatter):
    """Formatter que gera logs em JSON estruturado"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Adicionar info de exceção se houver
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Adicionar campos customizados
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    log_dir: str = 'logs',
    level: int = logging.INFO,
    console: bool = True,
    structured: bool = True
) -> logging.Logger:
    """
    Configura sistema de logging completo
    
    Args:
        log_dir: Diretório para logs
        level: Nível de log (DEBUG, INFO, WARNING, ERROR)
        console: Mostrar logs no console?
        structured: Usar logs estruturados (JSON)?
    
    Returns:
        Logger configurado
    """
    # Criar diretório de logs
    os.makedirs(log_dir, exist_ok=True)
    
    # Logger raiz
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Remover handlers antigos
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Format padrão
    if structured:
        log_format = JsonFormatter()
    else:
        log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Handler: Console
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        if not structured:
            console_handler.setFormatter(ColoredFormatter(
                '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                datefmt='%H:%M:%S'
            ))
        else:
            console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)
    
    # Handler: Arquivo geral (rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    
    # Handler: Arquivo de erros apenas
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'errors.log'),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    logger.addHandler(error_handler)
    
    # Handler: Arquivo de performance
    perf_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'performance.log'),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    perf_handler.setLevel(logging.DEBUG)
    perf_handler.setFormatter(log_format)
    
    # Adicionar handler de performance ao logger de performance
    perf_logger = logging.getLogger('performance')
    perf_logger.addHandler(perf_handler)
    perf_logger.setLevel(logging.DEBUG)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtém logger nomeado
    
    Uso:
        logger = get_logger(__name__)
        logger.info("Mensagem")
    """
    return logging.getLogger(name)


def log_with_context(logger: logging.Logger, level: int, message: str, **context):
    """
    Registra log com contexto adicional
    
    Uso:
        log_with_context(
            logger, logging.INFO, "Sinal processado",
            signal_id='sig_123',
            confidence=0.85
        )
    """
    extra_info = {k: v for k, v in context.items()}
    
    # Para Python 3.8+, usar extra
    logger.log(
        level,
        message,
        extra={'extra': extra_info}
    )


# Exportar
__all__ = [
    'setup_logging',
    'get_logger',
    'log_with_context',
    'ColoredFormatter',
    'JsonFormatter'
]
