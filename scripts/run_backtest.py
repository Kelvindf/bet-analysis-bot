#!/usr/bin/env python3
"""
Script para executar backtest da estratégia de análise

Uso:
    python scripts/run_backtest.py
    python scripts/run_backtest.py --win-rate 0.60
    python scripts/run_backtest.py --start-date 2025-01-01 --end-date 2025-12-31
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import argparse

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analysis.backtester import Backtester


def main():
    """Executa backtest completo"""
    
    parser = argparse.ArgumentParser(
        description='Backtest da estratégia de análise'
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
        default=None,
        help='Taxa de vitória esperada (0.0-1.0), padrão 0.55'
    )
    parser.add_argument(
        '--stake',
        type=float,
        default=10.0,
        help='Valor da aposta por trade (padrão R$ 10)'
    )
    parser.add_argument(
        '--csv',
        action='store_true',
        help='Salvar resultados em CSV'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(" "*20 + "BACKTEST FRAMEWORK v1.0")
    print("="*70)
    
    # Validar datas
    start_date = args.start_date
    end_date = args.end_date
    
    if start_date:
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            print(f"[!] Data inicial inválida: {start_date}")
            return 1
    
    if end_date:
        try:
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            print(f"[!] Data final inválida: {end_date}")
            return 1
    
    # Criar backtester
    backtester = Backtester(
        data_path='data/raw/',
        stake=args.stake
    )
    
    # Executar backtest
    print("\n[*] Iniciando backtest...")
    print(f"    Data inicial: {start_date or 'Todas'}")
    print(f"    Data final: {end_date or 'Todas'}")
    print(f"    Stake/Trade: R$ {args.stake}")
    if args.win_rate:
        print(f"    Win Rate: {args.win_rate:.1%}")
    print()
    
    try:
        results = backtester.run_backtest(
            start_date=start_date,
            end_date=end_date,
            win_rate=args.win_rate
        )
        
        # Gerar e exibir relatório
        report = backtester.generate_report()
        print(report)
        
        # Salvar em JSON
        json_path = Path('data') / 'backtest_results.json'
        json_path.parent.mkdir(exist_ok=True)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'parameters': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'stake': args.stake,
                    'win_rate': args.win_rate or 0.55
                },
                'results': results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"[OK] Resultados salvos em {json_path}\n")
        
        # Salvar trades em CSV se solicitado
        if args.csv:
            csv_path = backtester.save_trades_to_csv()
            if csv_path:
                print(f"[OK] Detalhes de trades em {csv_path}\n")
        
        # Retornar status baseado em ROI
        roi = float(results.get('roi_pct', '0').rstrip('%'))
        if roi > 5:
            print("[OK] ✅ Backtest passou - Estratégia viável\n")
            return 0
        else:
            print("[!] ⚠️  Backtest falhou - Estratégia precisa otimização\n")
            return 1
    
    except Exception as e:
        print(f"[!] Erro durante backtest: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main())
