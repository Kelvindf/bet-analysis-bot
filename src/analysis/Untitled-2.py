"""
Script para verificar resultados dos sinais enviados
Execute após as apostas para registrar acertos/erros
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tracking.result_tracker import ResultTracker
from datetime import datetime, timedelta

tracker = ResultTracker()

print("\n" + "="*70)
print("🎯 VERIFICAÇÃO DE RESULTADOS - Sistema de Tracking")
print("="*70)

# Mostrar sinais pendentes (últimas 24h)
pending = tracker.get_pending_signals()
recent = [s for s in pending 
          if datetime.fromisoformat(s['timestamp']) > datetime.now() - timedelta(hours=24)]

if not recent:
    print("\n✅ Não há sinais pendentes de verificação nas últimas 24h")
else:
    print(f"\n📋 {len(recent)} sinal(is) pendente(s) de verificação:\n")
    
    for i, signal in enumerate(recent, 1):
        ts = datetime.fromisoformat(signal['timestamp'])
        print(f"{i}. [{signal['signal_id']}]")
        print(f"   Sinal: {signal['signal_type']}")
        print(f"   Confiança: {signal['confidence']:.1%}")
        print(f"   Horário: {ts.strftime('%d/%m %H:%M:%S')}")
        print()
    
    # Perguntar resultados
    print("Digite o resultado de cada sinal:")
    print("  W = Win (acertou)")
    print("  L = Loss (errou)")
    print("  S = Skip (pular)")
    print()
    
    for i, signal in enumerate(recent, 1):
        while True:
            result = input(f"Sinal #{i} ({signal['signal_type']}): ").strip().upper()
            
            if result == 'W':
                tracker.register_result(signal['signal_id'], won=True)
                print(f"  ✅ Registrado como ACERTO\n")
                break
            elif result == 'L':
                tracker.register_result(signal['signal_id'], won=False)
                print(f"  ❌ Registrado como ERRO\n")
                break
            elif result == 'S':
                print(f"  ⏭️  Pulado\n")
                break
            else:
                print("  ⚠️  Opção inválida! Use W, L ou S")

# Mostrar estatísticas
print("\n" + "="*70)
print("📊 ESTATÍSTICAS DE ACERTOS")
print("="*70)

stats = tracker.get_stats()

if stats:
    print(f"\nTotal verificado: {stats['total_verified']}")
    print(f"Acertos: {stats['wins']} ✅")
    print(f"Erros: {stats['losses']} ❌")
    print(f"Taxa de acerto: {stats['win_rate_pct']}")
    
    print("\n📈 Por nível de confiança:")
    for conf_range, data in stats.get('by_confidence', {}).items():
        win_rate = data['wins'] / data['total'] if data['total'] > 0 else 0
        print(f"  {conf_range}: {data['wins']}/{data['total']} ({win_rate*100:.1f}%)")
else:
    print("\n⚠️  Nenhum resultado verificado ainda")

print("\n" + "="*70)