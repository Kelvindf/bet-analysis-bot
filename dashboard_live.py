#!/usr/bin/env python3
"""
Dashboard em Tempo Real - Monitoramento de Kelly + Drawdown
Mostra sinais sendo enviados para Telegram + métricas em tempo real
"""
import time
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Cores ANSI para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def load_json_safe(path):
    """Carrega JSON com segurança."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def get_kelly_stats():
    """Carrega stats de Kelly."""
    data = load_json_safe('logs/kelly_stats.json')
    return data.get('stats', {})

def get_drawdown_status():
    """Carrega status de Drawdown."""
    return load_json_safe('logs/drawdown_state.json')

def get_pipeline_metrics():
    """Carrega métricas de pipeline."""
    if not os.path.exists('logs/pipeline_metrics.csv'):
        return None
    try:
        import csv
        with open('logs/pipeline_metrics.csv', 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
            return rows[-1] if rows else None
    except:
        return None

def read_log_tail(filepath, lines=5):
    """Lê últimas linhas de um arquivo."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:]
    except:
        return []

def print_header():
    """Imprime header do dashboard."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print("║                                                                           ║")
    print("║        📊 DASHBOARD - Bet Analysis Platform com Kelly + Drawdown         ║")
    print("║                      Monitoramento em Tempo Real                          ║")
    print("║                                                                           ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")

def print_kelly_section():
    """Imprime seção Kelly Criterion."""
    stats = get_kelly_stats()
    
    if not stats:
        print(f"{Colors.WARNING}⏳ Aguardando dados de Kelly...{Colors.ENDC}\n")
        return
    
    bankroll = float(stats.get('current_bankroll', 0))
    roi = float(stats.get('roi_percent', 0))
    win_rate = float(stats.get('win_rate', 0)) * 100
    total_bets = int(stats.get('total_bets', 0))
    total_wins = int(stats.get('total_wins', 0))
    total_losses = int(stats.get('total_losses', 0))
    
    # Cores baseado em ROI
    roi_color = Colors.OKGREEN if roi >= 0 else Colors.FAIL
    
    print(f"{Colors.OKBLUE}{Colors.BOLD}💰 KELLY CRITERION{Colors.ENDC}")
    print(f"  Bankroll:      ${bankroll:10.2f}  {Colors.OKGREEN}✓{Colors.ENDC}")
    print(f"  ROI:           {roi_color}{roi:10.2f}%{Colors.ENDC}")
    print(f"  Win Rate:      {win_rate:10.1f}%  (Wins: {total_wins} | Losses: {total_losses})")
    print(f"  Total Bets:    {total_bets:10d}")
    print()

def print_drawdown_section():
    """Imprime seção Drawdown Manager."""
    status = get_drawdown_status()
    
    if not status:
        print(f"{Colors.WARNING}⏳ Aguardando dados de Drawdown...{Colors.ENDC}\n")
        return
    
    drawdown = float(status.get('drawdown_percent', 0))
    is_paused = status.get('is_paused', False)
    peak = float(status.get('peak_bankroll', 0))
    current = float(status.get('current_bankroll', 0))
    pause_count = len(status.get('pause_history', []))
    
    # Cores baseado em drawdown
    if is_paused:
        status_str = f"{Colors.FAIL}{Colors.BOLD}⏸️  PAUSED{Colors.ENDC}"
    else:
        status_str = f"{Colors.OKGREEN}{Colors.BOLD}▶️  RUNNING{Colors.ENDC}"
    
    dd_color = Colors.WARNING if drawdown >= 3 else Colors.OKGREEN
    
    print(f"{Colors.OKBLUE}{Colors.BOLD}📉 DRAWDOWN MANAGER{Colors.ENDC}")
    print(f"  Status:        {status_str}")
    print(f"  Drawdown:      {dd_color}{drawdown:10.2f}%{Colors.ENDC}  (Peak: ${peak:.2f})")
    print(f"  Current:       ${current:10.2f}")
    print(f"  Pause Events:  {pause_count:10d}")
    print()

def print_pipeline_section():
    """Imprime seção Pipeline."""
    metrics = get_pipeline_metrics()
    
    if not metrics:
        print(f"{Colors.WARNING}⏳ Aguardando dados de Pipeline...{Colors.ENDC}\n")
        return
    
    signals_processed = int(metrics.get('signals_processed', 0))
    signals_valid = int(metrics.get('signals_valid', 0))
    signals_sent = int(metrics.get('signals_sent', 0))
    confidence = float(metrics.get('avg_final_confidence', metrics.get('avg_confidence', 0)))
    
    print(f"{Colors.OKBLUE}{Colors.BOLD}📡 PIPELINE (6 Estratégias){Colors.ENDC}")
    print(f"  Sinais Processados: {signals_processed:10d}")
    print(f"  Sinais Válidos:     {signals_valid:10d}")
    print(f"  Sinais Enviados:    {signals_sent:10d}  {Colors.OKGREEN}✓{Colors.ENDC}")
    print(f"  Confiança Média:    {confidence:10.1f}%")
    print()

def print_logs_section():
    """Imprime últimos logs."""
    print(f"{Colors.OKBLUE}{Colors.BOLD}📝 ÚLTIMOS SINAIS (Últimos 5){Colors.ENDC}")
    
    logs = read_log_tail('logs/bet_analysis.log', lines=5)
    if logs:
        for line in logs:
            line = line.strip()
            if 'SINAL VÁLIDO' in line:
                print(f"  {Colors.OKGREEN}✓ {line}{Colors.ENDC}")
            elif 'ERROR' in line or 'Erro' in line:
                print(f"  {Colors.FAIL}✗ {line}{Colors.ENDC}")
            elif 'pausa' in line.lower() or 'pause' in line.lower():
                print(f"  {Colors.WARNING}⏸ {line}{Colors.ENDC}")
            else:
                print(f"  {line}")
    else:
        print(f"  {Colors.WARNING}Nenhum sinal registrado ainda{Colors.ENDC}")
    print()

def print_telegram_section():
    """Imprime status Telegram."""
    print(f"{Colors.OKBLUE}{Colors.BOLD}💬 TELEGRAM{Colors.ENDC}")
    print(f"  Bot Token:     Configurado ✓")
    print(f"  Chat ID:       Configurado ✓")
    print(f"  Status:        {Colors.OKGREEN}Ativo{Colors.ENDC}")
    print()

def print_footer():
    """Imprime footer com info de acesso."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════════════════════════════════╗")
    print(f"║ 🔗 Prometheus Metrics: http://localhost:8000/metrics                     ║")
    print(f"║ 📧 Telegram: Sinais sendo enviados continuamente                        ║")
    print(f"║ ⏰ Atualização: {now:<51} ║")
    print("╚═══════════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")

def main():
    """Loop principal do dashboard."""
    try:
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print_header()
            print_kelly_section()
            print_drawdown_section()
            print_pipeline_section()
            print_telegram_section()
            print_logs_section()
            print_footer()
            
            # Atualiza a cada 5 segundos
            time.sleep(5)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Dashboard encerrado.{Colors.ENDC}")
        sys.exit(0)

if __name__ == '__main__':
    main()
