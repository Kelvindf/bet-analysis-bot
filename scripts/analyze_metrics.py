import os
import json
import csv
from collections import Counter

csv_path = os.path.join('logs', 'pipeline_metrics.csv')
json_path = os.path.join('logs', 'pipeline_stats.json')

def analyze_csv(path):
    if not os.path.exists(path):
        print(f'CSV not found: {path}')
        return None
    try:
        import pandas as pd
        df = pd.read_csv(path)
        summary = {}
        summary['cycles'] = len(df)
        for col in ['signals_processed', 'signals_valid', 'signals_sent']:
            if col in df.columns:
                summary[col] = int(df[col].sum())
        if 'avg_confidence' in df.columns:
            summary['avg_confidence'] = float(df['avg_confidence'].mean())
        return summary
    except Exception as e:
        # fallback csv parsing
        with open(path, 'r', newline='', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
            if not rows:
                return {'cycles': 0}
            summary = {'cycles': len(rows)}
            for col in ['signals_processed', 'signals_valid', 'signals_sent']:
                summary[col] = sum(int(r.get(col,0) or 0) for r in rows)
            # try avg_confidence
            confidences = [float(r.get('avg_confidence')) for r in rows if r.get('avg_confidence')]
            if confidences:
                summary['avg_confidence'] = sum(confidences)/len(confidences)
            return summary

def analyze_jsonl(path):
    if not os.path.exists(path):
        print(f'JSONL not found: {path}')
        return None
    stats = []
    strategies_counter = Counter()
    try:
        with open(path, 'r', encoding='utf-8') as fh:
            for line in fh:
                line=line.strip()
                if not line:
                    continue
                try:
                    j = json.loads(line)
                except Exception:
                    continue
                stats.append(j)
                sp = j.get('strategies_passed') or j.get('strategies')
                if isinstance(sp, int):
                    strategies_counter[str(sp)] += 1
                elif isinstance(sp, list):
                    strategies_counter.update([str(len(sp))])
        return {'entries': len(stats), 'strategies_distribution': dict(strategies_counter)}
    except Exception as e:
        print('Erro ao ler JSONL:', e)
        return None

if __name__ == '__main__':
    print('Analisando métricas...')
    csv_summary = analyze_csv(csv_path)
    json_summary = analyze_jsonl(json_path)
    print('\nCSV resumo:')
    print(csv_summary)
    print('\nJSONL resumo:')
    print(json_summary)
    print('\nRecomendações rápidas:')
    if csv_summary:
        cycles = csv_summary.get('cycles',0)
        sent = csv_summary.get('signals_sent',0)
        valid = csv_summary.get('signals_valid',0)
        proc = csv_summary.get('signals_processed',0)
        if proc>0:
            print(f' - Taxa envio/gerados: {sent}/{proc} = {sent/proc:.2%}')
        if valid>0:
            print(f' - Taxa válidos/gerados: {valid}/{proc} = {valid/proc:.2%}')
        if 'avg_confidence' in csv_summary:
            print(f" - Confiança média dos sinais válidos: {csv_summary['avg_confidence']:.1f}%")
    if json_summary:
        print(' - Distribuição strategies_passed (por número de strategies):')
        for k,v in sorted(json_summary.get('strategies_distribution',{}).items(), key=lambda x: int(x[0])):
            print(f'    {k} strategies: {v} cycles')
    print('\nFim da análise.')
