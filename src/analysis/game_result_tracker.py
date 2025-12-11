"""
Game Result Tracker - Rastreia resultados reais de jogos
Correlaciona sinais gerados com resultados reais para análise e otimização
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from database import GameResultRepository

logger = logging.getLogger('analysis.game_result_tracker')


class GameResultTracker:
    """Rastreia e correlaciona resultados de jogos com sinais gerados"""
    
    def __init__(self, repo: GameResultRepository):
        """
        Inicializa o rastreador
        
        Args:
            repo: GameResultRepository para armazenar dados
        """
        self.repo = repo
        self.recent_results = {}  # Cache de resultados recentes
    
    def record_game_result(self, game_result: Dict[str, Any]) -> bool:
        """
        Registra o resultado de um jogo
        
        Args:
            game_result: Dict com {
                'id': resultado_id,
                'game': 'Double' ou 'Crash',
                'timestamp': datetime,
                'result': 'Vermelho'/'Preto'/'Suba'/'Caia',
                'price': float (para Crash),
                'odds': float,
                'signal_id': str (opcional - ID do sinal correlacionado),
                'raw_data': dict (dados completos)
            }
        
        Returns:
            True se salvo com sucesso
        """
        try:
            # Validar dados obrigatórios
            required_fields = ['id', 'game', 'timestamp', 'result', 'odds']
            if not all(field in game_result for field in required_fields):
                logger.warning(f"Resultado incompleto: {game_result}")
                return False
            
            # Processar: se há signal_id, marcar se acertou
            if game_result.get('signal_id'):
                # Aqui você correlaciona com o sinal gerado
                # Por enquanto, marcamos como True (será melhorado depois)
                game_result['signal_matched'] = True
            else:
                game_result['signal_matched'] = False
            
            # Salvar no banco
            self.repo.save(game_result)
            
            # Atualizar cache
            self.recent_results[game_result['id']] = game_result
            
            logger.info(f"[OK] Resultado registrado: {game_result['game']} {game_result['result']}")
            return True
            
        except Exception as e:
            logger.error(f"[ERRO] Erro ao registrar resultado: {str(e)}")
            return False
    
    def process_raw_data_as_results(self, raw_data: List[Dict[str, Any]], game: str) -> int:
        """
        Processa dados brutos coletados como resultados de jogos
        Útil para backfill de dados históricos
        
        Args:
            raw_data: Lista de dados brutos coletados
            game: Tipo de jogo ('Double' ou 'Crash')
        
        Returns:
            Número de resultados processados
        """
        count = 0
        
        for item in raw_data:
            try:
                result_id = f"{game}_{item.get('id', item.get('timestamp', datetime.now()))}"
                
                # Extrair resultado baseado no tipo de jogo
                if game == 'Double':
                    result = item.get('result', item.get('color', 'Unknown'))
                else:  # Crash
                    result = item.get('result', 'Preto')  # Default
                
                game_result = {
                    'id': result_id,
                    'game': game,
                    'timestamp': item.get('timestamp', datetime.now()),
                    'result': result,
                    'price': item.get('price'),
                    'odds': 1.9 if game == 'Double' else item.get('price', 1.0),
                    'signal_id': None,  # Sem correlação ainda
                    'signal_matched': False,
                    'raw_data': item,
                    'analyzed': False
                }
                
                if self.record_game_result(game_result):
                    count += 1
                    
            except Exception as e:
                logger.warning(f"[AVISO] Erro processando item: {str(e)}")
                continue
        
        logger.info(f"[OK] Processados {count} resultados de {game}")
        return count
    
    def correlate_with_signals(self, signal_id: str, game_result: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Correlaciona um sinal com seu resultado real
        
        Args:
            signal_id: ID do sinal gerado
            game_result: Resultado do jogo (opcional)
        
        Returns:
            Dict com correlação {
                'signal_id': str,
                'result': Dict,
                'matched': bool,
                'accuracy': float
            }
        """
        try:
            result = self.repo.get_by_signal(signal_id)
            
            if not result:
                return {
                    'signal_id': signal_id,
                    'result': None,
                    'matched': False,
                    'accuracy': 0.0
                }
            
            # Calcular se acertou
            matched = result.get('signal_matched', False)
            accuracy = 1.0 if matched else 0.0
            
            return {
                'signal_id': signal_id,
                'result': result,
                'matched': matched,
                'accuracy': accuracy
            }
            
        except Exception as e:
            logger.error(f"[ERRO] Erro correlacionando sinal: {str(e)}")
            return {
                'signal_id': signal_id,
                'result': None,
                'matched': False,
                'accuracy': 0.0
            }
    
    def get_performance_metrics(self, game: str, hours: int = 24) -> Dict[str, Any]:
        """
        Calcula métricas de performance para um jogo
        
        Args:
            game: Tipo de jogo ('Double' ou 'Crash')
            hours: Período em horas para análise
        
        Returns:
            Dict com métricas {
                'win_rate': float,
                'total_signals': int,
                'wins': int,
                'losses': int,
                'avg_odds': float,
                'period_hours': int
            }
        """
        try:
            stats = self.repo.get_win_rate_by_game(game, hours)
            results = self.repo.get_results_by_timeframe(game, hours)
            
            if not results:
                return {
                    'game': game,
                    'win_rate': 0.0,
                    'total_signals': 0,
                    'wins': 0,
                    'losses': 0,
                    'avg_odds': 0.0,
                    'period_hours': hours
                }
            
            # Calcular odds média
            odds_list = [r.get('price', 1.9) for r in results if r.get('price')]
            avg_odds = sum(odds_list) / len(odds_list) if odds_list else 1.9
            
            return {
                'game': game,
                'win_rate': stats.get('win_rate', 0.0),
                'total_signals': stats.get('total', 0),
                'wins': stats.get('wins', 0),
                'losses': stats.get('total', 0) - stats.get('wins', 0),
                'avg_odds': avg_odds,
                'period_hours': hours
            }
            
        except Exception as e:
            logger.error(f"[ERRO] Erro calculando métricas: {str(e)}")
            return {
                'game': game,
                'win_rate': 0.0,
                'total_signals': 0,
                'wins': 0,
                'losses': 0,
                'avg_odds': 0.0,
                'period_hours': hours
            }
    
    def get_recent_results(self, game: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retorna resultados recentes para um jogo
        
        Args:
            game: Tipo de jogo
            limit: Número máximo de resultados
        
        Returns:
            Lista de resultados recentes
        """
        try:
            return self.repo.get_results_by_timeframe(game, hours=24)[:limit]
        except Exception as e:
            logger.error(f"[ERRO] Erro obtendo resultados recentes: {str(e)}")
            return []
    
    def analyze_pattern_accuracy(self, pattern: str, game: str, hours: int = 24) -> Dict[str, float]:
        """
        Analisa acurácia de um padrão específico
        
        Args:
            pattern: Padrão analisado (ex: 'Preto', 'Suba')
            game: Tipo de jogo
            hours: Período de análise
        
        Returns:
            Dict com estatísticas do padrão
        """
        try:
            results = self.repo.get_results_by_timeframe(game, hours)
            
            if not results:
                return {'pattern': pattern, 'accuracy': 0.0, 'occurrences': 0}
            
            occurrences = sum(1 for r in results if r.get('result') == pattern)
            
            return {
                'pattern': pattern,
                'game': game,
                'accuracy': occurrences / len(results) if results else 0.0,
                'occurrences': occurrences,
                'total_results': len(results),
                'period_hours': hours
            }
            
        except Exception as e:
            logger.error(f"[ERRO] Erro analisando padrão: {str(e)}")
            return {'pattern': pattern, 'accuracy': 0.0, 'occurrences': 0}
