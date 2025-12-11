#!/usr/bin/env python3
# test_blaze_real_connection.py
# Script prático para validar conexão real com Blaze

"""
Teste de Conectividade Real - Blaze API

Este script testa:
1. Conectividade básica com Blaze
2. Endpoints disponíveis
3. Estrutura de resposta
4. Taxa de limitação
5. Qualidade dos dados

Uso:
    python test_blaze_real_connection.py
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional

class BlazeAPITester:
    """Tester para validar integração com Blaze"""
    
    def __init__(self, base_url: str = "https://blaze.com/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.setup_headers()
        self.results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
    
    def setup_headers(self):
        """Configurar headers padrão"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Referer': 'https://blaze.com/',
            'Origin': 'https://blaze.com'
        })
    
    def print_header(self, title: str):
        """Imprimir header formatado"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70)
    
    def print_success(self, msg: str):
        print(f"[OK] {msg}")
    
    def print_error(self, msg: str):
        print(f"[ERRO] {msg}")
        self.results['failed'] += 1
        self.results['errors'].append(msg)
    
    def print_info(self, msg: str):
        print(f"[*] {msg}")
    
    def test_connectivity(self):
        """Teste 1: Conectividade básica"""
        self.print_header("TESTE 1: Conectividade Básica")
        
        try:
            response = self.session.get(
                f"{self.base_url}/games/crash/history",
                timeout=10,
                params={'limit': 1}
            )
            
            self.print_info(f"URL: {response.url}")
            self.print_info(f"Status Code: {response.status_code}")
            self.print_info(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
            self.print_info(f"Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                self.print_success("Conectividade OK")
                self.results['success'] += 1
                return True
            else:
                self.print_error(f"Status {response.status_code}: {response.text[:100]}")
                return False
        
        except requests.exceptions.Timeout:
            self.print_error("Timeout na conexão")
            return False
        except requests.exceptions.ConnectionError as e:
            self.print_error(f"Erro de conexão: {e}")
            return False
        except Exception as e:
            self.print_error(f"Erro inesperado: {e}")
            return False
    
    def test_endpoints(self):
        """Teste 2: Testar múltiplos endpoints"""
        self.print_header("TESTE 2: Endpoints Disponíveis")
        
        endpoints_to_test = {
            'crash_v1': '/games/crash/history',
            'crash_v2': '/crash_games/recent',
            'roulette': '/games/roulette/history',
            'double': '/games/double/history',
            'status': '/status',
        }
        
        for name, endpoint in endpoints_to_test.items():
            url = f"{self.base_url}{endpoint}"
            
            try:
                response = self.session.get(url, timeout=5, params={'limit': 5})
                status = f"[{response.status_code}]"
                
                if response.status_code == 200:
                    self.print_success(f"{name:15} - {status} OK")
                    self.results['success'] += 1
                else:
                    self.print_info(f"{name:15} - {status} (não está neste endpoint)")
                
            except requests.exceptions.Timeout:
                self.print_info(f"{name:15} - [TIMEOUT]")
            except Exception as e:
                self.print_info(f"{name:15} - [ERRO] {type(e).__name__}")
    
    def test_data_structure(self):
        """Teste 3: Validar estrutura de dados"""
        self.print_header("TESTE 3: Estrutura de Dados")
        
        try:
            response = self.session.get(
                f"{self.base_url}/games/crash/history",
                timeout=10,
                params={'limit': 5}
            )
            
            if response.status_code != 200:
                self.print_error("Endpoint não retornou 200")
                return False
            
            data = response.json()
            self.print_info(f"Tipo de resposta: {type(data).__name__}")
            
            # Analisar estrutura
            if isinstance(data, dict):
                print(f"Chaves principais: {list(data.keys())}")
                
                # Tentar encontrar array de registros
                records = None
                for key in ['data', 'records', 'games', 'results']:
                    if key in data and isinstance(data[key], list):
                        records = data[key]
                        print(f"Array encontrado em: '{key}'")
                        break
                
                if records is None:
                    records = data if isinstance(data, list) else []
            
            elif isinstance(data, list):
                print(f"Tipo de resposta: Lista com {len(data)} itens")
                records = data
            
            else:
                self.print_error(f"Tipo inesperado: {type(data)}")
                return False
            
            # Analisar primeiro registro
            if records and len(records) > 0:
                first_record = records[0]
                self.print_success(f"Total de registros: {len(records)}")
                self.print_info(f"\nEstrutura do primeiro registro:")
                
                for key, value in first_record.items():
                    print(f"  {key:20} = {value} ({type(value).__name__})")
                
                self.results['success'] += 1
                return True
            
            else:
                self.print_error("Nenhum registro retornado")
                return False
        
        except json.JSONDecodeError:
            self.print_error("Resposta não é JSON válido")
            return False
        except Exception as e:
            self.print_error(f"Erro ao processar dados: {e}")
            return False
    
    def test_rate_limiting(self):
        """Teste 4: Verificar rate limiting"""
        self.print_header("TESTE 4: Rate Limiting")
        
        print("Enviando 5 requisições rápidas...\n")
        
        times = []
        
        for i in range(5):
            try:
                start = time.time()
                response = self.session.get(
                    f"{self.base_url}/games/crash/history",
                    timeout=10,
                    params={'limit': 1}
                )
                elapsed = time.time() - start
                times.append(elapsed)
                
                status = "OK" if response.status_code == 200 else f"ERR {response.status_code}"
                print(f"Req {i+1}: [{status}] {elapsed:.2f}s", end="")
                
                # Verificar rate limit headers
                if 'X-RateLimit-Remaining' in response.headers:
                    remaining = response.headers['X-RateLimit-Remaining']
                    print(f" | Restantes: {remaining}", end="")
                
                if 'Retry-After' in response.headers:
                    print(f" | Retry-After: {response.headers['Retry-After']}", end="")
                
                print()
                
            except Exception as e:
                print(f"Req {i+1}: [ERRO] {e}")
        
        # Calcular estatísticas
        if times:
            avg_time = sum(times) / len(times)
            self.print_info(f"\nTempo médio por requisição: {avg_time:.2f}s")
            self.print_success("Rate limiting verificado")
            self.results['success'] += 1
    
    def test_data_freshness(self):
        """Teste 5: Verificar se dados são atualizados"""
        self.print_header("TESTE 5: Freshness dos Dados")
        
        try:
            response = self.session.get(
                f"{self.base_url}/games/crash/history",
                timeout=10,
                params={'limit': 10}
            )
            
            if response.status_code != 200:
                self.print_error("Não conseguiu buscar dados")
                return False
            
            data = response.json()
            
            # Extrair timestamps
            records = data if isinstance(data, list) else data.get('data', [])
            
            if not records:
                self.print_error("Nenhum registro para análise")
                return False
            
            # Procurar campo de timestamp
            timestamp_fields = ['created_at', 'timestamp', 'date', 'time']
            timestamp_field = None
            
            for field in timestamp_fields:
                if field in records[0]:
                    timestamp_field = field
                    break
            
            if not timestamp_field:
                self.print_error(f"Nenhum campo de timestamp encontrado. Campos: {list(records[0].keys())}")
                return False
            
            self.print_info(f"Campo de timestamp: '{timestamp_field}'")
            
            # Analisar timestamps
            from datetime import datetime, timedelta
            
            oldest = records[0][timestamp_field]
            newest = records[0][timestamp_field]
            
            for record in records[1:]:
                ts = record[timestamp_field]
                if ts < oldest:
                    oldest = ts
                if ts > newest:
                    newest = ts
            
            self.print_info(f"Mais antigo: {oldest}")
            self.print_info(f"Mais novo: {newest}")
            
            # Verificar se timestamp é recente
            now = datetime.now().isoformat()
            if isinstance(newest, str) and newest > now[:19]:  # Comparar apenas a parte da data
                self.print_success("Dados são atualizados em tempo real")
            else:
                self.print_info("Dados aparecem ser históricos")
            
            self.results['success'] += 1
            return True
        
        except Exception as e:
            self.print_error(f"Erro ao verificar freshness: {e}")
            return False
    
    def print_summary(self):
        """Imprimir resumo final"""
        self.print_header("RESUMO DOS TESTES")
        
        total = self.results['success'] + self.results['failed']
        
        print(f"\nTestes bem-sucedidos: {self.results['success']}/{total}")
        print(f"Testes falhados: {self.results['failed']}/{total}")
        
        if self.results['errors']:
            print(f"\nErros encontrados:")
            for error in self.results['errors']:
                print(f"  - {error}")
        
        print("\n" + "="*70)
        
        if self.results['failed'] == 0:
            print("[OK] TODOS OS TESTES PASSARAM!")
            print("\nPróximas ações:")
            print("  1. Validar que as URLs estão corretas")
            print("  2. Implementar autenticação (se necessária)")
            print("  3. Adicionar rate limiting")
            print("  4. Integrar ao código principal")
        else:
            print("[AVISO] Alguns testes falharam!")
            print("\nPróximas ações:")
            print("  1. Revisar os erros acima")
            print("  2. Verificar conectividade com Blaze")
            print("  3. Validar URLs dos endpoints")
            print("  4. Contatar suporte Blaze se necessário")
        
        print("="*70)

def main():
    """Executar testes"""
    
    print("\n")
    print("█████████████████████████████████████████████████████████████████████")
    print("█  VALIDADOR DE INTEGRAÇÃO - BLAZE API                             █")
    print("█████████████████████████████████████████████████████████████████████")
    
    tester = BlazeAPITester()
    
    try:
        # Executar todos os testes
        tester.test_connectivity()
        tester.test_endpoints()
        tester.test_data_structure()
        tester.test_rate_limiting()
        tester.test_data_freshness()
        
        # Imprimir resumo
        tester.print_summary()
    
    except KeyboardInterrupt:
        print("\n\n[!] Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERRO CRÍTICO] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
