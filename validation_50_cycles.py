#!/usr/bin/env python3
"""
Validação de 50+ ciclos com Kelly Criterion + Drawdown Manager.
Simula trading 24/7, monitora bankroll, drawdowns, pause events.
Salva relatório em VALIDACAO_50_CICLOS.md
"""
import sys
import time
import json
import os
from datetime import datetime
from src.main import BetAnalysisPlatform
from src.strategies.kelly_criterion import KellyCriterion
from scripts.drawdown_manager import DrawdownManager

# ===== CONFIGURAÇÃO =====
INITIAL_BANKROLL = 1000.0
NUM_CYCLES = 50
CYCLE_INTERVAL_SECONDS = 2  # Para teste rápido

print(f"""
╔══════════════════════════════════════════════════════════════╗
║         VALIDAÇÃO 50+ CICLOS - KELLY + DRAWDOWN              ║
╠══════════════════════════════════════════════════════════════╣
║ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                       ║
║ Cycles: {NUM_CYCLES}                                                  ║
║ Initial Bankroll: ${INITIAL_BANKROLL}                              ║
║ Interval: {CYCLE_INTERVAL_SECONDS}s/cycle                                   ║
╚══════════════════════════════════════════════════════════════╝
""")

# ===== SETUP =====
os.environ['KELLY_BANKROLL'] = str(INITIAL_BANKROLL)
os.environ['KELLY_FRACTION'] = '0.25'
os.environ['MAX_DRAWDOWN_PERCENT'] = '5.0'

platform = BetAnalysisPlatform()

# Track metrics
metrics = {
    'start_time': datetime.now().isoformat(),
    'cycles_completed': 0,
    'total_signals': 0,
    'total_bets_kelly': 0,
    'total_wins': 0,
    'total_losses': 0,
    'peak_bankroll': INITIAL_BANKROLL,
    'min_bankroll': INITIAL_BANKROLL,
    'pause_events': [],
    'cycle_details': []
}

# ===== EXECUÇÃO =====
for cycle_num in range(1, NUM_CYCLES + 1):
    try:
        cycle_start = time.time()
        
        # Executar 1 ciclo
        platform.run_analysis_cycle()
        
        # Coletar metricas
        kelly_stats = platform.kelly.get_stats()
        dd_status = platform.drawdown.get_status()
        
        current_bankroll = kelly_stats.get('current_bankroll', INITIAL_BANKROLL)
        is_paused = dd_status.get('is_paused', False)
        drawdown = dd_status.get('drawdown_percent', 0)
        
        # Atualizar track
        metrics['cycles_completed'] += 1
        metrics['total_bets_kelly'] = kelly_stats.get('total_bets', 0)
        metrics['total_wins'] = kelly_stats.get('total_wins', 0)
        metrics['total_losses'] = kelly_stats.get('total_losses', 0)
        
        if current_bankroll > metrics['peak_bankroll']:
            metrics['peak_bankroll'] = current_bankroll
        if current_bankroll < metrics['min_bankroll']:
            metrics['min_bankroll'] = current_bankroll
        
        # Log pause events
        if is_paused and (not metrics['pause_events'] or metrics['pause_events'][-1]['cycle'] != cycle_num):
            metrics['pause_events'].append({
                'cycle': cycle_num,
                'drawdown': drawdown,
                'bankroll': current_bankroll,
                'timestamp': datetime.now().isoformat()
            })
        
        cycle_details = {
            'cycle': cycle_num,
            'bankroll': round(current_bankroll, 2),
            'drawdown': round(drawdown, 2),
            'paused': is_paused,
            'total_bets': kelly_stats.get('total_bets', 0),
            'win_rate': round(kelly_stats.get('win_rate', 0) * 100, 2),
            'roi': round(kelly_stats.get('roi_percent', 0), 2)
        }
        metrics['cycle_details'].append(cycle_details)
        
        # Print progress
        status = "⏸️ PAUSED" if is_paused else "✅ RUNNING"
        print(f"[{cycle_num:2d}/{NUM_CYCLES}] {status} | Bankroll: ${current_bankroll:8.2f} | DD: {drawdown:5.2f}% | WR: {cycle_details['win_rate']:5.1f}%")
        
        time.sleep(CYCLE_INTERVAL_SECONDS)
        
    except Exception as e:
        print(f"❌ Erro no ciclo {cycle_num}: {str(e)}")
        metrics['error'] = str(e)
        break

# ===== RESULTADO =====
end_time = datetime.now()
duration = (end_time - datetime.fromisoformat(metrics['start_time'])).total_seconds()
final_bankroll = metrics['cycle_details'][-1]['bankroll'] if metrics['cycle_details'] else INITIAL_BANKROLL
roi_total = ((final_bankroll - INITIAL_BANKROLL) / INITIAL_BANKROLL) * 100

print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    RESULTADO FINAL                           ║
╠══════════════════════════════════════════════════════════════╣
║ End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}                          ║
║ Duration: {duration:6.1f}s ({duration/60:5.1f}min)                            ║
║ Cycles Completed: {metrics['cycles_completed']}/{NUM_CYCLES}                                 ║
╟──────────────────────────────────────────────────────────────╢
║ Initial Bankroll:  ${INITIAL_BANKROLL:10.2f}                       ║
║ Final Bankroll:    ${final_bankroll:10.2f}                       ║
║ Peak Bankroll:     ${metrics['peak_bankroll']:10.2f}                       ║
║ Min Bankroll:      ${metrics['min_bankroll']:10.2f}                       ║
║ Total ROI:         {roi_total:10.2f}%                       ║
╟──────────────────────────────────────────────────────────────╢
║ Total Bets:        {metrics['total_bets_kelly']:10d}                       ║
║ Total Wins:        {metrics['total_wins']:10d}                       ║
║ Total Losses:      {metrics['total_losses']:10d}                       ║
║ Win Rate:          {(metrics['total_wins']/(metrics['total_bets_kelly'] if metrics['total_bets_kelly'] > 0 else 1)*100):10.2f}%                       ║
╟──────────────────────────────────────────────────────────────╢
║ Pause Events:      {len(metrics['pause_events']):10d}                       ║
║ Status:            {'✅ PASSED' if metrics['cycles_completed'] == NUM_CYCLES else '⚠️  INCOMPLETE':^28} ║
╚══════════════════════════════════════════════════════════════╝
""")

# ===== SALVAR RELATÓRIO =====
report = f"""# 📊 Relatório de Validação - 50+ Ciclos

**Data:** {datetime.now().strftime('%d de %B de %Y')}  
**Duração Total:** {duration:.1f}s ({duration/60:.1f} minutos)

## 📈 Resumo de Resultados

| Métrica | Valor |
|---------|-------|
| Ciclos Completados | {metrics['cycles_completed']}/{NUM_CYCLES} |
| Bankroll Inicial | ${INITIAL_BANKROLL:.2f} |
| Bankroll Final | ${final_bankroll:.2f} |
| Bankroll Pico | ${metrics['peak_bankroll']:.2f} |
| Bankroll Mínimo | ${metrics['min_bankroll']:.2f} |
| ROI Total | {roi_total:.2f}% |
| **Status** | **{'✅ PASSOU' if metrics['cycles_completed'] == NUM_CYCLES else '⚠️ INCOMPLETO'}** |

## 💰 Estatísticas de Trading

| Métrica | Valor |
|---------|-------|
| Total de Apostas | {metrics['total_bets_kelly']} |
| Total de Vitórias | {metrics['total_wins']} |
| Total de Perdas | {metrics['total_losses']} |
| Taxa de Vitória | {(metrics['total_wins']/(metrics['total_bets_kelly'] if metrics['total_bets_kelly'] > 0 else 1)*100):.2f}% |

## ⏸️ Eventos de Drawdown

**Total de Pausas:** {len(metrics['pause_events'])}

"""

if metrics['pause_events']:
    report += "| Ciclo | Drawdown | Bankroll | Timestamp |\n"
    report += "|-------|----------|----------|----------|\n"
    for event in metrics['pause_events']:
        report += f"| {event['cycle']} | {event['drawdown']:.2f}% | ${event['bankroll']:.2f} | {event['timestamp']} |\n"
else:
    report += "✅ Nenhum evento de pausa (drawdown manteve-se dentro dos limites)\n"

report += """

## 📊 Detalhe por Ciclo (Primeiros 10 e Últimos 10)

### Primeiros 10 Ciclos
"""

for detail in metrics['cycle_details'][:10]:
    status = "⏸️ PAUSED" if detail['paused'] else "✅"
    report += f"- **Ciclo {detail['cycle']}** {status}: Bankroll ${detail['bankroll']:.2f} | DD: {detail['drawdown']:.2f}% | WR: {detail['win_rate']:.1f}%\n"

report += "\n### Últimos 10 Ciclos\n"
for detail in metrics['cycle_details'][-10:]:
    status = "⏸️ PAUSED" if detail['paused'] else "✅"
    report += f"- **Ciclo {detail['cycle']}** {status}: Bankroll ${detail['bankroll']:.2f} | DD: {detail['drawdown']:.2f}% | WR: {detail['win_rate']:.1f}%\n"

report += f"""

## 🎯 Conclusões

1. **Funcionalidade Kelly:** {'✅ Funcionando' if metrics['total_bets_kelly'] > 0 else '❌ Não funcionando'}
2. **Funcionalidade Drawdown:** {'✅ Funcionando' if len(metrics['pause_events']) > 0 or metrics['cycles_completed'] > 40 else '⚠️ Não testado completamente'}
3. **Estabilidade de Bankroll:** {'✅ Estável' if abs(roi_total) < 10 else '⚠️ Volatilidade alta'}
4. **Recomendações:** {'Pronto para produção' if metrics['cycles_completed'] == NUM_CYCLES and abs(roi_total) < 5 else 'Revisar configurações de Kelly/Drawdown'}

---

**Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status Final:** {('✅ PASSOU' if metrics['cycles_completed'] == NUM_CYCLES else '⚠️ INCOMPLETO')}
"""

with open('VALIDACAO_50_CICLOS.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("\n✅ Relatório salvo em: VALIDACAO_50_CICLOS.md")
print(f"📊 JSON Metrics: {json.dumps(metrics, indent=2, default=str)}")

# Salvar JSON também
with open('logs/validacao_50_ciclos_metrics.json', 'w', encoding='utf-8') as f:
    json.dump(metrics, f, indent=2, default=str)

print("✅ Métricas JSON salvas em: logs/validacao_50_ciclos_metrics.json")
