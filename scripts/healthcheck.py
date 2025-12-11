#!/usr/bin/env python3
"""Healthcheck script for docker-compose.
Checks that logs/bet_analysis.log exists and was modified recently.
Exit 0 if healthy, non-zero otherwise.
"""
import os
import sys
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--max-age', type=int, default=120, help='Max allowed age of log file in seconds')
args = parser.parse_args()

log_path = os.path.join('logs', 'bet_analysis.log')

if not os.path.exists(log_path):
    print(f'UNHEALTHY: {log_path} not found')
    sys.exit(2)

mtime = os.path.getmtime(log_path)
age = time.time() - mtime
if age <= args.max_age:
    print(f'HEALTHY: {log_path} age={age:.1f}s')
    sys.exit(0)
else:
    print(f'UNHEALTHY: {log_path} age={age:.1f}s > {args.max_age}s')
    sys.exit(1)
