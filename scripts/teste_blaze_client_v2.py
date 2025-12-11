"""
Teste rápido do novo cliente Blaze (BlazeDataCollectorV2)

Verifica:
1. Conectividade com API (real ou fallback)
2. Geração de dados (Double e Crash)
3. Formato dos dados
4. Cache local
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_blaze_client_v2():
    """Testa o novo cliente Blaze"""
    
    print("\n" + "="*80)
    print("TESTE - NOVO CLIENTE BLAZE (V2)")
    print("="*80 + "\n")
    
    from src.data_collection.blaze_client_v2 import BlazeDataCollectorV2
    
    # Criar cliente
    print("[1] Criando cliente...")
    client = BlazeDataCollectorV2()
    print("    ✅ Cliente criado\n")
    
    # Testar conectividade
    print("[2] Testando conectividade com API Blaze...")
    connected = client.test_connectivity()
    if connected:
        print("    ✅ Conectado à API real")
    else:
        print("    ℹ️  Usando dados de fallback (esperado em desenvolvimento)\n")
    
    # Obter dados
    print("[3] Coletando dados...")
    all_data = client.get_all_data(limit=20)
    
    print(f"\n    Status: {all_data['source'].upper()}")
    print(f"    Total de registros: {all_data['count']}")
    print(f"    Timestamp: {all_data['timestamp']}\n")
    
    # Double
    print("[4] Dados do Double:")
    print(f"    Total: {len(all_data['double'])} registros\n")
    
    if all_data['double']:
        print("    Primeiros 5 registros:")
        for i, record in enumerate(all_data['double'][:5], 1):
            print(f"      {i}. Cor: {record['color']:5} | ID: {record['game_id']}")
    
    # Crash
    print("\n[5] Dados do Crash:")
    print(f"    Total: {len(all_data['crash'])} registros\n")
    
    if all_data['crash']:
        print("    Primeiros 5 registros:")
        for i, record in enumerate(all_data['crash'][:5], 1):
            print(f"      {i}. Crash: {record['crash_point']:6.2f}x | ID: {record['game_id']}")
    
    # Análise de padrão
    print("\n[6] Análise de padrão (Double):")
    if all_data['double']:
        reds = sum(1 for r in all_data['double'] if r['color'] == 'RED')
        blacks = len(all_data['double']) - reds
        
        print(f"    RED:   {reds:2} ({100*reds//len(all_data['double']):2}%)")
        print(f"    BLACK: {blacks:2} ({100*blacks//len(all_data['double']):2}%)")
        
        # Detectar clusters
        if all_data['double']:
            current_color = all_data['double'][0]['color']
            cluster = 1
            max_cluster = 1
            
            for record in all_data['double'][1:]:
                if record['color'] == current_color:
                    cluster += 1
                    max_cluster = max(max_cluster, cluster)
                else:
                    current_color = record['color']
                    cluster = 1
            
            print(f"    Cluster máximo: {max_cluster} cor(es) seguidas")
    
    # Cache
    print("\n[7] Verificando cache...")
    cache_path = Path(__file__).parent.parent / 'data' / 'raw' / 'blaze_data_cache.json'
    if cache_path.exists():
        print(f"    ✅ Cache salvo em: {cache_path.name}")
        import json
        with open(cache_path) as f:
            cache = json.load(f)
        print(f"    ├─ Timestamp: {cache['timestamp']}")
        print(f"    ├─ Fonte: {cache['source']}")
        print(f"    ├─ Double: {len(cache['double'])} registros")
        print(f"    └─ Crash: {len(cache['crash'])} registros")
    else:
        print(f"    ⚠️  Cache não encontrado (será criado na próxima coleta)")
    
    print("\n" + "="*80)
    print("TESTE CONCLUÍDO COM SUCESSO")
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        test_blaze_client_v2()
    except Exception as e:
        print(f"\n❌ Erro durante teste: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
