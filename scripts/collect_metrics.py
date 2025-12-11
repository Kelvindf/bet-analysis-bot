#!/usr/bin/env python3
"""
Roda a plataforma em modo teste por um tempo limitado e coleta métricas por ciclo.

Uso: python scripts/collect_metrics.py --seconds 60

Gera: logs/pipeline_metrics.csv
"""
import argparse
import time
import csv
import os
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

# Tenta importar BetAnalysisPlatform de várias localizações comuns de forma dinâmica.
def _load_bet_analysis_platform():
    import importlib
    import importlib.util

    candidates = ['main', 'bet_analysis_platform.main', 'src.main']
    for name in candidates:
        try:
            module = importlib.import_module(name)
            if hasattr(module, 'BetAnalysisPlatform'):
                return getattr(module, 'BetAnalysisPlatform')
        except Exception:
            # Ignora falhas e tenta o próximo candidato
            continue

    # Tenta carregar diretamente do arquivo src/main.py (por segurança)
    main_path = Path(__file__).resolve().parents[1] / 'src' / 'main.py'
    if main_path.exists():
        spec = importlib.util.spec_from_file_location("bet_analysis_main", str(main_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        try:
            return getattr(module, 'BetAnalysisPlatform')
        except AttributeError:
            raise ImportError(
                "Arquivo 'main.py' encontrado, mas não contém 'BetAnalysisPlatform'."
            )

    raise ImportError(
        "Não foi possível resolver a importação 'main'. "
        "Verifique se 'main.py' existe dentro de 'src' ou ajuste o sys.path."
    )

BetAnalysisPlatform = _load_bet_analysis_platform()


def run_collection(duration_seconds: int = 60, interval_seconds: int = 5):
    os.makedirs('logs', exist_ok=True)
    csv_path = os.path.join('logs', 'pipeline_metrics.csv')
    header = ['timestamp', 'cycle', 'total_records', 'signals_processed', 'signals_valid', 'signals_sent', 'avg_final_confidence', 'avg_strategies_passed']

    platform = BetAnalysisPlatform(test_mode=True)

    start = time.time()
    cycle = 0

    # Cria arquivo CSV se não existir
    if not os.path.exists(csv_path):
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)

    while time.time() - start < duration_seconds:
        cycle += 1
        t0 = time.time()
        platform.run_analysis_cycle()

        # Coletar métricas do objeto platform.stats
        stats = platform.stats
        total_records = stats.get('colors_collected', 0)
        sp = stats.get('signals_processed', 0)
        sv = stats.get('signals_valid', 0)
        ss = stats.get('signals_sent', 0)

        # Estimar avg_final_confidence e avg_strategies_passed lendo pipeline_stats.json ou usando 0
        avg_conf = 0.0
        avg_spassed = 0.0
        try:
            import json
            with open('logs/pipeline_stats.json', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last = json.loads(lines[-1])
                    # Não temos avg_conf no arquivo atual - usar 0
                    avg_conf = last.get('avg_confidence_valid', 0)
        except Exception:
            pass

        with open(csv_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                cycle,
                total_records,
                sp,
                sv,
                ss,
                avg_conf,
                avg_spassed
            ])

        # Aguardar intervalo mínimo entre ciclos
        elapsed = time.time() - t0
        sleep_for = max(0, interval_seconds - elapsed)
        time.sleep(sleep_for)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--seconds', type=int, default=60, help='Duração em segundos (default 60)')
    parser.add_argument('--interval', type=int, default=5, help='Intervalo entre ciclos em segundos (default 5)')
    args = parser.parse_args()

    print(f"Iniciando coleta por {args.seconds}s (intervalo {args.interval}s)...")
    run_collection(duration_seconds=args.seconds, interval_seconds=args.interval)
    print("Coleta finalizada. Arquivo: logs/pipeline_metrics.csv")


if __name__ == '__main__':
    main()
