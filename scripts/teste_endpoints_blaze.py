"""
Teste dos novos endpoints da Blaze API (blaze.bet.br)

Testa conectividade com os endpoints corretos
"""

import sys
import requests
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

def test_blaze_endpoints():
    """Testa endpoints da Blaze API"""
    
    print("\n" + "="*80)
    print("TESTE - ENDPOINTS BLAZE API (blaze.bet.br)")
    print("="*80 + "\n")
    
    # URLs base para testar
    base_urls = [
        "https://blaze.bet.br/api",  # URL CORRIGIDA
        "https://api.blaze.bet.br",
        "https://blaze.com/api",
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    })
    
    # Testar cada URL base
    for base_url in base_urls:
        print(f"\n[*] Testando: {base_url}")
        print("-" * 80)
        
        # Endpoints para testar
        endpoints = [
            ("status", "Verificar status da API"),
            ("games", "Lista geral de games"),
            ("games?type=double", "Games Double"),
            ("games?type=crash", "Games Crash"),
            ("double/games", "Endpoint específico Double"),
            ("crash/games", "Endpoint específico Crash"),
            ("roulette", "Endpoint Roleta"),
            ("games/status", "Status dos games"),
        ]
        
        for endpoint, desc in endpoints:
            url = f"{base_url}/{endpoint}"
            try:
                response = session.get(url, timeout=3)
                
                status_icon = "✅" if response.status_code == 200 else "⚠️"
                print(f"  {status_icon} {endpoint:25} [{response.status_code}] - {desc}")
                
                # Se retornar 200, mostrar mais detalhes
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            keys = list(data.keys())[:3]
                            print(f"      └─ Chaves: {keys}")
                        elif isinstance(data, list):
                            print(f"      └─ Lista com {len(data)} itens")
                    except:
                        print(f"      └─ Resposta não é JSON válido")
                        
            except requests.exceptions.Timeout:
                print(f"  ❌ {endpoint:25} [TIMEOUT] - {desc}")
            except requests.exceptions.ConnectionError:
                print(f"  ❌ {endpoint:25} [CONNECTION ERROR] - {desc}")
            except Exception as e:
                print(f"  ❌ {endpoint:25} [ERROR] - {str(e)[:30]}")
    
    print("\n" + "="*80)
    print("TESTE CONCLUÍDO")
    print("="*80 + "\n")
    
    # Teste com novo cliente
    print("\n[*] Testando novo cliente Blaze (V2)...")
    print("-" * 80)
    
    from src.data_collection.blaze_client_v2 import BlazeDataCollectorV2
    
    client = BlazeDataCollectorV2()
    print(f"URLs configuradas:")
    for i, url in enumerate(client.base_urls, 1):
        print(f"  {i}. {url}")
    
    print(f"\nURL principal: {client.base_url}")
    print(f"Usando fallback: {client.use_fallback}")
    
    print("\nTestando conectividade...")
    is_available = client.test_connectivity()
    
    if is_available:
        print(f"✅ API DISPONÍVEL em: {client.base_url}")
    else:
        print(f"⚠️  API não disponível, usando fallback")
    
    print("\n" + "="*80)
    print("RECOMENDAÇÕES")
    print("="*80)
    print(f"""
1. Se https://blaze.bet.br/api respondeu:
   ✅ Novo cliente está configurado corretamente
   ✅ API real será usada automaticamente
   
2. Se não respondeu:
   ℹ️  Sistema continuará usando dados de fallback
   ℹ️  Quando API ficar disponível, será usado automaticamente
   
3. Para usar o novo cliente:
   cp src/data_collection/blaze_client_v2.py src/data_collection/blaze_client.py
   
4. Próximo passo:
   python scripts/teste_integracao_completa.py
    """)

if __name__ == "__main__":
    try:
        test_blaze_endpoints()
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
