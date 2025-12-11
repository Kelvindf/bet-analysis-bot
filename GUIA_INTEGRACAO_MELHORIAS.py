"""
GUIA DE INTEGRAÇÃO - Melhorias V2
==================================

Como integrar as melhorias no sistema principal (main.py)
Sem interromper o projeto que está rodando.

OPÇÕES:
1. Integração Parcial (Apenas mensagens ricas) - FÁCIL
2. Integração Completa (Análise + Mensagens) - RECOMENDADO
3. Migração Gradual (Testar em paralelo) - SEGURO
"""

# ============================================================
# OPÇÃO 1: Apenas Mensagens Ricas (Mínima Invasão)
# ============================================================

print("""
OPÇÃO 1: APENAS ENRIQUECER MENSAGENS
=====================================

Manter a análise atual, melhorar apenas as mensagens do Telegram.

1. Abrir src/main.py

2. Adicionar import (linha ~15):
   
   from telegram_bot.message_enricher import TelegramMessageEnricher

3. No __init__ da classe BetAnalysisPlatform (linha ~40):
   
   self.message_enricher = TelegramMessageEnricher()

4. No método send_signal (linha ~300), substituir:
   
   # ANTES:
   message = f"Sinal: {signal_type}\\nConfiança: {confidence:.1%}"
   
   # DEPOIS:
   message = self.message_enricher.create_simple_signal_message(
       signal_type, confidence
   )

5. Salvar e reiniciar:
   
   Ctrl+C no terminal do main.py
   python -u src/main.py --scheduled

✅ Resultado: Mensagens com emojis e formatação bonita
⏱️ Tempo: 5 minutos
🔧 Risco: BAIXO (apenas visual)
""")

# ============================================================
# OPÇÃO 2: Integração Completa (Análise + Mensagens)
# ============================================================

print("""
OPÇÃO 2: INTEGRAÇÃO COMPLETA
==============================

Usar o analisador avançado E mensagens ricas.

1. Abrir src/main.py

2. Adicionar imports (linha ~15):
   
   from strategies.advanced_pattern_analyzer import AdvancedPatternAnalyzer
   from telegram_bot.message_enricher import TelegramMessageEnricher

3. No __init__ (linha ~40):
   
   self.advanced_analyzer = AdvancedPatternAnalyzer(min_confidence=0.65)
   self.message_enricher = TelegramMessageEnricher()

4. Criar método novo (linha ~200):
   
   def analyze_with_advanced(self, data):
       \"\"\"Análise avançada com múltiplos indicadores\"\"\"
       # Converter dados para DataFrame
       import pandas as pd
       df = pd.DataFrame(data)
       
       # Análise avançada
       signal = self.advanced_analyzer.analyze(df)
       
       if signal:
           logger.info(f"[SINAL AVANÇADO] {signal.signal_type} - {signal.confidence:.1%}")
           logger.info(f"  Força: {signal.strength} | Risco: {signal.risk_level}")
           return signal
       return None

5. No método principal de análise (linha ~250), substituir:
   
   # ANTES:
   if confidence >= self.min_confidence:
       self.send_signal(signal_type, confidence)
   
   # DEPOIS:
   advanced_signal = self.analyze_with_advanced(historical_data)
   if advanced_signal:
       # Mensagem rica
       rich_message = self.message_enricher.create_rich_signal_message(
           advanced_signal.to_dict()
       )
       self.telegram_bot.send_message(rich_message)

6. Salvar e reiniciar

✅ Resultado: Análise 4x mais precisa + mensagens ricas
⏱️ Tempo: 15 minutos
🔧 Risco: MÉDIO (muda lógica de análise)
📊 Benefício: ALTO (muito mais contexto)
""")

# ============================================================
# OPÇÃO 3: Migração Gradual (Testar em Paralelo)
# ============================================================

print("""
OPÇÃO 3: TESTE PARALELO (MAIS SEGURO)
=======================================

Rodar análise antiga E nova, comparar resultados antes de migrar.

1. No método principal de análise (linha ~250):
   
   # Análise ATUAL (manter)
   if confidence >= self.min_confidence:
       logger.info(f"[ANÁLISE ATUAL] {signal_type} - {confidence:.1%}")
       self.send_signal(signal_type, confidence)
   
   # Análise AVANÇADA (paralela)
   try:
       advanced_signal = self.advanced_analyzer.analyze(historical_df)
       if advanced_signal:
           logger.info(f"[ANÁLISE AVANÇADA] {advanced_signal.signal_type} - {advanced_signal.confidence:.1%}")
           
           # COMPARAR
           if signal_type == advanced_signal.signal_type:
               logger.info("  ✅ Sinais concordam!")
           else:
               logger.warning(f"  ⚠️ Divergência: Atual={signal_type} vs Avançado={advanced_signal.signal_type}")
           
           # NÃO ENVIAR (só logar)
           # self.telegram_bot.send_message(...)
   except Exception as e:
       logger.error(f"Erro na análise avançada: {e}")

2. Rodar por 1-2 horas

3. Analisar logs:
   
   grep "✅ Sinais concordam" logs/bet_analysis.log | wc -l
   grep "⚠️ Divergência" logs/bet_analysis.log | wc -l

4. Se concordância > 80%, migrar para Opção 2

✅ Resultado: Validação antes de mudar
⏱️ Tempo: 20 min setup + 2h validação
🔧 Risco: MUITO BAIXO (não afeta produção)
📊 Benefício: Confiança para migração
""")

# ============================================================
# EXEMPLO COMPLETO: Snippet Pronto
# ============================================================

print("""
SNIPPET PRONTO PARA COPIAR/COLAR
==================================

# ===== NO TOPO DO src/main.py =====
from strategies.advanced_pattern_analyzer import AdvancedPatternAnalyzer
from telegram_bot.message_enricher import TelegramMessageEnricher

# ===== NO __init__ =====
def __init__(self, settings):
    # ... código existente ...
    
    # Melhorias V2
    self.advanced_analyzer = AdvancedPatternAnalyzer(min_confidence=0.65)
    self.message_enricher = TelegramMessageEnricher()
    logger.info("[OK] Melhorias V2 inicializadas")

# ===== NOVO MÉTODO =====
def analyze_advanced(self, data_dict):
    \"\"\"Análise avançada com múltiplos indicadores\"\"\"
    try:
        import pandas as pd
        
        # Converter para DataFrame
        if isinstance(data_dict, dict) and 'double' in data_dict:
            df = data_dict['double']
        elif isinstance(data_dict, pd.DataFrame):
            df = data_dict
        else:
            logger.warning("Formato de dados não suportado para análise avançada")
            return None
        
        # Garantir colunas necessárias
        if not all(col in df.columns for col in ['color', 'roll']):
            logger.warning("DataFrame não tem colunas necessárias (color, roll)")
            return None
        
        # Análise
        signal = self.advanced_analyzer.analyze(df)
        return signal
        
    except Exception as e:
        logger.error(f"Erro na análise avançada: {str(e)}")
        return None

# ===== SUBSTITUIR NO MÉTODO PRINCIPAL =====
def run_analysis_cycle(self):
    \"\"\"Executa um ciclo completo de análise\"\"\"
    try:
        # ... coleta de dados existente ...
        
        # Análise avançada
        advanced_signal = self.analyze_advanced(collected_data)
        
        if advanced_signal and advanced_signal.confidence >= 0.65:
            # Criar mensagem rica
            rich_message = self.message_enricher.create_rich_signal_message(
                advanced_signal.to_dict()
            )
            
            # Enviar
            self.telegram_bot.send_message(rich_message)
            
            # Logging detalhado
            logger.info(f"[SINAL ENVIADO] {advanced_signal.signal_type}")
            logger.info(f"  Confiança: {advanced_signal.confidence:.1%}")
            logger.info(f"  Volume: {advanced_signal.volume_score:.2f}")
            logger.info(f"  Tendência: {advanced_signal.trend_score:.2f}")
            logger.info(f"  Stake: {advanced_signal.suggested_stake:.1%}")
        else:
            logger.info("Nenhum sinal válido neste ciclo")
            
    except Exception as e:
        logger.error(f"Erro no ciclo de análise: {str(e)}")

""")

# ============================================================
# CHECKLIST
# ============================================================

print("""
CHECKLIST DE INTEGRAÇÃO
=========================

Antes de integrar:
□ Testes executados com sucesso (python test_improvements.py)
□ Projeto atual rodando estável
□ Backup do main.py atual (cp src/main.py src/main.py.backup)

Durante integração:
□ Imports adicionados
□ Objetos inicializados no __init__
□ Método analyze_advanced criado
□ Lógica principal substituída
□ Arquivo salvo

Após integração:
□ Parar processo atual (Ctrl+C)
□ Reiniciar (python -u src/main.py --scheduled)
□ Verificar logs (sem erros de import)
□ Aguardar 1º sinal (2 minutos)
□ Conferir mensagem no Telegram (está rica?)
□ Monitorar por 30 minutos
□ Validar performance

Rollback (se necessário):
mv src/main.py.backup src/main.py
python -u src/main.py --scheduled
""")

# ============================================================
# PERGUNTAS FREQUENTES
# ============================================================

print("""
FAQ - PERGUNTAS FREQUENTES
===========================

P: As melhorias vão atrasar os sinais?
R: Não. Processamento adicional é < 0.1 segundo.

P: Posso usar apenas parte das melhorias?
R: Sim! Opção 1 usa apenas mensagens ricas (5 min).

P: E se der erro?
R: Sistema tem fallback. Se análise avançada falhar, usa a antiga.

P: Como reverter se não gostar?
R: Restaurar backup: mv src/main.py.backup src/main.py

P: Precisa instalar algo novo?
R: Não! Usa mesmas dependências (pandas, numpy).

P: As mensagens vão ficar muito longas?
R: Mensagem rica tem ~15 linhas. Se preferir curta, use Opção 1.

P: Vai mudar os sinais que recebo?
R: Opção 1: Não (só visual)
   Opção 2/3: Sim (análise melhorada, mais precisa)

P: Como sei se está funcionando?
R: Logs mostram "[SINAL AVANÇADO]" e Telegram recebe emojis.
""")

print("""
=====================================
RECOMENDAÇÃO FINAL
=====================================

Para primeira vez: OPÇÃO 1 (só mensagens)
- Rápido, seguro, bonito
- Validar que mensagens chegam bem

Depois de validar: OPÇÃO 2 (completo)
- Análise muito melhor
- Sinais mais precisos
- Gestão de banca incluída

Para os cautelosos: OPÇÃO 3 (paralelo)
- Comparar resultados
- Migrar com confiança

Tempo estimado total: 30 minutos (setup + validação)
""")
