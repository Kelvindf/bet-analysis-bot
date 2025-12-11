"""
Plataforma de Análise de Apostas - Main Module

Integrado com Pipeline de 6 Estratégias:
- Strategy 1: Pattern Detection
- Strategy 2: Technical Validation
- Strategy 3: Confidence Filter
- Strategy 4: Confirmation Filter
- Strategy 5: Monte Carlo Validation (NOVO)
- Strategy 6: Run Test Validation (NOVO)
"""
import logging
import argparse
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os
import sys
import json
import time

# Adiciona o diretório src ao path
src_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, src_dir)

from data_collection.blaze_client_v2 import BlazeDataCollectorV2 as BlazeDataCollector
from analysis.statistical_analyzer import StatisticalAnalyzer
from analysis.strategy_pipeline import StrategyPipeline
from telegram_bot.bot_manager import TelegramBotManager
from config.settings import Settings
from strategies.kelly_criterion import KellyCriterion

# Import drawdown manager (relative to scripts/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from drawdown_manager import DrawdownManager

# Adicione este import
from analysis.result_tracker import ResultTracker
from analysis.game_result_tracker import GameResultTracker

# FASE 2: Novos módulos de otimização
from learning.optimal_sequencer import OptimalSequencer
from learning.signal_pruner import SignalPruner
from learning.meta_learner import MetaLearner, MetaContext

# FASE 3: Feedback Loop Automático
from learning.feedback_loop import FeedbackLoop, SignalResult

# FASE 3: A/B Testing Framework
from learning.ab_test import ABTestManager, TestResult

# Tipos com validação
from core import Signal, SignalType, GameType

# Banco de dados
from database import SignalRepository, GameResultRepository, init_db

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bet_analysis.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BetAnalysisPlatform:
    """Classe principal da plataforma de análise de apostas"""

    def __init__(self, test_mode: bool = False):
        load_dotenv()
        self.settings = Settings()
        self.setup_directories()

        self.data_collector = BlazeDataCollector()
        self.analyzer = StatisticalAnalyzer()
        self.bot_manager = TelegramBotManager()
        self.test_mode = test_mode
        
        # Inicializar novo pipeline com 6 estratégias
        self.pipeline = StrategyPipeline(logger)
        
        # Inicializar Kelly Criterion e Drawdown Manager
        self.kelly = KellyCriterion(
            initial_bankroll=float(os.getenv('KELLY_BANKROLL', '1000.0')),
            kelly_fraction=float(os.getenv('KELLY_FRACTION', '0.25'))
        )
        self.drawdown = DrawdownManager(
            initial_bankroll=float(os.getenv('KELLY_BANKROLL', '1000.0')),
            max_drawdown_percent=float(os.getenv('MAX_DRAWDOWN_PERCENT', '5.0'))
        )
        
        # Estatísticas de coleta
        self.stats = {
            'signals_processed': 0,
            'signals_valid': 0,
            'signals_sent': 0,
            'colors_collected': 0,
            'start_time': datetime.now()
        }

        # Inicializar tracker de resultados
        self.tracker = ResultTracker()

        # Inicializa sessão do banco de dados
        self.Session = init_db()
        self.repo = SignalRepository(self.Session)
        self.result_repo = GameResultRepository(self.Session)
        self.game_result_tracker = GameResultTracker(self.result_repo)
        
        # FASE 2: Inicializar módulos de otimização
        self.optimal_sequencer = OptimalSequencer()
        self.signal_pruner = SignalPruner(min_threshold=0.02)  # 2% minimum profit
        self.meta_learner = MetaLearner()
        
        # FASE 3: Inicializar Feedback Loop Automático
        self.feedback_loop = FeedbackLoop(
            initial_confidence=0.65,
            initial_kelly=0.25,
            min_samples=50,  # Ajustar após 50 resultados
            adjustment_threshold=0.05  # 5% desvio máximo
        )
        
        # FASE 3: Inicializar A/B Testing Framework
        self.ab_test = ABTestManager(
            min_samples=100,  # 100 apostas mínimo de cada versão
            significance_level=0.05,  # 95% confiança
            analysis_interval_hours=24  # Analisar a cada 24h
        )

    def setup_directories(self):
        """Cria estrutura de diretórios necessária"""
        os.makedirs('data/raw', exist_ok=True)
        os.makedirs('data/processed', exist_ok=True)
        os.makedirs('logs', exist_ok=True)

    def run_analysis_cycle(self):
        """Executa um ciclo completo de coleta e análise com Pipeline de 6 Estratégias"""
        try:
            logger.info("[*] Iniciando ciclo de analise com Pipeline (6 estratégias)")

            # Coleta dados (novo cliente V2)
            logger.info("[*] Coletando dados...")
            all_data = self.data_collector.get_all_data(limit=100)
            
            if all_data and (all_data.get('double') or all_data.get('crash')):
                double_data = all_data.get('double', [])
                crash_data = all_data.get('crash', [])
                
                logger.info(f"[*] Coletados: {len(double_data)} Double + {len(crash_data)} Crash")
                
                # Preparar dados para análise
                # Converter listas em pandas DataFrame para compatibilidade com o analisador
                import pandas as pd

                # Crash -> DataFrame com coluna 'crash_point'
                try:
                    df_crash = pd.DataFrame(crash_data)
                except Exception:
                    df_crash = pd.DataFrame()

                # Double -> DataFrame com colunas 'color' e 'roll' (cria 'roll' sintético se não existir)
                try:
                    df_double = pd.DataFrame(double_data)
                except Exception:
                    df_double = pd.DataFrame()

                if 'roll' not in df_double.columns:
                    # gerar um número sintético 0-36 para compatibilidade
                    import numpy as _np
                    if not df_double.empty:
                        df_double['roll'] = _np.random.randint(0, 37, size=(len(df_double),))
                    else:
                        df_double['roll'] = []

                raw_data = {
                    'double': df_double,
                    'crash': df_crash,
                    'source': all_data.get('source', 'fallback')
                }
                
                # Analisa dados
                logger.info("[*] Analisando padroes...")
                analysis_results = self.analyzer.analyze_patterns(raw_data)

                # Gera sinais com NOVO PIPELINE (6 estratégias)
                logger.info("[*] Gerando sinais com Pipeline (6 estratégias)...")
                signals = self.generate_signals_with_pipeline(analysis_results, raw_data)

                # Verificar se trading está pausado por drawdown
                if self.drawdown.is_paused:
                    logger.warning(f"[AVISO] TRADING PAUSED: Drawdown {self.drawdown.get_status()['drawdown_percent']:.2f}% exceeded limit")
                    signals = []  # Não gerar novos sinais durante pausa
                
                # Envia para Telegram apenas sinais válidos
                if signals:
                    logger.info(f"[*] Enviando {len(signals)} sinal(is) válido(s) para Telegram...")
                    
                    # Calcular tamanho da aposta via Kelly Criterion
                    win_rate = self._calculate_recent_win_rate()
                    for signal in signals:
                        # Adicionar tamanho da aposta ao sinal
                        signal['bet_size'] = self.kelly.calculate_bet_size(
                            win_rate=win_rate,
                            odds=float(signal.get('odds', 1.9)),
                            min_bet=1.0
                        )
                        signal['kelly_fraction'] = self.kelly.kelly_fraction
                    
                    # Salvar sinais com toda informação importante
                    for signal in signals:
                        # Preparar dados para banco de dados
                        signal_data = {
                            'game_id': signal.get('game_id', f"sig_{uuid.uuid4().hex[:12]}"),
                            'game': signal.get('game', 'Double'),
                            'signal_type': signal.get('signal', 'Unknown'),
                            'confidence': signal.get('confidence', 0.0),
                            'strategies_passed': signal.get('strategies_passed', 0),
                            'timestamp': datetime.now(),
                            'bet_size': signal.get('bet_size', 0.0),
                            'odds': signal.get('odds', 1.9),
                            'kelly_fraction': self.kelly.kelly_fraction,
                            'bankroll': float(os.getenv('KELLY_BANKROLL', '1000.0')),
                            'drawdown_status': self.drawdown.get_status(),
                            'metadata': {
                                'data_source': raw_data.get('source', 'fallback'),
                                'colors_analyzed': len(self._extract_all_colors(raw_data)),
                                'analysis_results': str(analysis_results)
                            },
                            'optimal_bet_fraction': signal.get('optimal_bet_fraction', 0.25),
                            'signal_id': signal.get('game_id', f"sig_{uuid.uuid4().hex[:12]}")
                        }
                        
                        # Salvar para tracking de resultados
                        self.tracker.save_signal(signal_data)
                        
                        # Salvar no banco de dados com metadados
                        # Mapear tipo de sinal para enum
                        signal_type_map = {
                            'Vermelho': SignalType.RED,
                            'Preto': SignalType.BLACK,
                            'Suba': SignalType.UP,
                            'Caia': SignalType.DOWN
                        }
                        signal_type_enum = signal_type_map.get(signal_data['signal_type'], SignalType.UNKNOWN)
                        
                        db_signal = Signal(
                            id=signal_data['game_id'],
                            game=GameType.CRASH if signal_data['game'] == 'Crash' else GameType.DOUBLE,
                            signal_type=signal_type_enum,
                            confidence=signal_data['confidence'],
                            timestamp=signal_data['timestamp'],
                            strategies_passed=signal_data['strategies_passed'],
                            bet_size=signal_data['bet_size'],
                            metadata={
                                'odds': signal_data['odds'],
                                'kelly_fraction': signal_data['kelly_fraction'],
                                'bankroll': signal_data['bankroll'],
                                'drawdown_percent': signal_data['drawdown_status'].get('drawdown_percent', 0),
                                'data_source': signal_data['metadata']['data_source'],
                                'colors_analyzed': signal_data['metadata']['colors_analyzed'],
                                'optimal_bet_fraction': signal_data['optimal_bet_fraction']
                            }
                        )
                        self.repo.save(db_signal)
                        logger.info(f"[OK] Sinal {signal_data['game_id']} salvo no banco de dados")
                    # Enviar ao Telegram com mensagens formatadas
                    self.bot_manager.send_signals(signals)
                    self.stats['signals_sent'] += len(signals)
                else:
                    logger.info("[*] Nenhum sinal com confiança suficiente gerado (0/6 estratégias)")

                # *** NOVO: Armazenar dados brutos coletados como resultados de jogos ***
                # Isso permite análise histórica e correlação com sinais
                try:
                    # Processar dados de Double como resultados
                    if double_data:
                        self.game_result_tracker.process_raw_data_as_results(double_data, 'Double')
                    
                    # Processar dados de Crash como resultados
                    if crash_data:
                        self.game_result_tracker.process_raw_data_as_results(crash_data, 'Crash')
                    
                    logger.info(f"[OK] Dados de jogos armazenados para análise histórica")
                except Exception as e:
                    logger.warning(f"[AVISO] Erro ao armazenar resultados: {str(e)}")

                # Salva dados em cache (passando os arrays originais)
                self.data_collector.save_cache(double_data, crash_data)
                self.stats['colors_collected'] += len(raw_data['crash']) + len(raw_data['double'])
            else:
                logger.warning("[!] Nenhum dado coletado para analise")

            # Salvar estatísticas
            self._save_statistics()

            logger.info("[OK] Ciclo de analise concluido com sucesso")

        except Exception as e:
            logger.error(f"[ERRO] Erro no ciclo de analise: {str(e)}")
            import traceback
            traceback.print_exc()

    def generate_signals_with_pipeline(self, analysis_results, raw_data):
        """
        Gera sinais usando o novo Pipeline com 6 Estratégias + FASE 2 Otimizações
        
        O pipeline processa através de:
        1. Pattern Detection
        2. Technical Validation
        3. Confidence Filter
        4. Confirmation Filter
        5. Monte Carlo Validation
        6. Run Test Validation
        
        FASE 2 (Otimizações):
        7. Meta-Learning (seleciona melhores estratégias por contexto)
        8. Signal Pruner (filtra sinais ineficientes)
        9. Optimal Sequencer (otimiza tamanho da aposta)
        """
        signals = []
        
        try:
            # Preparar dados históricos
            all_colors = self._extract_all_colors(raw_data)
            recent_colors = all_colors[-10:] if len(all_colors) >= 10 else all_colors
            
            if not all_colors or len(all_colors) < 20:
                logger.warning(f"[!] Histórico insuficiente ({len(all_colors)} cores)")
                return signals
            
            # Normalizar resultados para processamento: criar lista de resultados por jogo
            results_to_process = []
            if isinstance(analysis_results, dict):
                if 'crash' in analysis_results and isinstance(analysis_results['crash'], dict):
                    r = analysis_results['crash']
                    r.setdefault('game', 'Crash')
                    results_to_process.append(r)
                if 'double' in analysis_results and isinstance(analysis_results['double'], dict):
                    r = analysis_results['double']
                    r.setdefault('game', 'Double')
                    results_to_process.append(r)
            else:
                # Se já for uma lista, usar diretamente
                results_to_process = list(analysis_results)

            # Processar análise através do pipeline
            for result in results_to_process:
                signal_data = {
                    'all_colors': all_colors,
                    'recent_colors': recent_colors,
                    'observed_count': result.get('desequilibrio', 0) if isinstance(result, dict) else 0,
                    'initial_confidence': result.get('confidence', 0.72) if isinstance(result, dict) else 0.72
                }
                
                # Processar através de 6 estratégias
                signal = self.pipeline.process_signal(signal_data)
                self.stats['signals_processed'] += 1
                
                if signal.is_valid:
                    self.stats['signals_valid'] += 1
                    
                    # FASE 2: Aplicar otimizações
                    optimized_signal = self._apply_fase2_optimizations(signal, result, raw_data)
                    
                    if optimized_signal is not None:
                        signals.append(self._format_signal_for_telegram(optimized_signal, result))
                        
                        logger.info(f"SINAL VÁLIDO: {optimized_signal.signal_type}")
                        logger.info(f"   Confiança final: {optimized_signal.final_confidence:.1%}")
                        logger.info(f"   Estratégias passadas: {optimized_signal.strategies_passed}/6")
                        logger.info(f"   Tamanho ótimo: {optimized_signal.optimal_bet_fraction:.1%} do bankroll")
                    else:
                        logger.debug(f"Sinal rejeitado pela filtragem FASE 2 (Signal Pruner)")
                else:
                    logger.debug(f"Sinal rejeitado (estratégias passadas: {signal.strategies_passed}/6)")

            # Se estivermos em modo de teste forçado, e nenhum sinal válido foi gerado,
            # fabricar um sinal de teste com confiança alta para forçar envio ao Telegram.
            if self.test_mode and not signals:
                logger.info("[TEST-MODE] Gerando sinal de teste forçado para validação Telegram")
                test_result = {
                    'desequilibrio': 5,
                    'confidence': 0.95,
                    'game': 'Test'
                }
                test_signal_data = {
                    'signal_id': 'test-forced-1',
                    'signal_type': 'Vermelho',
                    'recent_colors': recent_colors,
                    'all_colors': all_colors,
                    'prices': [],
                    'initial_confidence': 0.90,
                    'timestamp': datetime.now()
                }
                test_signal = self.pipeline.process_signal(test_signal_data)
                test_signal.finalize(required_strategies=1)
                if test_signal.is_valid:
                    signals.append(self._format_signal_for_telegram(test_signal, test_result))
                    self.stats['signals_valid'] += 1
                    logger.info(f"[TEST-MODE] Sinal de teste válido gerado: {test_signal.signal_type} ({test_signal.final_confidence:.1%})")
            
            return signals
            
        except Exception as e:
            logger.error(f"[ERRO] Erro ao gerar sinais com pipeline: {str(e)}")
            import traceback
            traceback.print_exc()
            return signals
    
    def _apply_fase2_optimizations(self, signal, result, raw_data):
        """
        Aplica otimizações FASE 2:
        1. Meta-Learner: Seleciona estratégias ótimas por contexto
        2. Signal Pruner: Filtra sinais ineficientes
        3. Optimal Sequencer: Calcula tamanho ótimo de aposta
        """
        try:
            from datetime import datetime
            
            # 1. META-LEARNING: Predizer pesos das estratégias por contexto
            current_hour = datetime.now().hour
            current_day = datetime.now().weekday()
            
            # Extrair contexto do sinal
            meta_context = MetaContext(
                timestamp=datetime.now(),
                hour_of_day=current_hour,
                day_of_week=current_day,
                pattern_id=1,  # Simplificado - poderia vir do analysis_results
                game_type='Double' if result.get('game') == 'Double' else 'Crash',
                recent_wr=self._calculate_recent_win_rate(),
                recent_drawdown=self.drawdown.get_status().get('drawdown_percent', 0),
                bankroll_pct=100  # Simplificado
            )
            
            # Predizer pesos usando meta-learner
            strategy_weights = self.meta_learner.predict_strategy_weights(meta_context)
            
            logger.debug(f"   Meta-Learning: Pesos das estratégias = {strategy_weights}")
            
            # 2. SIGNAL PRUNING: Verificar se sinal é economicamente viável
            pruning_result = self.signal_pruner.prune_signal(
                signal_id=signal.signal_type,
                confidence=signal.final_confidence,
                game=result.get('game', 'Double'),
                recent_performance=self._calculate_recent_win_rate()
            )
            
            if pruning_result.should_prune:
                logger.debug(f"   Signal Pruner: Sinal rejeitado (lower_bound={pruning_result.lower_bound:.1%}, min={self.signal_pruner.min_threshold:.1%})")
                return None
            
            logger.debug(f"   Signal Pruner: Sinal aprovado (lower_bound={pruning_result.lower_bound:.1%}, bet_adjustment={pruning_result.bet_adjustment:.1%})")
            
            # 3. OPTIMAL SEQUENCER: Calcular tamanho ótimo de aposta
            bankroll_pct = 100.0  # Simplificado - seria calculado do atual vs inicial
            optimal_bet = self.optimal_sequencer.get_optimal_bet(
                confidence=signal.final_confidence,
                bankroll_percentage=bankroll_pct,
                hour_of_day=current_hour
            )
            
            logger.debug(f"   Optimal Sequencer: Tamanho ótimo = {optimal_bet:.1%} do bankroll")
            
            # Adicionar informações FASE 2 ao sinal
            signal.optimal_bet_fraction = optimal_bet
            signal.strategy_weights = strategy_weights
            signal.pruning_result = pruning_result
            signal.meta_context = meta_context
            
            return signal
            
        except Exception as e:
            logger.warning(f"[AVISO] Erro na aplicação de otimizações FASE 2: {str(e)}")
            import traceback
            traceback.print_exc()
            # Retornar sinal original sem otimizações FASE 2
            signal.optimal_bet_fraction = 0.25  # Default Kelly
            return signal
    
    def _extract_all_colors(self, raw_data):
        """Extrai todas as cores do histórico"""
        colors = []
        
        # Extrair cores do crash (Blaze)
        if 'crash' in raw_data and not raw_data['crash'].empty:
            crash_colors = raw_data['crash'].get('color', [])
            colors.extend([str(c).lower() for c in crash_colors])
        
        # Extrair cores do double (Blaze)
        if 'double' in raw_data and not raw_data['double'].empty:
            double_colors = raw_data['double'].get('color', [])
            colors.extend([str(c).lower() for c in double_colors])
        
        return colors
    
    def _format_signal_for_telegram(self, signal, original_result):
        """Formata sinal do pipeline para envio via Telegram"""
        # Determinar jogo (Double ou Crash)
        game = original_result.get('game', 'Double') if isinstance(original_result, dict) else 'Double'
        
        return {
            'game': game,
            'signal': signal.signal_type,
            'message': f"Sinal: {signal.signal_type} | Confianca: {signal.final_confidence:.1%} | Estrategias: {signal.strategies_passed}/6",
            'type': signal.signal_type,
            'confidence': signal.final_confidence,
            'timestamp': datetime.now(),
            'strategies_passed': signal.strategies_passed,
            'original_confidence': original_result.get('confidence', 0.72) if isinstance(original_result, dict) else 0.72,
            'details': {
                'pipeline_results': {
                    name: {
                        'result': result.value,
                        'confidence': conf
                    }
                    for name, (result, conf) in signal.strategy_results.items()
                }
            }
        }
    
    def _calculate_recent_win_rate(self):
        """Calcula taxa de vitória recente baseada no histórico"""
        if not self.kelly.history:
            return 0.5  # Default conservador
        
        # Usar últimas 50+ apostas se disponíveis
        recent = self.kelly.history[-50:] if len(self.kelly.history) >= 50 else self.kelly.history
        wins = sum(1 for h in recent if h.get('result') == 'WIN')
        
        win_rate = wins / len(recent) if recent else 0.5
        return max(0.3, min(0.7, win_rate))  # Clamp entre 30-70%
    
    def _collect_training_data_for_meta_learner(self, signal, winning_strategy_ids):
        """
        Coleta dados de treinamento para o Meta-Learner
        Deve ser chamado após obter resultado do jogo
        """
        try:
            from datetime import datetime
            
            if not hasattr(signal, 'meta_context') or signal.meta_context is None:
                return  # Sinal não tem contexto meta-learning
            
            # Adicionar amostra de treinamento
            self.meta_learner.add_training_sample(
                context=signal.meta_context,
                winning_strategies=winning_strategy_ids
            )
            
            logger.debug(f"[Meta-Learning] Amostra de treinamento coletada (total: {self.meta_learner.training_sample_count})")
            
            # Verificar se deve retrainer
            if self.meta_learner.should_retrain():
                logger.info("[Meta-Learning] Acionando retreinamento do modelo...")
                self.meta_learner.train()
                logger.info("[Meta-Learning] Modelo retreinado com sucesso!")
                
        except Exception as e:
            logger.warning(f"[AVISO] Erro ao coletar dados para meta-learner: {str(e)}")
    
    def process_game_result_feedback(self, signal, game_result):
        """
        FASE 3: Processa resultado do jogo com Feedback Loop
        
        Auto-ajusta parâmetros baseado em performance real
        
        Args:
            signal: Sinal original que gerou a aposta
            game_result: Resultado do jogo (WIN/LOSS)
        """
        try:
            from datetime import datetime
            
            # Validar inputs
            if not signal or not hasattr(game_result, 'result'):
                return
            
            # Criar SignalResult para o feedback loop
            signal_result = SignalResult(
                signal_id=signal.signal_id if hasattr(signal, 'signal_id') else str(uuid.uuid4()),
                signal_type=str(signal.signal_type) if hasattr(signal, 'signal_type') else 'Unknown',
                game_type=str(signal.game_type) if hasattr(signal, 'game_type') else 'Double',
                confidence=signal.confidence if hasattr(signal, 'confidence') else 0.65,
                bet_size=signal.bet_size if hasattr(signal, 'bet_size') else 10.0,
                odds=1.9,  # Default para Double
                timestamp=datetime.now(),
                result=game_result.result,  # 'WIN' ou 'LOSS'
                payout=game_result.payout if hasattr(game_result, 'payout') else (19.0 if game_result.result == 'WIN' else -100.0),
                context_hour=datetime.now().hour,
                context_day=datetime.now().weekday(),
                strategy_used=signal.strategy_id if hasattr(signal, 'strategy_id') else 'Unknown',
                expected_wr=0.65,  # Padrão
                actual_wr_24h=0.65  # Será atualizado pelo sistema
            )
            
            # Registrar resultado no feedback loop
            self.feedback_loop.record_result(signal_result)
            
            logger.debug(f"[Feedback] Resultado registrado: {signal_result.signal_id} → {signal_result.result}")
            
            # Analisar e fazer ajustes automáticos
            adjustments = self.feedback_loop.analyze_and_adjust()
            
            if adjustments:
                logger.info(f"[Feedback-ADJ] {len(adjustments)} parâmetros ajustados automaticamente")
                
                # Aplicar ajustes ao sistema
                for adj in adjustments:
                    if adj.parameter == 'min_confidence':
                        # Atualizar threshold mínimo de confiança
                        self.pipeline.min_confidence_threshold = adj.new_value
                        logger.info(f"[Feedback] min_confidence: {adj.old_value:.3f} → {adj.new_value:.3f}")
                    
                    elif adj.parameter == 'kelly_fraction':
                        # Atualizar kelly fraction
                        self.kelly.kelly_fraction = adj.new_value
                        logger.info(f"[Feedback] kelly_fraction: {adj.old_value:.3f} → {adj.new_value:.3f}")
            
            # Exportar métricas para monitoramento
            metrics = self.feedback_loop.export_metrics()
            
            if metrics['total_adjustments'] % 5 == 0:  # Log a cada 5 ajustes
                logger.info(f"[Feedback-Status] WR: {metrics['win_rate']}, "
                          f"ROI: {metrics['roi']}, "
                          f"Total Ajustes: {metrics['total_adjustments']}")
            
        except Exception as e:
            logger.warning(f"[AVISO] Erro ao processar feedback: {str(e)}")
    
    def _save_statistics(self):
        """Salva estatísticas de análise"""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        
        stats_data = {
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': elapsed,
            'signals_processed': self.stats['signals_processed'],
            'signals_valid': self.stats['signals_valid'],
            'signals_sent': self.stats['signals_sent'],
            'colors_collected': self.stats['colors_collected'],
            'valid_rate': f"{self.stats['signals_valid']/max(self.stats['signals_processed'], 1)*100:.1f}%"
        }
        
        # Salvar em arquivo de log
        try:
            os.makedirs('logs', exist_ok=True)
            with open('logs/pipeline_stats.json', 'a') as f:
                json.dump(stats_data, f)
                f.write('\n')
        except Exception as e:
            logger.warning(f"[!] Não foi possível salvar estatísticas: {e}")

    def start_scheduled_analysis(self, interval_minutes=None):
        """Inicia análise agendada com coleta contínua de dados"""
        import schedule

        # Forçar intervalo de 2 minutos
        if interval_minutes is None:
            interval_minutes = 2

        schedule.every(interval_minutes).minutes.do(self.run_analysis_cycle)

        logger.info(f"[*] Analise agendada iniciada - Intervalo: {interval_minutes} minutos")
        logger.info(f"[*] Pipeline com 6 estratégias ativo")
        logger.info(f"[*] Coleta contínua de dados iniciada...")

        # Executa imediatamente o primeiro ciclo
        self.run_analysis_cycle()

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("[*] Analise agendada interrompida pelo usuario")
            self._print_final_statistics()
        except Exception as e:
            logger.error(f"[ERRO] Erro no agendador: {str(e)}")
            time.sleep(60)

    def _print_final_statistics(self):
        """Exibe estatísticas finais da sessão"""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        hours = elapsed / 3600
        
        logger.info("\n" + "="*80)
        logger.info("ESTATÍSTICAS FINAIS DA SESSÃO")
        logger.info("="*80)
        logger.info(f"Tempo decorrido: {hours:.2f} horas")
        logger.info(f"Sinais processados: {self.stats['signals_processed']}")
        logger.info(f"Sinais válidos: {self.stats['signals_valid']} ({self.stats['signals_valid']/max(self.stats['signals_processed'], 1)*100:.1f}%)")
        logger.info(f"Sinais enviados: {self.stats['signals_sent']}")
        logger.info(f"Cores coletadas: {self.stats['colors_collected']}")
        logger.info(f"Sinais/hora: {self.stats['signals_processed']/max(hours, 0.01):.1f}")
        logger.info("="*80 + "\n")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Plataforma de Análise de Apostas com Pipeline de 6 Estratégias')
    parser.add_argument('--scheduled', action='store_true',
                       help='Executa em modo agendado com coleta contínua')
    parser.add_argument('--interval', type=int, default=2,
                       help='Intervalo em minutos para análise agendada (padrão: 2)')
    parser.add_argument('--collect-only', action='store_true',
                       help='Apenas coleta dados sem enviar sinais')

    args = parser.parse_args()

    platform = BetAnalysisPlatform()

    if args.scheduled or args.collect_only:
        logger.info("\n" + "="*80)
        logger.info("MODO DE COLETA CONTÍNUA INICIADO")
        logger.info("Pipeline com 6 Estratégias (incluindo Monte Carlo + Run Test)")
        logger.info("="*80)
        logger.info("Pressione CTRL+C para parar e exibir estatísticas\n")
        platform.start_scheduled_analysis(args.interval)
    else:
        logger.info("\n" + "="*80)
        logger.info("ANÁLISE SIMPLES (UMA VEZ)")
        logger.info("Pipeline com 6 Estratégias")
        logger.info("="*80 + "\n")
        platform.run_analysis_cycle()

if __name__ == "__main__":
    main()