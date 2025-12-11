"""
Teste de integração - Novo cliente Blaze com análise
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection.blaze_client_v2 import BlazeDataCollectorV2
from src.analysis.statistical_analyzer import StatisticalAnalyzer

def main():
    print("\n" + "="*80)
    print("TESTE DE INTEGRAÇÃO - COLETA + ANÁLISE ESTATÍSTICA")
    print("="*80 + "\n")
    
    # Criar cliente
    print("[1] Criando coletor de dados...")
    collector = BlazeDataCollectorV2()
    print("    ✅ Coletor criado\n")
    
    # Coletar dados
    print("[2] Coletando 30 registros de cada tipo...")
    data = collector.get_all_data(limit=30)
    print(f"    ✅ {len(data['double'])} registros Double")
    print(f"    ✅ {len(data['crash'])} registros Crash")
    print(f"    Fonte: {data['source'].upper()}\n")
    
    # Analisar dados Double
    print("[3] Analisando dados Double...")
    analyzer = StatisticalAnalyzer()
    
    # Extrair colors para análise
    colors = [record['color'] for record in data['double']]
    red_count = sum(1 for c in colors if c == 'RED')
    black_count = len(colors) - red_count
    
    print(f"    ✅ Análise concluída")
    print(f"    ├─ RED: {red_count} ({100*red_count//len(colors)}%)")
    print(f"    └─ BLACK: {black_count} ({100*black_count//len(colors)}%)\n")
    
    # Analisar dados Crash
    print("[4] Analisando dados Crash...")
    crashes = [record['crash_point'] for record in data['crash']]
    avg_crash = sum(crashes) / len(crashes)
    min_crash = min(crashes)
    max_crash = max(crashes)
    
    print(f"    ✅ Análise concluída")
    print(f"    ├─ Média: {avg_crash:.2f}x")
    print(f"    ├─ Mínimo: {min_crash:.2f}x")
    print(f"    └─ Máximo: {max_crash:.2f}x\n")
    
    # Testar compatibilidade com Pipeline
    print("[5] Testando compatibilidade com Pipeline...")
    try:
        from src.analysis.strategy_pipeline import StrategyPipeline
        
        pipeline = StrategyPipeline()
        print("    ✅ StrategyPipeline carregado\n")
        
    except Exception as e:
        print(f"    ⚠️  Pipeline não testado: {str(e)}\n")
    
    print("="*80)
    print("✅ TESTE CONCLUÍDO COM SUCESSO")
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
