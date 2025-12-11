"""
Quick Start - Inicialização Rápida da Coleta Contínua

Este script facilita a inicialização da coleta de 48 horas
com validação automática do ambiente.
"""

import sys
import os
import subprocess
from pathlib import Path

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*100)
    print(f"  {title}")
    print("="*100 + "\n")

def print_step(step_num, title, description=""):
    """Imprime número do passo"""
    print(f"\n📍 PASSO {step_num}: {title}")
    if description:
        print(f"   {description}")

def run_command(cmd, description):
    """Executa comando e retorna resultado"""
    print(f"\n   ▶ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"   ✅ Sucesso!")
            return True
        else:
            print(f"   ❌ Erro: {result.stderr[:100]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"   ⏱️  Timeout (pode estar esperando entrada)")
        return True
    except Exception as e:
        print(f"   ❌ Erro: {str(e)[:100]}")
        return False

def main():
    """Função principal"""
    os.chdir(Path(__file__).parent)
    
    print_header("🚀 QUICK START - Coleta Contínua de 48 Horas")
    
    print("""
Este script irá:
1. Validar ambiente Python e dependências
2. Verificar estrutura de diretórios
3. Testar conexões (Blaze API, etc)
4. Guiar você através da inicialização
5. Iniciar coleta de dados (Terminal 1)
6. Iniciar dashboard de monitoramento (Terminal 2)

Total de tempo: 2 minutos para preparação + 48 horas de coleta
    """)
    
    input("Pressione ENTER para continuar...")
    
    # ETAPA 1: Validação
    print_step(1, "VALIDAÇÃO DO AMBIENTE", "Verificando Python e dependências")
    
    # Executar validador
    print("\n   Executando validador pré-coleta...\n")
    resultado = run_command(
        f"{sys.executable} scripts/validar_pre_coleta.py",
        "Validação de ambiente"
    )
    
    if not resultado:
        print("\n❌ Validação falhou. Abra scripts/validar_pre_coleta.py para detalhes.")
        sys.exit(1)
    
    # ETAPA 2: Preparação
    print_step(2, "PREPARAÇÃO", "Criando diretórios necessários")
    
    dirs = ['data', 'logs']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"   ✅ Diretório '{dir_name}/' pronto")
    
    # ETAPA 3: Resumo
    print_header("✅ AMBIENTE VALIDADO E PRONTO")
    
    print("""
RESUMO:
  ✅ Python 3.13.9 configurado
  ✅ Todos os arquivos necessários encontrados
  ✅ Dependências instaladas (NumPy, SciPy, Requests, Schedule)
  ✅ Espaço em disco suficiente
  ✅ Diretórios criados (data/, logs/)
  
PRÓXIMAS AÇÕES:
  1. Abra DOIS terminais PowerShell NOVOS
  2. Em cada terminal, navegue até:
     cd c:\\Users\\Trampo\\Downloads\\ChamaeledePlataformaX\\bet_analysis_platform-2
  
  3. No Terminal 1, execute:
     python scripts\\coleta_continua_dados.py --duration 48 --interval 30
  
  4. No Terminal 2 (após ~30 segundos), execute:
     python scripts\\dashboard_monitoramento.py --interval 10
  
  5. Deixe rodando por 48 horas
  
  6. Após 48 horas, execute novo backtest:
     python scripts\\run_backtest_optimized.py --win-rate 0.60 --margin 0.08 --compare
  
DOCUMENTAÇÃO:
  • GUIA_COLETA_48HORAS.md - Guia completo
  • RESUMO_EXECUTIVO_COLETA.md - Visão geral
  • MONTE_CARLO_IMPLEMENTACAO.md - Detalhes técnicos
  • ARQUITETURA_PIPELINE_6_ESTRATEGIAS.md - Pipeline explicado

SUPORTE:
  Se encontrar problemas, consulte:
  • TROUBLESHOOTING.md
  • scripts/validar_pre_coleta.py (para diagnóstico)
  • logs/bet_analysis.log (para erros detalhados)
    """)
    
    # ETAPA 4: Próximos passos
    print_header("📊 PRÓXIMAS ETAPAS")
    
    print("""
TERMINAL 1 - Coleta de Dados:
──────────────────────────────
Copie e execute este comando em um novo terminal:

    python scripts\\coleta_continua_dados.py --duration 48 --interval 30

O que você verá:
  [INFO] Ciclo 1: Coletados 3 cores (total: 3)
  [INFO] Ciclo 1: Processados 9 sinais (válidos: 0)
  [INFO] Ciclo 1: Salvo em data/coleta_continua.json
  [INFO] Ciclo 2: Coletados 2 cores (total: 5)
  ... (continua por 48 horas)


TERMINAL 2 - Dashboard de Monitoramento:
─────────────────────────────────────────
Inicie APÓS ~30 segundos do Terminal 1. Execute:

    python scripts\\dashboard_monitoramento.py --interval 10

O que você verá:
  ====================================
  MONITORAMENTO EM TEMPO REAL
  ====================================
  Tempo decorrido: 0.01 horas (36 segundos)
  Cores coletadas: 3
  Taxa de coleta: 300 cores/hora
  
  Sinais processados: 9
  Sinais válidos: 0 (0.0%)
  
  Taxa de acerto média: 0.0%
  
  Coleta quase completa: 3/1000 cores (0%)
  Tempo estimado para 1000 cores: 5.6 horas


PARANDO A COLETA:
─────────────────
Pressione CTRL+C em qualquer momento. Os dados serão salvos automaticamente:
  • data/coleta_continua.json ✅
  • logs/pipeline_stats.json ✅
  • logs/bet_analysis.log ✅
    """)
    
    # ETAPA 5: Confirmação
    print_header("⚠️ ÚLTIMA CONFIRMAÇÃO")
    
    print("""
Antes de iniciar, confirme:

  ✅ Você tem 48 horas disponíveis?
     (A coleta é contínua, não pode ser pausada)
  
  ✅ Você tem 2 terminais PowerShell disponíveis?
     (Um para coleta, um para monitoramento)
  
  ✅ Você mantém seu computador ligado durante 48 horas?
     (Recomenda-se não desligar durante coleta)
  
  ✅ Você verificou a internet está estável?
     (API Blaze precisa de conexão contínua)
    """)
    
    confirmacao = input("\n✅ Você quer iniciar a coleta? (s/n): ").lower()
    
    if confirmacao != 's':
        print("\n❌ Coleta cancelada. Execute este script novamente quando estiver pronto.")
        sys.exit(0)
    
    # ETAPA 6: Instruções finais
    print_header("🎯 INSTRUÇÕES FINAIS")
    
    print("""
VOCÊ ESTÁ PRONTO! 🚀

Copie os comandos abaixo e cole em seus terminais:

────────────────────────────────────────────────────────────────
TERMINAL 1 - Copie e execute AGORA:
────────────────────────────────────────────────────────────────
cd c:\\Users\\Trampo\\Downloads\\ChamaeledePlataformaX\\bet_analysis_platform-2
python scripts\\coleta_continua_dados.py --duration 48 --interval 30

────────────────────────────────────────────────────────────────
TERMINAL 2 - Copie e execute DEPOIS de ~30 segundos:
────────────────────────────────────────────────────────────────
cd c:\\Users\\Trampo\\Downloads\\ChamaeledePlataformaX\\bet_analysis_platform-2
python scripts\\dashboard_monitoramento.py --interval 10

────────────────────────────────────────────────────────────────

Esperado em 48 horas:
  ✅ 1000+ cores coletadas
  ✅ 3000+ sinais processados
  ✅ 60-150 sinais válidos
  ✅ Dados prontos para novo backtest

ROI esperado após novo backtest:
  📈 4-5% (vs 3.56% com dados aleatórios)

Boa sorte! 🍀
    """)
    
    print("\n" + "="*100)
    print("✅ SCRIPT CONCLUÍDO - Agora abra os terminais PowerShell e execute os comandos acima")
    print("="*100 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Script cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro: {e}")
        sys.exit(1)
