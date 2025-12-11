#!/usr/bin/env python3
"""
Script de Análise Rápida - Histórico de Jogos
Analisa dados coletados e gera insights para otimização de estratégias
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Adiciona o diretório src ao path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_dir)

from database import GameResultRepository, init_db
from analysis.game_result_tracker import GameResultTracker
from collections import Counter
import statistics

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('analysis.quick_analysis')


def print_section(title):
    """Imprime seção formatada"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def analyze_game_results(game: str, hours: int = 24):
    """Analisa resultados de um jogo"""
    
    # Inicializar
    Session = init_db()
    repo = GameResultRepository(Session)
    tracker = GameResultTracker(repo)
    
    print_section(f"ANÁLISE DE {game} - Últimas {hours}h")
    
    # 1. Métricas gerais
    metrics = tracker.get_performance_metrics(game, hours)
    
    print(f"📊 MÉTRICAS GERAIS")
    print(f"  Total de sinais com resultado: {metrics['total_signals']}")
    print(f"  Vitórias: {metrics['wins']}")
    print(f"  Derrotas: {metrics['losses']}")
    print(f"  Taxa de acerto: {metrics['win_rate']:.1%}")
    print(f"  Odds médio: {metrics['avg_odds']:.2f}x")
    
    # 2. Resultados por tipo
    results = repo.get_results_by_timeframe(game, hours)
    
    if results:
        print(f"\n🎯 DISTRIBUIÇÃO DE RESULTADOS")
        
        if game == 'Double':
            colors = [r['result'] for r in results]
            color_dist = Counter(colors)
            total = len(colors)
            
            for color, count in color_dist.most_common():
                pct = (count / total) * 100
                print(f"  {color}: {count} ({pct:.1f}%)")
        
        else:  # Crash
            prices = [r['price'] for r in results if r['price']]
            
            if prices:
                print(f"  Multiplicadores coletados: {len(prices)}")
                print(f"  Mínimo: {min(prices):.2f}x")
                print(f"  Máximo: {max(prices):.2f}x")
                print(f"  Média: {statistics.mean(prices):.2f}x")
                
                if len(prices) > 1:
                    print(f"  StdDev: {statistics.stdev(prices):.2f}x")
    
    # 3. Padrões por hora
    print(f"\n⏰ DISTRIBUIÇÃO POR HORA")
    
    by_hour = {}
    for result in results:
        hour = result['timestamp'].hour
        if hour not in by_hour:
            by_hour[hour] = {'total': 0, 'wins': 0}
        by_hour[hour]['total'] += 1
        if result.get('signal_matched'):
            by_hour[hour]['wins'] += 1
    
    for hour in sorted(by_hour.keys()):
        data = by_hour[hour]
        win_rate = (data['wins'] / data['total']) if data['total'] > 0 else 0
        print(f"  {hour:02d}:00 - {data['total']} jogos, {win_rate:.1%} acerto ({data['wins']}/{data['total']})")
    
    # 4. Correlação com sinais
    print(f"\n🔗 CORRELAÇÃO COM SINAIS")
    
    with_signal = sum(1 for r in results if r.get('signal_id'))
    without_signal = len(results) - with_signal
    
    print(f"  Com sinal gerado: {with_signal}")
    print(f"  Sem sinal: {without_signal}")
    
    if with_signal > 0:
        signal_wins = sum(1 for r in results if r.get('signal_matched'))
        print(f"  Sinais que acertaram: {signal_wins}/{with_signal} ({signal_wins/with_signal:.1%})")


def analyze_strategy_effectiveness():
    """Analisa efetividade das estratégias"""
    
    Session = init_db()
    repo = GameResultRepository(Session)
    
    print_section("ANÁLISE DE ESTRATÉGIAS")
    
    # Comparar Double vs Crash
    print("Comparação Double vs Crash (24h):\n")
    
    double_metrics = repo.get_win_rate_by_game('Double', 24)
    crash_metrics = repo.get_win_rate_by_game('Crash', 24)
    
    print(f"📊 DOUBLE")
    print(f"  Win Rate: {double_metrics.get('win_rate', 0):.1%}")
    print(f"  Sinais: {double_metrics.get('total', 0)}")
    print(f"  Vitórias: {double_metrics.get('wins', 0)}")
    
    print(f"\n📊 CRASH")
    print(f"  Win Rate: {crash_metrics.get('win_rate', 0):.1%}")
    print(f"  Sinais: {crash_metrics.get('total', 0)}")
    print(f"  Vitórias: {crash_metrics.get('wins', 0)}")
    
    # Recomendação
    print("\n💡 INSIGHTS:")
    
    double_wr = double_metrics.get('win_rate', 0)
    crash_wr = crash_metrics.get('win_rate', 0)
    
    if double_wr > crash_wr:
        print(f"  ✓ Double está com melhor taxa ({double_wr:.1%} vs {crash_wr:.1%})")
        print(f"  ✓ Aumentar confiança em sinais de Double")
        print(f"  ✓ Revisar estratégia de Crash")
    elif crash_wr > double_wr:
        print(f"  ✓ Crash está com melhor taxa ({crash_wr:.1%} vs {double_wr:.1%})")
        print(f"  ✓ Aumentar confiança em sinais de Crash")
        print(f"  ✓ Revisar estratégia de Double")
    else:
        print(f"  ✓ Taxa de acerto igual ({double_wr:.1%})")


def get_data_summary():
    """Resumo dos dados coletados"""
    
    Session = init_db()
    repo = GameResultRepository(Session)
    
    print_section("RESUMO DE DADOS COLETADOS")
    
    # Total de registros
    all_results = repo.get_all(limit=100000)
    
    if all_results:
        print(f"✓ Total de registros: {len(all_results)}")
        
        # Distribuição por jogo
        games = Counter([r['game'] for r in all_results])
        print(f"\nDistribuição por jogo:")
        for game, count in games.most_common():
            print(f"  {game}: {count}")
        
        # Distribuição por resultado
        if all_results:
            results_list = [r['result'] for r in all_results if 'result' in r]
            result_dist = Counter(results_list)
            print(f"\nDistribuição de resultados:")
            for result, count in result_dist.most_common():
                pct = (count / len(all_results)) * 100
                print(f"  {result}: {count} ({pct:.1f}%)")
        
        # Período coletado
        if all_results and 'timestamp' in all_results[0]:
            timestamps = [r['timestamp'] for r in all_results if 'timestamp' in r]
            if timestamps:
                min_time = min(timestamps)
                max_time = max(timestamps)
                duration = max_time - min_time
                
                print(f"\nPeríodo de coleta:")
                print(f"  De: {min_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Até: {max_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Duração: {duration}")
    else:
        print("❌ Nenhum dado coletado ainda!")


def main():
    """Função principal"""
    
    print("\n" + "="*80)
    print("  ANÁLISE RÁPIDA - SISTEMA DE SINAIS")
    print("  " + datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
    print("="*80)
    
    try:
        # 1. Resumo geral
        get_data_summary()
        
        # 2. Análise por jogo
        analyze_game_results('Double', hours=24)
        analyze_game_results('Crash', hours=24)
        
        # 3. Análise de estratégias
        analyze_strategy_effectiveness()
        
        print("\n" + "="*80)
        print("  ANÁLISE CONCLUÍDA")
        print("="*80 + "\n")
        
    except Exception as e:
        logger.error(f"Erro na análise: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
