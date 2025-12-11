#!/usr/bin/env python3
"""
MODO 24/7 - Sistema enviando sinais continuamente

Executa coleta de dados e envio de sinais 24 horas por dia, 7 dias por semana.
O sistema roda indefinidamente até ser interrompido manualmente.

Uso:
    python scripts/modo_24_7.py                    # Rodar indefinidamente
    python scripts/modo_24_7.py --duration 48      # Rodar por 48 horas
    python scripts/modo_24_7.py --duration 1       # Rodar por 1 hora (teste)

Status:
    ✅ Coleta contínua de dados
    ✅ Análise a cada N segundos
    ✅ Envio de sinais via Telegram
    ✅ Dashboard monitoramento
    ✅ Recuperação automática de erros
"""

import sys
import os
import time
import logging
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
import schedule

# Adiciona src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import BetAnalysisPlatform
from src.telegram_bot.bot_manager import TelegramBotManager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler('logs/modo_24_7.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Sistema24_7:
    """Sistema de análise 24/7 com coleta contínua"""
    
    def __init__(self):
        load_dotenv()
        self.platform = BetAnalysisPlatform()
        self.bot = TelegramBotManager()
        self.start_time = datetime.now()
        self.execution_hours = 0  # Indefinido até especificar
        self.is_running = True
        
        # Estatísticas
        self.stats = {
            'cycles': 0,
            'signals_total': 0,
            'signals_sent': 0,
            'errors': 0,
            'uptime_hours': 0,
            'last_signal': None,
            'last_error': None
        }
        
        logger.info("="*80)
        logger.info("SISTEMA 24/7 INICIALIZADO")
        logger.info("="*80)
        logger.info(f"Início: {self.start_time}")
        logger.info(f"Status: AGUARDANDO CONFIGURAÇÃO")
        logger.info("="*80)
    
    def set_duration(self, hours):
        """Define quanto tempo o sistema vai rodar"""
        if hours == 0:
            logger.info(f"✅ Sistema configurado para rodar INDEFINIDAMENTE (24/7)")
            logger.info("   Pressione Ctrl+C para parar")
            self.execution_hours = 0
        else:
            logger.info(f"✅ Sistema configurado para rodar por {hours} hora(s)")
            self.execution_hours = hours
            self.end_time = self.start_time + timedelta(hours=hours)
    
    def log_status(self):
        """Mostra status atual do sistema"""
        elapsed = datetime.now() - self.start_time
        hours = elapsed.total_seconds() / 3600
        
        logger.info("\n" + "="*80)
        logger.info("📊 STATUS SISTEMA 24/7")
        logger.info("="*80)
        logger.info(f"Tempo de execução: {int(hours)}h {int((hours % 1) * 60)}m")
        logger.info(f"Ciclos executados: {self.stats['cycles']}")
        logger.info(f"Sinais processados: {self.stats['signals_total']}")
        logger.info(f"Sinais enviados: {self.stats['signals_sent']}")
        logger.info(f"Taxa de conversão: {self.stats['signals_sent']}/{self.stats['signals_total']} = {(self.stats['signals_sent']/max(self.stats['signals_total'],1))*100:.1f}%")
        logger.info(f"Erros: {self.stats['errors']}")
        
        if self.stats['last_signal']:
            logger.info(f"Último sinal: {self.stats['last_signal']}")
        if self.stats['last_error']:
            logger.info(f"Último erro: {self.stats['last_error']}")
        
        if self.execution_hours > 0:
            remaining = self.end_time - datetime.now()
            remaining_hours = remaining.total_seconds() / 3600
            logger.info(f"Tempo restante: {max(0, remaining_hours):.1f} horas")
        
        logger.info("="*80 + "\n")
    
    def cycle_analysis(self):
        """Executa um ciclo de análise e envio de sinais"""
        try:
            self.stats['cycles'] += 1
            
            logger.info(f"\n[CICLO {self.stats['cycles']}] Iniciando análise...")
            
            # Executar ciclo de análise
            self.platform.run_analysis_cycle()
            
            # Atualizar estatísticas (pegando de platform.stats)
            self.stats['signals_total'] = self.platform.stats['signals_processed']
            self.stats['signals_sent'] = self.platform.stats['signals_sent']
            
            logger.info(f"[CICLO {self.stats['cycles']}] ✅ Concluído com sucesso")
            
        except Exception as e:
            self.stats['errors'] += 1
            self.stats['last_error'] = str(e)
            logger.error(f"[CICLO {self.stats['cycles']}] ❌ Erro na análise: {str(e)}")
            
            # Tentar notificar no Telegram
            try:
                self.bot.send_message(f"⚠️ ERRO no sistema 24/7:\n{str(e)}")
            except:
                pass
    
    def check_duration(self):
        """Verifica se atingiu o tempo configurado"""
        if self.execution_hours <= 0:
            return True  # Rodar indefinidamente
        
        elapsed = datetime.now() - self.start_time
        if elapsed >= timedelta(hours=self.execution_hours):
            logger.info(f"\n⏰ Tempo limite atingido ({self.execution_hours}h)")
            return False
        
        return True
    
    def run(self):
        """Executa o sistema em modo contínuo"""
        logger.info("\n" + "="*80)
        logger.info("🚀 INICIANDO SISTEMA 24/7")
        logger.info("="*80 + "\n")
        
        try:
            # Fazer notificação de inicialização
            try:
                uptime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.bot.send_message(f"✅ Sistema 24/7 iniciado\nHora: {uptime}\nPressione Ctrl+C para parar")
            except:
                logger.warning("Não conseguiu enviar notificação ao Telegram")
            
            # Loop principal
            cycle_count = 0
            while self.is_running and self.check_duration():
                try:
                    cycle_count += 1
                    
                    # Executar análise
                    self.cycle_analysis()
                    
                    # Mostrar status a cada 10 ciclos
                    if cycle_count % 10 == 0:
                        self.log_status()
                    
                    # Aguardar antes do próximo ciclo (30 segundos padrão)
                    logger.info(f"Aguardando 30s até próximo ciclo...")
                    time.sleep(30)
                    
                except KeyboardInterrupt:
                    logger.info("\n⏹️  Interrupção do usuário detectada")
                    self.is_running = False
                    break
                except Exception as e:
                    logger.error(f"Erro no loop principal: {str(e)}")
                    self.stats['errors'] += 1
                    time.sleep(5)  # Aguardar antes de retentativa
            
            # Finalização
            self.finalize()
            
        except KeyboardInterrupt:
            logger.info("\n⏹️  Sistema interrompido pelo usuário")
            self.finalize()
        except Exception as e:
            logger.error(f"Erro crítico: {str(e)}")
            self.finalize()
    
    def finalize(self):
        """Finaliza o sistema e envia relatório final"""
        logger.info("\n" + "="*80)
        logger.info("📋 RELATÓRIO FINAL")
        logger.info("="*80)
        
        elapsed = datetime.now() - self.start_time
        hours = elapsed.total_seconds() / 3600
        
        logger.info(f"Tempo total de execução: {int(hours)}h {int((hours % 1) * 60)}m")
        logger.info(f"Total de ciclos: {self.stats['cycles']}")
        logger.info(f"Sinais processados: {self.stats['signals_total']}")
        logger.info(f"Sinais enviados: {self.stats['signals_sent']}")
        logger.info(f"Taxa de conversão: {(self.stats['signals_sent']/max(self.stats['signals_total'],1))*100:.1f}%")
        logger.info(f"Erros encontrados: {self.stats['errors']}")
        
        logger.info("="*80 + "\n")
        
        # Enviar relatório para Telegram
        try:
            relatorio = f"""
📋 SISTEMA 24/7 FINALIZADO

⏱️ Tempo total: {int(hours)}h {int((hours % 1) * 60)}m
🔄 Ciclos: {self.stats['cycles']}
📊 Sinais: {self.stats['signals_sent']}/{self.stats['signals_total']}
📈 Taxa de conversão: {(self.stats['signals_sent']/max(self.stats['signals_total'],1))*100:.1f}%
⚠️ Erros: {self.stats['errors']}

Fim: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            """
            self.bot.send_message(relatorio)
        except:
            logger.warning("Não conseguiu enviar relatório ao Telegram")
        
        logger.info("✅ Sistema finalizado com sucesso")

def main():
    parser = argparse.ArgumentParser(
        description='Sistema 24/7 - Coleta contínua de dados e envio de sinais'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=0,
        help='Duração em horas (0=indefinido/24-7, padrão: 0)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Intervalo entre ciclos em segundos (padrão: 30)'
    )
    parser.add_argument(
        '--test-signals',
        action='store_true',
        help='Modo de teste: força envio de sinais de teste para o Telegram quando não houver sinais reais'
    )
    
    args = parser.parse_args()
    
    # Criar sistema
    sistema = Sistema24_7()
    # Se solicitado, ativar modo de teste que força sinais
    if args.test_signals:
        # Propagar flag para a plataforma interna
        try:
            sistema.platform.test_mode = True
            logger.info("[TEST-MODE] Modo de testes ativado: sinais forçados quando necessário")
        except Exception:
            logger.warning("Não foi possível ativar o modo de teste na plataforma")
    sistema.set_duration(args.duration)
    
    # Executar
    sistema.run()

if __name__ == '__main__':
    main()
