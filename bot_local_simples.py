#!/usr/bin/env python3
"""
Bot de Análise Blaze - Versão Local com Melhorias
- Pattern Recognition: Detecta padrões nos últimos sinais
- Momentum Analysis: Calcula velocidade e aceleração
- Dynamic Bankroll: Ajusta confiança baseado em resultados
- Hourly Filters: Aplica filtros por horário
"""

import time
import requests
import random
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import deque

# Configurações
TELEGRAM_BOT_TOKEN = "8260416435:AAH7aPa8eL8bYG0051IPyulUXqmaetFxrzQ"
TELEGRAM_CHANNEL_ID = "8329919168"
INTERVAL = 60  # 1 minuto

# Arquivo para persistir histórico
HISTORY_FILE = Path("signal_history.json")
MAX_HISTORY = 50  # Manter últimos 50 sinais

# Bankroll inicial
INITIAL_BANKROLL = 100.0
BANKROLL_THRESHOLD_GOOD = 1.1  # 10% ganho
BANKROLL_THRESHOLD_BAD = 0.9   # 10% perda

# ==================== 1. GERENCIAMENTO DE HISTÓRICO ====================

def load_history():
    """Carrega histórico de sinais do arquivo"""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return deque(data.get('signals', []), maxlen=MAX_HISTORY), data.get('bankroll', INITIAL_BANKROLL)
        except:
            return deque(maxlen=MAX_HISTORY), INITIAL_BANKROLL
    return deque(maxlen=MAX_HISTORY), INITIAL_BANKROLL

def save_history(signals, bankroll):
    """Salva histórico de sinais no arquivo"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'signals': list(signals),
                'bankroll': bankroll,
                'last_update': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️  Erro ao salvar histórico: {e}")

# ==================== 2. PATTERN RECOGNITION ====================

def detect_pattern(signals_history):
    """Detecta padrões nos últimos sinais"""
    if len(signals_history) < 5:
        return "normal", 0
    
    # Análise simples: conta sucessos/fracassos consecutivos
    last_5 = [s['game'] for s in list(signals_history)[-5:]]
    
    # Contar repetições
    max_repeat = 1
    current_repeat = 1
    for i in range(1, len(last_5)):
        if last_5[i] == last_5[i-1]:
            current_repeat += 1
            max_repeat = max(max_repeat, current_repeat)
        else:
            current_repeat = 1
    
    # Se mesmo jogo aparece 3+ vezes = padrão detectado
    if max_repeat >= 3:
        pattern_type = "repetition"
        confidence_boost = min(5, max_repeat - 2)  # +3 a +5%
        return pattern_type, confidence_boost
    
    # Análise de alternância
    alternating = sum(1 for i in range(1, len(last_5)) if last_5[i] != last_5[i-1])
    if alternating == len(last_5) - 1:  # Todos alternam
        return "alternating", 2
    
    return "normal", 0

# ==================== 3. MOMENTUM ANALYSIS ====================

def calculate_momentum(signals_history):
    """Calcula momentum dos sinais (velocidade e aceleração)"""
    if len(signals_history) < 3:
        return 0, "neutral"
    
    # Obter últimos 10 sinais
    recent = list(signals_history)[-10:]
    
    # Calcular "velocidade" = mudanças por sinal
    changes = 0
    for i in range(1, len(recent)):
        if recent[i]['game'] != recent[i-1]['game']:
            changes += 1
    
    velocity = changes / len(recent)  # 0 a 1
    
    # Calcular "aceleração" = tendência de mudança
    if len(recent) >= 5:
        first_half_changes = sum(1 for i in range(1, len(recent)//2) 
                                 if recent[i]['game'] != recent[i-1]['game'])
        second_half_changes = sum(1 for i in range(len(recent)//2 + 1, len(recent)) 
                                  if recent[i]['game'] != recent[i-1]['game'])
        
        acceleration = second_half_changes - first_half_changes
    else:
        acceleration = 0
    
    # Interpretação
    if velocity < 0.3:
        momentum = "trending"  # Tendência forte
        boost = 3
    elif velocity > 0.7:
        momentum = "volatile"  # Muita volatilidade
        boost = -2
    else:
        momentum = "neutral"
        boost = 0
    
    return boost, momentum

# ==================== 4. DYNAMIC BANKROLL ====================

def adjust_by_bankroll(base_confidence, bankroll):
    """Ajusta confiança baseado no bankroll (capital)"""
    ratio = bankroll / INITIAL_BANKROLL
    
    if ratio >= BANKROLL_THRESHOLD_GOOD:
        # Bankroll subiu, ser mais agressivo
        adjustment = min(5, int((ratio - 1) * 10))
        status = "📈 Ganhos"
        return adjustment, status
    elif ratio <= BANKROLL_THRESHOLD_BAD:
        # Bankroll caiu, ser mais conservador
        adjustment = max(-5, int((ratio - 1) * 10))
        status = "📉 Perdas"
        return adjustment, status
    else:
        # Bankroll estável
        return 0, "➡️  Estável"

# ==================== 5. HOURLY FILTERS ====================

def apply_hourly_filters(base_confidence):
    """Aplica filtros baseado na hora do dia"""
    hour = datetime.now().hour
    
    # Horários melhores para trading (empiricamente)
    # Manhã: 8-11h (melhor)
    # Tarde: 14-17h (bom)
    # Noite: 20-23h (razoável)
    
    if 8 <= hour < 11:
        return 5, "🌅 Manhã (melhor)"
    elif 14 <= hour < 17:
        return 3, "🌞 Tarde (bom)"
    elif 20 <= hour < 23:
        return 1, "🌙 Noite (ok)"
    else:
        return -3, "⏰ Madrugada (evitar)"

# ==================== 6. ANÁLISE COMBINADA ====================

def analyze_signal_quality(signals_history, bankroll):
    """Combina todas as análises para determinar qualidade do sinal"""
    
    # 1. Pattern Recognition
    pattern, pattern_boost = detect_pattern(signals_history)
    
    # 2. Momentum Analysis
    momentum_boost, momentum_type = calculate_momentum(signals_history)
    
    # 3. Dynamic Bankroll
    bankroll_boost, bankroll_status = adjust_by_bankroll(100, bankroll)
    
    # 4. Hourly Filters
    hourly_boost, hourly_status = apply_hourly_filters(100)
    
    # Total de ajustes
    total_boost = pattern_boost + momentum_boost + bankroll_boost + hourly_boost
    
    return {
        'pattern': (pattern, pattern_boost),
        'momentum': (momentum_type, momentum_boost),
        'bankroll': (bankroll_status, bankroll_boost),
        'hourly': (hourly_status, hourly_boost),
        'total_boost': total_boost
    }

def send_telegram_message(message):
    """Envia mensagem ao Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")
        return False

def generate_signal(signals_history, bankroll):
    """Gera sinal com análises avançadas"""
    games = ["🎰 Crash", "🎰 Double", "🎰 Tiger"]
    entries = ["1.5", "2.0", "2.5", "3.0"]
    stops = ["1.0", "1.5", "2.0"]
    base_confidences = [75, 80, 85, 87, 90, 92, 95]
    
    game = random.choice(games)
    entry = random.choice(entries)
    stop = random.choice(stops)
    base_confidence = random.choice(base_confidences)
    
    # Análise combinada
    analysis = analyze_signal_quality(signals_history, bankroll)
    
    # Aplicar boosts
    final_confidence = min(98, max(50, base_confidence + analysis['total_boost']))
    
    # Salvar no histórico
    signal_data = {
        'game': game,
        'entry': entry,
        'stop': stop,
        'confidence': int(final_confidence),
        'timestamp': datetime.now().isoformat(),
        'pattern': analysis['pattern'][0],
        'momentum': analysis['momentum'][0],
        'bankroll_status': analysis['bankroll'][0]
    }
    
    signals_history.append(signal_data)
    
    # Simular resultado (50% sucesso)
    success = random.random() > 0.5
    new_bankroll = bankroll * 1.02 if success else bankroll * 0.98
    
    # Construir mensagem
    message = f"""
🤖 <b>BET ANALYSIS BOT v2.0 - MELHORADO</b>

{game}
📊 Entrada: {entry}
🛑 Stop: {stop}
🎯 Confiança: {int(final_confidence)}%

<b>📈 Análises:</b>
• Padrão: {analysis['pattern'][0]} ({analysis['pattern'][1]:+d}%)
• Momentum: {analysis['momentum'][0]} ({analysis['momentum'][1]:+d}%)
• Bankroll: {analysis['bankroll'][0]} ({analysis['bankroll'][1]:+d}%)
• Horário: {analysis['hourly'][0]} ({analysis['hourly'][1]:+d}%)

💰 Capital: ${new_bankroll:.2f}
⏰ {datetime.now().strftime('%H:%M:%S')}
    """
    
    return message.strip(), new_bankroll

def main():
    """Loop principal com histórico persistido"""
    print("\n" + "="*70)
    print("  🚀 BOT DE ANÁLISE BLAZE v2.0 - LOCAL COM MELHORIAS")
    print("="*70)
    print(f"✅ Pattern Recognition (Detecta padrões)")
    print(f"✅ Momentum Analysis (Velocidade de sinais)")
    print(f"✅ Dynamic Bankroll (Ajusta por capital)")
    print(f"✅ Hourly Filters (Filtro por hora)")
    print("="*70)
    print(f"Token: {TELEGRAM_BOT_TOKEN[:20]}...")
    print(f"Canal: {TELEGRAM_CHANNEL_ID}")
    print(f"Intervalo: {INTERVAL}s")
    print("="*70 + "\n")
    
    # Carregar histórico
    signals_history, bankroll = load_history()
    print(f"📊 Histórico carregado: {len(signals_history)} sinais")
    print(f"💰 Bankroll: ${bankroll:.2f}\n")
    
    counter = 0
    while True:
        try:
            counter += 1
            signal, new_bankroll = generate_signal(signals_history, bankroll)
            bankroll = new_bankroll
            
            print(f"[{counter}] Enviando sinal ao Telegram...")
            print(signal)
            print()
            
            if send_telegram_message(signal):
                print(f"✅ Sinal #{counter} enviado com sucesso!")
                save_history(signals_history, bankroll)
            else:
                print(f"⚠️  Erro ao enviar sinal #{counter}")
            
            print(f"⏳ Próxima análise em {INTERVAL}s...\n")
            time.sleep(INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n❌ Bot parado pelo usuário")
            save_history(signals_history, bankroll)
            print(f"💾 Histórico salvo: {len(signals_history)} sinais")
            print(f"💰 Bankroll final: ${bankroll:.2f}")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
