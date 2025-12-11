import os
import json
from datetime import datetime

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
LOGS = os.path.join(BASE, 'logs')
PIPELINE_STATS = os.path.join(LOGS, 'pipeline_stats.json')
MODO_LOG = os.path.join(LOGS, 'modo_24_7.log')

OUT_DIR = os.path.join(BASE, 'outputs', datetime.now().strftime('run_%Y%m%d_%H%M%S'))
os.makedirs(OUT_DIR, exist_ok=True)

summary = {
    'collected_at': datetime.now().isoformat(),
    'pipeline_stats_lines': 0,
    'last_stats': None,
    'cycles': 0,
    'signals_sent_final': 0,
    'signals_processed_final': 0,
    'colors_collected_final': 0,
    'notes': []
}

# Copy pipeline_stats.json if exists and parse
if os.path.exists(PIPELINE_STATS):
    try:
        with open(PIPELINE_STATS, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        summary['pipeline_stats_lines'] = len(lines)
        if lines:
            last = json.loads(lines[-1])
            summary['last_stats'] = last
            summary['cycles'] = None
            # Prefer explicit fields if present
            summary['signals_sent_final'] = last.get('signals_sent', 0)
            summary['signals_processed_final'] = last.get('signals_processed', 0)
            summary['colors_collected_final'] = last.get('colors_collected', 0)
        # copy file to outputs
        import shutil
        shutil.copy2(PIPELINE_STATS, os.path.join(OUT_DIR, 'pipeline_stats.json'))
    except Exception as e:
        summary['notes'].append(f'Erro lendo pipeline_stats.json: {e}')
else:
    summary['notes'].append('pipeline_stats.json nao encontrado')

# Copy last part of modo_24_7.log
if os.path.exists(MODO_LOG):
    try:
        with open(MODO_LOG, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        tail = lines[-400:] if len(lines) > 400 else lines
        with open(os.path.join(OUT_DIR, 'modo_24_7_tail.log'), 'w', encoding='utf-8') as out:
            out.writelines(tail)
        summary['notes'].append('modo_24_7.log copiado (parte final)')
    except Exception as e:
        summary['notes'].append(f'Erro lendo modo_24_7.log: {e}')
else:
    summary['notes'].append('modo_24_7.log nao encontrado')

# Save summary
with open(os.path.join(OUT_DIR, 'summary.json'), 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

# Print concise summary to stdout for the caller
print('--- RUN RESULTS SUMMARY ---')
print(f"Collected at: {summary['collected_at']}")
print(f"Pipeline stats lines: {summary['pipeline_stats_lines']}")
if summary['last_stats']:
    ls = summary['last_stats']
    print(f"Signals sent (final): {summary['signals_sent_final']}")
    print(f"Signals processed (final): {summary['signals_processed_final']}")
    print(f"Colors collected (final): {summary['colors_collected_final']}")
else:
    print('No pipeline stats available')

print('\nFiles saved to:')
print(OUT_DIR)
print('\nContents:')
for fn in os.listdir(OUT_DIR):
    print(' -', fn)

print('\nDetailed notes:')
for n in summary['notes']:
    print(' -', n)

print('\nDone.')
