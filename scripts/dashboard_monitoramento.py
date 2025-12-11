"""
Dashboard de Monitoramento em Tempo Real

Exibe estatísticas ao vivo durante a coleta de dados e análise.
Mostra: sinais/hora, ROI atual, taxa de acerto, confiança média.
"""

import logging
import json
import time
from datetime import datetime
from pathlib import Path
import sys
import os
from collections import deque

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DashboardMonitoramento:
    """Dashboard de monitoramento em tempo real"""
    
    def __init__(self, log_file='logs/coleta_continua.log', stats_file='logs/pipeline_stats.json'):
        self.log_file = log_file
        self.stats_file = stats_file
        self.stats_history = deque(maxlen=1000)  # Últimas 1000 entradas
        self.last_position = 0
    
    def carregar_arquivo_stats(self):
        """Carrega estatísticas do arquivo"""
        stats = []
        try:
            if Path(self.stats_file).exists():
                with open(self.stats_file, 'r') as f:
                    for line in f:
                        try:
                            stats.append(json.loads(line))
                        except:
                            pass
        except Exception as e:
            logger.error(f"Erro ao carregar stats: {e}")
        return stats
    
    def exibir_dashboard(self, intervalo=10):
        """Exibe dashboard continuamente"""
        logger.info("\n" + "="*100)
        logger.info("DASHBOARD DE MONITORAMENTO EM TEMPO REAL")
        logger.info("="*100)
        logger.info("Atualizando a cada {} segundos... (Pressione CTRL+C para sair)\n".format(intervalo))
        
        try:
            while True:
                self._limpar_tela()
                self._exibir_cabecalho()
                self._exibir_metricas()
                time.sleep(intervalo)
        except KeyboardInterrupt:
            logger.info("\n[*] Dashboard interrompido")
    
    def _limpar_tela(self):
        """Limpa a tela do terminal"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _exibir_cabecalho(self):
        """Exibe cabeçalho do dashboard"""
        print("\n" + "="*100)
        print("MONITORAMENTO EM TEMPO REAL - Pipeline com 6 Estratégias (Monte Carlo + Run Test)")
        print("="*100)
        print(f"Atualizado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    def _exibir_metricas(self):
        """Exibe métricas do monitoramento"""
        stats = self.carregar_arquivo_stats()
        
        if not stats:
            print("[!] Nenhum dado disponível ainda. Aguardando primeiro ciclo...\n")
            return
        
        # Última entrada
        ultima = stats[-1]
        
        print("📊 MÉTRICAS GERAIS")
        print("-" * 100)
        print(f"  Tempo decorrido: {ultima['elapsed_seconds']/3600:.2f} horas ({int(ultima['elapsed_seconds']/60)} minutos)")
        print(f"  Cores coletadas: {ultima['colors_collected']}")
        print(f"  Taxa de coleta: {ultima['colors_collected']/(ultima['elapsed_seconds']/3600):.1f} cores/hora\n")
        
        print("🎯 SINAIS E ESTRATÉGIA")
        print("-" * 100)
        print(f"  Sinais processados: {ultima['signals_processed']}")
        print(f"  Sinais válidos: {ultima['signals_valid']} ({ultima.get('valid_rate', '0%')})")
        print(f"  Taxa de processamento: {ultima['signals_processed']/(ultima['elapsed_seconds']/3600):.1f} sinais/hora")
        print(f"  Sinais válidos/hora: {ultima['signals_valid']/(max(ultima['elapsed_seconds']/3600, 0.01)):.1f}\n")
        
        # Estatísticas adicionais
        if len(stats) > 1:
            print("📈 TENDÊNCIAS (últimas 10 coletas)")
            print("-" * 100)
            ultimas_10 = list(stats[-10:])
            
            # Calcular taxa média de sinais válidos
            total_processados = sum(s['signals_processed'] for s in ultimas_10)
            total_validos = sum(s['signals_valid'] for s in ultimas_10)
            
            if total_processados > 0:
                taxa_acerto = (total_validos / total_processados) * 100
                print(f"  Taxa de acerto média: {taxa_acerto:.1f}%")
                print(f"  Sinais válidos em últimas 10: {total_validos}/{total_processados}\n")
        
        print("✅ RECOMENDAÇÕES")
        print("-" * 100)
        
        if ultima['colors_collected'] < 500:
            print(f"  • Continuar coleta: {ultima['colors_collected']}/1000 cores (50%)")
            remaining_cores = 1000 - ultima['colors_collected']
            hours_at_current_rate = remaining_cores / max(ultima['colors_collected']/(ultima['elapsed_seconds']/3600), 0.01)
            print(f"  • Tempo estimado para 1000 cores: {hours_at_current_rate:.1f} horas")
        elif ultima['colors_collected'] < 1000:
            print(f"  • Coleta quase completa: {ultima['colors_collected']}/1000 cores (90%)")
            remaining_cores = 1000 - ultima['colors_collected']
            hours_at_current_rate = remaining_cores / max(ultima['colors_collected']/(ultima['elapsed_seconds']/3600), 0.01)
            print(f"  • Tempo estimado para 1000 cores: {hours_at_current_rate:.1f} horas")
        else:
            print(f"  • ✅ Meta atingida: {ultima['colors_collected']}/1000 cores")
            print(f"  • Backtest agora será mais preciso com {ultima['colors_collected']} amostras")
            print(f"  • Execute novo backtest para validar ROI: 4-5% esperado")
        
        print("\n")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Dashboard de monitoramento em tempo real'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='Intervalo de atualização em segundos (padrão: 10)'
    )
    parser.add_argument(
        '--log-file',
        default='logs/coleta_continua.log',
        help='Arquivo de log (padrão: logs/coleta_continua.log)'
    )
    parser.add_argument(
        '--stats-file',
        default='logs/pipeline_stats.json',
        help='Arquivo de stats (padrão: logs/pipeline_stats.json)'
    )
    
    args = parser.parse_args()
    
    dashboard = DashboardMonitoramento(
        log_file=args.log_file,
        stats_file=args.stats_file
    )
    
    dashboard.exibir_dashboard(intervalo=args.interval)


if __name__ == "__main__":
    main()
