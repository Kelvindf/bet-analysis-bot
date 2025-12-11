"""
Decision Cache - Memoization com TTL

Otimização por Memoização (Técnica: Dynamic Programming Cache)

OBJETIVO:
    - Cache de decisões de sinais similares
    - Reutilizar resultados em vez de recalcular
    - Ganho esperado: -25% tempo computação, -40% CPU

ESTRUTURA:
    Key: hash(game + pattern + hour + trend)
    Value: {result, confidence, timestamp}
    TTL: 60 minutos

HIT RATE ESPERADO: 15-20%
    - Jogos repetidos (Double → Double)
    - Padrões recorrentes (VermelhoxPreto)
    - Mesma hora do dia (19:00-20:00)
    
ECONOMIA:
    - Sem cache: 100 sinais = 100 validações
    - Com cache: 100 sinais = 85 validações (~15% cache hit)
    - Economia por hit: ~100ms de computação
    - Total economizado: 15 sinais x 100ms = 1.5s / 100 sinais
"""

import logging
import hashlib
from typing import Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrada no cache com timestamp para TTL"""
    result: str  # 'PASS', 'WEAK', 'REJECT'
    confidence: float
    details: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    hits: int = 0  # Número de vezes que foi usado
    
    def is_expired(self, ttl_minutes: int = 60) -> bool:
        """Verifica se cache expirou"""
        age = datetime.now() - self.timestamp
        return age > timedelta(minutes=ttl_minutes)
    
    def __repr__(self):
        age_min = int((datetime.now() - self.timestamp).total_seconds() / 60)
        return f"CacheEntry({self.result}, conf={self.confidence:.2f}, age={age_min}min, hits={self.hits})"


class DecisionCache:
    """
    Cache de decisões de sinais com memoização e TTL
    
    Exemplo:
        cache = DecisionCache(ttl_minutes=60)
        
        # Verificar cache
        cached = cache.get('Double', 'VermelhoPorSaida', 19)
        if cached:
            return cached
        
        # Calcular e armazenar
        result = calcular_sinal()
        cache.set('Double', 'VermelhoPorSaida', 19, result)
    """
    
    def __init__(self, max_entries: int = 10000, ttl_minutes: int = 60):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_entries = max_entries
        self.ttl_minutes = ttl_minutes
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'total_cached': 0
        }
        logger.info(f"[CACHE] Iniciado: max={max_entries}, ttl={ttl_minutes}min")
    
    def _make_key(self, game: str, pattern: str, hour: int, 
                  trend: str = '', game_type: str = '') -> str:
        """
        Cria key única combinando features principais
        
        Features:
            - game: 'Double' ou 'Crash'
            - pattern: 'VermelhoPorSaida', 'PretoLongo', etc
            - hour: 0-23 (hora do dia)
            - trend: 'UP', 'DOWN', 'NEUTRAL'
            - game_type: 'Suba', 'Caia' para Crash
        """
        # Normalizar inputs
        game = str(game).upper()
        pattern = str(pattern).upper()
        hour = int(hour) % 24
        trend = str(trend).upper()
        game_type = str(game_type).upper()
        
        # Criar string para hash
        combined = f"{game}#{pattern}#{hour}#{trend}#{game_type}"
        key = hashlib.md5(combined.encode()).hexdigest()[:16]
        
        return key
    
    def get(self, game: str, pattern: str, hour: int,
            trend: str = '', game_type: str = '') -> Optional[Tuple[str, float, Dict]]:
        """
        Recupera decisão em cache
        
        Returns:
            (result, confidence, details) ou None se não encontrado/expirado
        """
        key = self._make_key(game, pattern, hour, trend, game_type)
        
        if key not in self.cache:
            self.stats['misses'] += 1
            return None
        
        entry = self.cache[key]
        
        # Verificar expiração
        if entry.is_expired(self.ttl_minutes):
            del self.cache[key]
            self.stats['misses'] += 1
            logger.debug(f"[CACHE] Expirado: {key} (age={self.ttl_minutes}min)")
            return None
        
        # Cache hit!
        entry.hits += 1
        self.stats['hits'] += 1
        
        logger.debug(f"[CACHE HIT] {game}/{pattern}/h{hour} → {entry.result} "
                    f"(conf={entry.confidence:.2f}, hits={entry.hits})")
        
        return (entry.result, entry.confidence, entry.details)
    
    def set(self, game: str, pattern: str, hour: int,
            result: str, confidence: float, details: Dict = None,
            trend: str = '', game_type: str = ''):
        """
        Armazena decisão em cache
        
        Args:
            game: 'Double' ou 'Crash'
            pattern: Nome do padrão detectado
            hour: Hora do dia (0-23)
            result: 'PASS', 'WEAK' ou 'REJECT'
            confidence: Confiança (0.0-1.0)
            details: Dict com detalhes adicionais
            trend: Tendência observada
            game_type: Tipo de jogo (para Crash)
        """
        if details is None:
            details = {}
        
        key = self._make_key(game, pattern, hour, trend, game_type)
        
        # LRU Eviction: se cache cheio, remover mais antigo
        if len(self.cache) >= self.max_entries:
            oldest_key = min(
                self.cache.keys(),
                key=lambda k: self.cache[k].timestamp
            )
            del self.cache[oldest_key]
            self.stats['evictions'] += 1
            logger.debug(f"[CACHE] Eviction: removido {oldest_key} (cache cheio)")
        
        # Armazenar
        entry = CacheEntry(
            result=result,
            confidence=confidence,
            details=details,
            timestamp=datetime.now()
        )
        self.cache[key] = entry
        self.stats['total_cached'] = len(self.cache)
        
        logger.debug(f"[CACHE SET] {game}/{pattern}/h{hour} = {result} "
                    f"(conf={confidence:.2f})")
    
    def clear(self):
        """Limpa todo o cache"""
        self.cache.clear()
        logger.info("[CACHE] Limpo completamente")
    
    def clear_expired(self) -> int:
        """
        Remove todas as entradas expiradas
        
        Returns:
            Número de entradas removidas
        """
        expired_keys = [
            k for k, v in self.cache.items()
            if v.is_expired(self.ttl_minutes)
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        count = len(expired_keys)
        self.stats['total_cached'] = len(self.cache)
        
        if count > 0:
            logger.info(f"[CACHE] Removidas {count} entradas expiradas")
        
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_entries': len(self.cache),
            'max_entries': self.max_entries,
            'cache_usage_pct': (len(self.cache) / self.max_entries * 100),
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'total_requests': total_requests,
            'hit_rate_pct': round(hit_rate, 1),
            'evictions': self.stats['evictions'],
            'ttl_minutes': self.ttl_minutes,
            'memory_estimate_mb': round(len(self.cache) * 0.001, 2)  # Aprox 1KB por entry
        }
    
    def print_stats(self):
        """Imprime estatísticas formatadas"""
        stats = self.get_stats()
        print("\n" + "="*60)
        print("ESTATÍSTICAS DO CACHE DE DECISÕES")
        print("="*60)
        print(f"Entradas ativas: {stats['total_entries']}/{stats['max_entries']} "
              f"({stats['cache_usage_pct']:.1f}% utilizado)")
        print(f"Hit rate: {stats['hit_rate_pct']:.1f}% "
              f"({stats['hits']} hits em {stats['total_requests']} requisições)")
        print(f"Evictions (LRU): {stats['evictions']}")
        print(f"TTL: {stats['ttl_minutes']} minutos")
        print(f"Memória estimada: {stats['memory_estimate_mb']} MB")
        print("="*60 + "\n")
    
    def __repr__(self):
        stats = self.get_stats()
        return (f"DecisionCache(entries={stats['total_entries']}, "
                f"hit_rate={stats['hit_rate_pct']:.1f}%, "
                f"usage={stats['cache_usage_pct']:.1f}%)")


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    # Criar cache
    cache = DecisionCache(ttl_minutes=5, max_entries=100)
    
    # Simular alguns acessos
    for i in range(10):
        # 50% de cache hits
        if i % 2 == 0:
            # Repetir mesmo padrão
            result = cache.get('Double', 'VermelhoPorSaida', 19, 'UP')
            if result:
                print(f"✓ Cache hit {i}: {result}")
            else:
                print(f"✗ Cache miss {i}")
                cache.set('Double', 'VermelhoPorSaida', 19, 'PASS', 0.85,
                         trend='UP', details={'reason': 'test'})
        else:
            # Novo padrão
            cache.set('Crash', 'SubaLonga', 20, 'WEAK', 0.65, trend='DOWN')
    
    # Mostrar estatísticas
    cache.print_stats()
