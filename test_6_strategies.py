#!/usr/bin/env python3
"""
Teste completo do pipeline de 6 estratégias

Verifica se todas as 6 engrenagens estão funcionando corretamente
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Adicionar src ao path (resolve para caminho absoluto)
src_path = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src_path))

# Tenta importar o StrategyPipeline da forma padrão; se falhar, tenta um fallback
try:
    from analysis.strategy_pipeline import StrategyPipeline
except Exception:
    try:
        # Em alguns setups o package raiz pode ser 'src'
        from src.analysis.strategy_pipeline import StrategyPipeline
    except Exception as e:
        raise ImportError(f"Não foi possível importar 'StrategyPipeline' a partir de 'analysis' nem de 'src.analysis': {e}")


def test_6_strategies():
    """Testa pipeline completo com 6 estratégias"""
    
    print("=" * 80)
    print("TESTE: Pipeline com 6 Estratégias (Engrenagens)")
    print("=" * 80)
    
    # Criar pipeline
    pipeline = StrategyPipeline()
    
    # Dados de teste (fallback-like: 100 cores)
    test_colors = ['vermelho', 'preto'] * 50
    test_colors = test_colors[:80]  # 80 cores
    
    # Adicionar desequilíbrio (mais preto nos últimos 10)
    recent_desequilibrio = ['preto'] * 8 + ['vermelho'] * 2
    test_colors_with_bias = test_colors[:-10] + recent_desequilibrio
    
    # Criar preços fake (para Strategy 2)
    prices = [100.0 + i*0.5 for i in range(len(test_colors_with_bias))]
    
    # Dados de sinal
    signal_data = {
        'signal_id': 'test_001',
        'recent_colors': recent_desequilibrio,
        'all_colors': test_colors_with_bias,
        'prices': prices,
        'game_id': 'game_123',
        'timestamp': datetime.now(),
        'signal_type': 'Unknown',
        'initial_confidence': 0.60
    }
    
    # Processar sinal (passa por todas as 6 estratégias)
    signal = pipeline.process_signal(signal_data)
    
    print("\n" + "=" * 80)
    print("RESULTADOS DO PIPELINE")
    print("=" * 80)
    
    print(f"\nSinal ID: {signal.signal_id}")
    print(f"Tipo de Sinal: {signal.signal_type}")
    print(f"Confiança Inicial: {signal.initial_confidence:.1%}")
    print(f"Confiança Final: {signal.final_confidence:.1%}")
    print(f"É Válido: {signal.is_valid}")
    print(f"Estratégias que Passaram: {signal.strategies_passed}/6")
    
    print("\n" + "-" * 80)
    print("DETALHES DE CADA ESTRATÉGIA:")
    print("-" * 80)
    
    strategy_names = [
        "Strategy1_Pattern",
        "Strategy2_Technical",
        "Strategy3_Confidence",
        "Strategy4_Confirmation",
        "Strategy5_MonteCarlo",
        "Strategy6_RunTest"
    ]
    
    all_passed = []
    all_rejected = []
    
    for i, strategy_name in enumerate(strategy_names, 1):
        if strategy_name in signal.strategy_results:
            result, confidence = signal.strategy_results[strategy_name]
            details = signal.strategy_details.get(strategy_name, {})
            
            print(f"\n[ENGRENAGEM {i}] {strategy_name}")
            print(f"  Status: {result.value.upper()}")
            print(f"  Confiança: {confidence:.1%}")
            
            # Mostrar alguns detalhes importantes
            if isinstance(details, dict):
                if 'pattern' in details:
                    print(f"  Padrão: {details.get('pattern')}")
                if 'subrepresentada' in details:
                    print(f"  Cor Subrepresentada: {details.get('subrepresentada')}")
                if 'rsi' in details:
                    print(f"  RSI: {details.get('rsi')}")
                if 'z_score' in details:
                    print(f"  Z-Score: {details.get('z_score')}")
                if 'interpretation' in details:
                    print(f"  Interpretação: {details.get('interpretation')}")
            
            if result.value == 'pass':
                all_passed.append(strategy_name)
            else:
                all_rejected.append(strategy_name)
    
    print("\n" + "=" * 80)
    print("RESUMO")
    print("=" * 80)
    
    print(f"\n✓ Estratégias que PASSARAM ({len(all_passed)}/6):")
    for s in all_passed:
        print(f"  - {s}")
    
    if all_rejected:
        print(f"\n✗ Estratégias que FALHARAM ({len(all_rejected)}/6):")
        for s in all_rejected:
            print(f"  - {s}")
    
    print(f"\n{'='*80}")
    print(f"VÁLIDO PARA ENVIO? {'SIM ✓' if signal.is_valid else 'NÃO ✗'}")
        print("="*80)
    
    # Teste 2: Verificar que todas as 6 estratégias são chamadas
    print("\n\n" + "=" * 80)
    print("VERIFICAÇÃO: Todas as 6 estratégias foram processadas?")
    print("=" * 80)
    
    expected_strategies = set(strategy_names)
    actual_strategies = set(signal.strategy_results.keys())
    
    if expected_strategies == actual_strategies:
        print("\n✓ SUCESSO: Todas as 6 estratégias foram processadas!")
        print(f"  Estratégias processadas: {len(actual_strategies)}")
    else:
        print("\n✗ ERRO: Nem todas as estratégias foram processadas!")
        print(f"  Esperadas: {expected_strategies}")
        print(f"  Processadas: {actual_strategies}")
        print(f"  Faltando: {expected_strategies - actual_strategies}")
        print(f"\n\n[RESUMO FINAL]")
        print(f"Sinal válido: {signal.is_valid}")
        print(f"Estratégias processadas: {len(actual_strategies)}/6")
        print(f"Estratégias que passaram: {len(all_passed)}/6")
    
    return signal.is_valid


if __name__ == "__main__":
    try:
        is_valid = test_6_strategies()
        sys.exit(0 if is_valid else 1)
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
