#!/usr/bin/env python3
"""
Script para executar Backtest Otimizado com Pipeline de Estratégias

Pipeline em cascata:
  Entrada → [Padrão] → [Técnico] → [Confiança] → [Confirmação] → Saída
            (Filtra)   (Valida)   (Rejeita)     (Confirma)       (Válido)

Uso:
    python scripts/run_backtest_optimized.py
    python scripts/run_backtest_optimized.py --win-rate 0.60
    python scripts/run_backtest_optimized.py --margin 0.07 --win-rate 0.58
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import argparse

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.optimized_backtester import OptimizedBacktester


def main():
    """Executa backtest otimizado com pipeline"""
    
    parser = argparse.ArgumentParser(
        description='Backtest Otimizado com Pipeline de Estratégias em Cascata'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        default=None,
        help='Data inicial (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        default=None,
        help='Data final (YYYY-MM-DD)'
    )
    parser.add_argument(
        '--win-rate',
        type=float,
        default=0.55,
        help='Taxa de vitória esperada (padrão 0.55 = 55%)'
    )
    parser.add_argument(
        '--margin',
        type=float,
        default=0.05,
        help='Margem de lucro (padrão 0.05 = 5%)'
    )
    parser.add_argument(
        '--stake',
        type=float,
        default=10.0,
        help='Valor da aposta por trade (padrão R$ 10)'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Comparar com backtest simples (sem pipeline)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(" "*10 + "BACKTEST OTIMIZADO COM PIPELINE DE ESTRATÉGIAS")
    print(" "*15 + "Engrenagens em Cascata")
    print("="*70)
    
    # Criar backtester otimizado
    backtester = OptimizedBacktester(
        data_path='data/raw/',
        stake=args.stake,
        use_pipeline=True
    )
    
    # Executar backtest otimizado
    print("\n[*] Iniciando backtest otimizado...")
    print(f"    Margem: {args.margin*100:.1f}%")
    print(f"    Win Rate: {args.win_rate*100:.1f}%")
    print(f"    Stake: R$ {args.stake}\n")
    
    try:
        results = backtester.run_backtest_optimized(
            start_date=args.start_date,
            end_date=args.end_date,
            win_rate=args.win_rate,
            margin_pct=args.margin
        )
        
        # Gerar e exibir relatório
        report = backtester.generate_report_optimized()
        print(report)
        
        # Salvar em JSON
        json_path = Path('data') / 'backtest_results_optimized.json'
        json_path.parent.mkdir(exist_ok=True)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'pipeline': True,
                'parameters': {
                    'start_date': args.start_date,
                    'end_date': args.end_date,
                    'win_rate': args.win_rate,
                    'margin': args.margin,
                    'stake': args.stake
                },
                'results': results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Resultados salvos em {json_path}\n")
        
        # OPCIONAL: Comparar com backtest simples
        if args.compare:
            print("\n" + "-"*70)
            print("COMPARAÇÃO: Backtest Simples vs Otimizado")
            print("-"*70 + "\n")
            
            # Rodar sem pipeline
            backtester_simple = OptimizedBacktester(
                data_path='data/raw/',
                stake=args.stake,
                use_pipeline=False
            )
            
            print("[*] Executando backtest SIMPLES (sem pipeline)...\n")
            
            from src.analysis.backtester import Backtester
            simple_bt = Backtester(data_path='data/raw/', stake=args.stake)
            simple_bt.load_historical_data(args.start_date, args.end_date)
            simple_signals = simple_bt.simulate_signals()
            simple_bt.execute_trades(simple_signals, win_rate=args.win_rate)
            simple_results = simple_bt.analyze_performance()
            
            print("\n[COMPARAÇÃO DE RESULTADOS]")
            print("─" * 70)
            print(f"{'Métrica':<30} {'SIMPLES':<20} {'OTIMIZADO':<20}")
            print("─" * 70)
            print(f"{'Sinais':<30} {len(simple_signals):<20} {len(backtester.processed_signals):<20}")
            print(f"{'Trades':<30} {simple_results['total_trades']:<20} {results['total_trades']:<20}")
            print(f"{'ROI':<30} {simple_results['roi_pct']:<20} {results['roi_pct']:<20}")
            print(f"{'Profit Factor':<30} {simple_results['profit_factor']:<20} {results['profit_factor']:<20}")
            print(f"{'Lucro Total':<30} {'R$ ' + str(simple_results['total_profit']):<18} {'R$ ' + str(results['total_profit']):<18}")
            print("─" * 70)
            
            # Calcular melhoria
            roi_simple = float(simple_results['roi_pct'].rstrip('%'))
            roi_optimized = float(results['roi_pct'].rstrip('%'))
            melhoria = roi_optimized - roi_simple
            
            print(f"\n✅ MELHORIA COM PIPELINE: {melhoria:+.2f}pp ROI")
            if melhoria > 0:
                print(f"   Pipeline MELHOROU o resultado!")
            else:
                print(f"   Pipeline REDUZIU a qualidade dos sinais")
        
        # Status final
        roi = float(results.get('roi_pct', '0').rstrip('%'))
        if roi > 3:
            print("\n✅ BACKTEST OTIMIZADO PASSOU - Estratégia com pipeline é viável!\n")
            return 0
        elif roi > 0:
            print("\n⚠️  BACKTEST MARGINAL - Resultado positivo mas com pouca margem\n")
            return 1
        else:
            print("\n❌ BACKTEST FALHOU - ROI negativo, precisa mais otimização\n")
            return 2
    
    except Exception as e:
        print(f"[!] Erro durante backtest: {e}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == '__main__':
    sys.exit(main())
