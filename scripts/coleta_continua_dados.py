"""
Sistema de Coleta Contínua de Dados para Análise em Tempo Real

Este módulo coleta dados continuamente por 2+ dias para:
1. Acumular 1000+ registros de cores
2. Melhorar a qualidade estatística
3. Validar padrões com Monte Carlo + Run Test
4. Treinar o pipeline com dados reais

Uso:
    python scripts/coleta_continua_dados.py --duration 48h --interval 5m
"""

import logging
import argparse
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import sys
import os

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection.blaze_client import BlazeDataCollector
from src.analysis.strategy_pipeline import StrategyPipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/coleta_continua.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ColetorDadosContinuo:
    """Coleta dados continuamente em tempo real"""
    
    def __init__(self, output_file='data/coleta_continua.json'):
        """
        Inicializa o coletor
        
        Args:
            output_file: Arquivo para salvar dados coletados
        """
        self.output_file = output_file
        self.data_collector = BlazeDataCollector()
        self.pipeline = StrategyPipeline(logger)
        
        # Estatísticas
        self.stats = {
            'colors_collected': 0,
            'signals_processed': 0,
            'signals_valid': 0,
            'start_time': datetime.now(),
            'last_colors': []
        }
        
        # Garantir que o diretório existe
        os.makedirs(Path(output_file).parent, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
    
    def coletar_um_ciclo(self):
        """Executa um ciclo de coleta de dados"""
        try:
            logger.info("[*] Coletando dados...")
            raw_data = self.data_collector.collect_recent_data()
            
            if raw_data and (not raw_data.get('crash', {}).empty or not raw_data.get('double', {}).empty):
                # Extrair cores
                colors = []
                
                if 'crash' in raw_data and not raw_data['crash'].empty:
                    crash_colors = raw_data['crash'].get('color', [])
                    colors.extend([str(c).lower() for c in crash_colors])
                
                if 'double' in raw_data and not raw_data['double'].empty:
                    double_colors = raw_data['double'].get('color', [])
                    colors.extend([str(c).lower() for c in double_colors])
                
                if colors:
                    # Adicionar à coleção
                    self.stats['last_colors'].extend(colors)
                    self.stats['colors_collected'] += len(colors)
                    
                    # Manter apenas últimas 1000 cores em memória
                    if len(self.stats['last_colors']) > 1000:
                        self.stats['last_colors'] = self.stats['last_colors'][-1000:]
                    
                    # Processar através do pipeline
                    self._processar_com_pipeline()
                    
                    # Salvar dados
                    self._salvar_dados(colors)
                    
                    logger.info(f"✅ Coletadas {len(colors)} cores | Total: {self.stats['colors_collected']}")
                else:
                    logger.warning("[!] Nenhuma cor extraída dos dados")
            else:
                logger.debug("[*] Dados insuficientes para processar")
        
        except Exception as e:
            logger.error(f"[ERRO] Erro ao coletar dados: {e}")
            import traceback
            traceback.print_exc()
    
    def _processar_com_pipeline(self):
        """Processa cores coletadas através do pipeline"""
        if len(self.stats['last_colors']) < 10:
            return  # Precisa de histórico mínimo
        
        try:
            # Preparar dados
            all_colors = self.stats['last_colors']
            recent_colors = all_colors[-10:]
            
            # Verificar desequilíbrio
            red_count = sum(1 for c in recent_colors if 'vermelho' in c or 'red' in c)
            black_count = len(recent_colors) - red_count
            
            if red_count > black_count:
                signal_data = {
                    'all_colors': all_colors,
                    'recent_colors': recent_colors,
                    'observed_count': red_count,
                    'initial_confidence': 0.72
                }
                expected_color = 'vermelho'
            else:
                signal_data = {
                    'all_colors': all_colors,
                    'recent_colors': recent_colors,
                    'observed_count': black_count,
                    'initial_confidence': 0.72
                }
                expected_color = 'preto'
            
            # Processar
            signal = self.pipeline.process_signal(signal_data)
            self.stats['signals_processed'] += 1
            
            if signal.is_valid:
                self.stats['signals_valid'] += 1
                logger.info(f"✅ SINAL VÁLIDO: {signal.signal_type} ({signal.final_confidence:.1%})")
                logger.info(f"   Estratégias: {signal.strategies_passed}/6")
        
        except Exception as e:
            logger.error(f"[ERRO] Erro ao processar pipeline: {e}")
    
    def _salvar_dados(self, colors):
        """Salva dados coletados em arquivo JSON"""
        try:
            data_entry = {
                'timestamp': datetime.now().isoformat(),
                'colors': colors,
                'count': len(colors),
                'total_collected': self.stats['colors_collected'],
                'signals_processed': self.stats['signals_processed'],
                'signals_valid': self.stats['signals_valid']
            }
            
            # Append ao arquivo JSON (um por linha)
            with open(self.output_file, 'a') as f:
                json.dump(data_entry, f)
                f.write('\n')
        
        except Exception as e:
            logger.error(f"[ERRO] Erro ao salvar dados: {e}")
    
    def exibir_estatisticas(self):
        """Exibe estatísticas de coleta"""
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        hours = elapsed / 3600
        
        logger.info("\n" + "="*80)
        logger.info("ESTATÍSTICAS DE COLETA CONTÍNUA")
        logger.info("="*80)
        logger.info(f"Tempo decorrido: {hours:.2f} horas ({int(elapsed/60)} minutos)")
        logger.info(f"Cores coletadas: {self.stats['colors_collected']}")
        logger.info(f"Cores/hora: {self.stats['colors_collected']/max(hours, 0.01):.1f}")
        logger.info(f"")
        logger.info(f"Sinais processados: {self.stats['signals_processed']}")
        logger.info(f"Sinais válidos: {self.stats['signals_valid']} ({self.stats['signals_valid']/max(self.stats['signals_processed'], 1)*100:.1f}%)")
        logger.info(f"Sinais/hora: {self.stats['signals_processed']/max(hours, 0.01):.1f}")
        logger.info(f"")
        logger.info(f"Arquivo: {self.output_file}")
        logger.info("="*80 + "\n")
    
    def coletar_por_duracao(self, duracao_horas=2, intervalo_segundos=30):
        """
        Coleta dados continuamente por um período específico
        
        Args:
            duracao_horas: Duração da coleta em horas (padrão: 2)
            intervalo_segundos: Intervalo entre coletas em segundos (padrão: 30)
        """
        tempo_fim = datetime.now() + timedelta(hours=duracao_horas)
        
        logger.info("\n" + "="*80)
        logger.info("COLETA CONTÍNUA DE DADOS INICIADA")
        logger.info("="*80)
        logger.info(f"Duração: {duracao_horas} horas")
        logger.info(f"Intervalo: {intervalo_segundos} segundos")
        logger.info(f"Tempo fim: {tempo_fim.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Pipeline: 6 estratégias (Monte Carlo + Run Test inclusos)")
        logger.info("Pressione CTRL+C para parar\n")
        logger.info("="*80 + "\n")
        
        try:
            while datetime.now() < tempo_fim:
                tempo_restante = tempo_fim - datetime.now()
                horas_restantes = tempo_restante.total_seconds() / 3600
                
                # Exibir progresso
                logger.info(f"[▶] Tempo restante: {horas_restantes:.2f}h | Total: {self.stats['colors_collected']} cores")
                
                # Coletar
                self.coletar_um_ciclo()
                
                # Aguardar
                time.sleep(intervalo_segundos)
        
        except KeyboardInterrupt:
            logger.info("\n[*] Coleta interrompida pelo usuário")
        
        finally:
            self.exibir_estatisticas()
    
    def coletar_infinito(self, intervalo_segundos=30):
        """
        Coleta dados continuamente sem limite de tempo
        
        Args:
            intervalo_segundos: Intervalo entre coletas
        """
        logger.info("\n" + "="*80)
        logger.info("COLETA CONTÍNUA DE DADOS - MODO INFINITO")
        logger.info("="*80)
        logger.info(f"Intervalo: {intervalo_segundos} segundos")
        logger.info("Pipeline: 6 estratégias (Monte Carlo + Run Test inclusos)")
        logger.info("Pressione CTRL+C para parar\n")
        logger.info("="*80 + "\n")
        
        try:
            while True:
                logger.info(f"[▶] Total: {self.stats['colors_collected']} cores | Sinais válidos: {self.stats['signals_valid']}")
                
                # Coletar
                self.coletar_um_ciclo()
                
                # Aguardar
                time.sleep(intervalo_segundos)
        
        except KeyboardInterrupt:
            logger.info("\n[*] Coleta interrompida pelo usuário")
        
        finally:
            self.exibir_estatisticas()


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description='Coleta contínua de dados para análise em tempo real'
    )
    parser.add_argument(
        '--duration',
        type=float,
        default=48,
        help='Duração da coleta em horas (padrão: 48)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Intervalo entre coletas em segundos (padrão: 30)'
    )
    parser.add_argument(
        '--infinite',
        action='store_true',
        help='Coleta infinitamente sem limite de tempo'
    )
    parser.add_argument(
        '--output',
        default='data/coleta_continua.json',
        help='Arquivo de saída (padrão: data/coleta_continua.json)'
    )
    
    args = parser.parse_args()
    
    # Criar coletor
    coletor = ColetorDadosContinuo(output_file=args.output)
    
    # Iniciar coleta
    if args.infinite:
        coletor.coletar_infinito(intervalo_segundos=args.interval)
    else:
        coletor.coletar_por_duracao(
            duracao_horas=args.duration,
            intervalo_segundos=args.interval
        )


if __name__ == "__main__":
    main()
