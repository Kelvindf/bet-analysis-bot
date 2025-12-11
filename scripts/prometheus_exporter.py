#!/usr/bin/env python3
"""Simple Prometheus exporter that reads logs/pipeline_metrics.csv and exposes metrics.
Run this sidecar or in the same container.
Includes Kelly Criterion and Drawdown Manager metrics (Tier 1).
"""
import time
import os
import csv
import json
from prometheus_client import start_http_server, Gauge

CSV_PATH = os.path.join('logs', 'pipeline_metrics.csv')
KELLY_PATH = os.path.join('logs', 'kelly_stats.json')
DRAWDOWN_PATH = os.path.join('logs', 'drawdown_state.json')

# Pipeline Gauges
g_cycles = Gauge('pipeline_cycles_total', 'Total cycles observed')
g_signals_processed = Gauge('signals_processed_total', 'Total signals processed')
g_signals_valid = Gauge('signals_valid_total', 'Total signals considered valid')
g_signals_sent = Gauge('signals_sent_total', 'Total signals sent')
g_avg_confidence = Gauge('signals_avg_confidence', 'Average final confidence')

# Kelly Criterion Gauges (NEW - Tier 1)
g_kelly_bankroll = Gauge('kelly_bankroll_usd', 'Current bankroll (Kelly Criterion)')
g_kelly_roi = Gauge('kelly_roi_percent', 'Return on Investment % (Kelly Criterion)')
g_kelly_win_rate = Gauge('kelly_win_rate_percent', 'Win Rate % (Kelly Criterion)')
g_kelly_total_bets = Gauge('kelly_total_bets', 'Total bets placed (Kelly Criterion)')
g_kelly_total_wins = Gauge('kelly_total_wins', 'Total wins (Kelly Criterion)')
g_kelly_total_losses = Gauge('kelly_total_losses', 'Total losses (Kelly Criterion)')

# Drawdown Manager Gauges (NEW - Tier 1)
g_drawdown_percent = Gauge('drawdown_percent', 'Current drawdown % (Drawdown Manager)')
g_drawdown_is_paused = Gauge('drawdown_is_paused', 'Trading paused due to drawdown (1=yes, 0=no)')
g_drawdown_pause_events = Gauge('drawdown_pause_events_total', 'Total pause events (Drawdown Manager)')
g_drawdown_peak_bankroll = Gauge('drawdown_peak_bankroll_usd', 'Peak bankroll high water mark')


def read_csv_and_update():
    """Read pipeline metrics from CSV."""
    if not os.path.exists(CSV_PATH):
        return
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
            cycles = len(rows)
            proc = sum(int(r.get('signals_processed') or 0) for r in rows)
            valid = sum(int(r.get('signals_valid') or 0) for r in rows)
            sent = sum(int(r.get('signals_sent') or 0) for r in rows)
            confidences = [float(r.get('avg_final_confidence') or r.get('avg_confidence') or 0) for r in rows if (r.get('avg_final_confidence') or r.get('avg_confidence'))]
            avg_conf = sum(confidences)/len(confidences) if confidences else 0.0

            g_cycles.set(cycles)
            g_signals_processed.set(proc)
            g_signals_valid.set(valid)
            g_signals_sent.set(sent)
            g_avg_confidence.set(avg_conf)
    except Exception:
        pass


def read_kelly_and_update():
    """Read Kelly Criterion metrics from JSON."""
    if not os.path.exists(KELLY_PATH):
        return
    try:
        with open(KELLY_PATH, 'r', encoding='utf-8') as fh:
            kelly_data = json.load(fh)
            stats = kelly_data.get('stats', {})
            
            g_kelly_bankroll.set(float(stats.get('current_bankroll', 0)))
            g_kelly_roi.set(float(stats.get('roi_percent', 0)))
            g_kelly_win_rate.set(float(stats.get('win_rate', 0)) * 100)
            g_kelly_total_bets.set(int(stats.get('total_bets', 0)))
            g_kelly_total_wins.set(int(stats.get('total_wins', 0)))
            g_kelly_total_losses.set(int(stats.get('total_losses', 0)))
    except Exception:
        pass


def read_drawdown_and_update():
    """Read Drawdown Manager metrics from JSON."""
    if not os.path.exists(DRAWDOWN_PATH):
        return
    try:
        with open(DRAWDOWN_PATH, 'r', encoding='utf-8') as fh:
            dd_data = json.load(fh)
            
            g_drawdown_percent.set(float(dd_data.get('drawdown_percent', 0)))
            g_drawdown_is_paused.set(1 if dd_data.get('is_paused', False) else 0)
            g_drawdown_pause_events.set(len(dd_data.get('pause_history', [])))
            g_drawdown_peak_bankroll.set(float(dd_data.get('peak_bankroll', 0)))
    except Exception:
        pass


def main():
    start_http_server(8000)
    print('Prometheus exporter listening on :8000')
    print('📊 Metrics available:')
    print('   Pipeline:  pipeline_cycles_total, signals_processed_total, signals_valid_total, signals_sent_total, signals_avg_confidence')
    print('   Kelly:     kelly_bankroll_usd, kelly_roi_percent, kelly_win_rate_percent, kelly_total_bets, kelly_total_wins, kelly_total_losses')
    print('   Drawdown:  drawdown_percent, drawdown_is_paused, drawdown_pause_events_total, drawdown_peak_bankroll_usd')
    print('🔗 Access at: http://localhost:8000/metrics')
    while True:
        read_csv_and_update()
        read_kelly_and_update()
        read_drawdown_and_update()
        time.sleep(5)

if __name__ == '__main__':
    main()
