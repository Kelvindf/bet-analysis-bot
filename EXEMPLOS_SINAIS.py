#!/usr/bin/env python3
"""
EXEMPLOS PRÁTICOS - Como os Sinais Funcionam Agora
Demonstra a melhoria na entrega e armazenamento de sinais
"""

# ============================================================================
# EXEMPLO 1: COMO UM SINAL DE CRASH FICA NO TELEGRAM
# ============================================================================

exemplo_crash_telegram = """
╔════════════════════════════════════════╗
║    🎮 ALERTA DE SINAL - CRASH 🎮      ║
╚════════════════════════════════════════╝

🔴 PREVISÃO: Vermelho

📊 ANÁLISE:
   Confiança: 🔥 MUITO ALTA (97.9%)
   Estratégias: 3/6 validadas
   Multiplicador esperado: 1.5x - 2.5x

⏰ TIMING:
   Horário: 00:14:13
   Data: 11/12/2025

💡 RECOMENDAÇÃO:
   • Comece com aposta pequena
   • Controle seu risco
   • Máximo 5% de seu bankroll

⚠️ DISCLAIMER:
Apostas envolvem risco alto. Jogue responsavelmente.
"""

# ============================================================================
# EXEMPLO 2: COMO UM SINAL DE DOUBLE FICA NO TELEGRAM
# ============================================================================

exemplo_double_telegram = """
╔════════════════════════════════════════╗
║    🎲 ALERTA DE SINAL - DOUBLE 🎲     ║
╚════════════════════════════════════════╝

🔴 PREVISÃO: Vermelho

📊 ANÁLISE:
   Confiança: ✅ ALTA (85.6%)
   Estratégias: 5/6 validadas
   Odds da aposta: 1.90x

⏰ TIMING:
   Horário: 00:15:00
   Data: 11/12/2025

💡 RECOMENDAÇÃO:
   • Cores têm odds de 1.90x
   • Branco paga 14.00x (risco maior)
   • Máximo 4% de seu bankroll

⚠️ DISCLAIMER:
Apostas envolvem risco. Jogue responsavelmente.
"""

# ============================================================================
# EXEMPLO 3: COMO OS DADOS FICAM NO BANCO DE DADOS (CRASH)
# ============================================================================

exemplo_bd_crash = {
    "id": "sig_crash_1702300453",
    "game": "Crash",
    "signal_type": "RED",
    "confidence": 0.979,
    "timestamp": "2025-12-11T00:14:13",
    "strategies_passed": 3,
    "bet_size": 45.50,
    "result": None,  # Aguardando resultado do jogo
    "metadata": {
        "odds": 2.1,
        "kelly_fraction": 0.25,
        "bankroll": 1000.0,
        "drawdown_percent": 2.3,
        "data_source": "blaze_api",
        "colors_analyzed": 100,
        "multiplicador_esperado": "1.5x - 2.5x"
    },
    "created_at": "2025-12-11T00:14:13",
    "updated_at": "2025-12-11T00:14:13"
}

# ============================================================================
# EXEMPLO 4: COMO OS DADOS FICAM NO BANCO DE DADOS (DOUBLE)
# ============================================================================

exemplo_bd_double = {
    "id": "sig_double_1702300500",
    "game": "Double",
    "signal_type": "RED",
    "confidence": 0.856,
    "timestamp": "2025-12-11T00:15:00",
    "strategies_passed": 5,
    "bet_size": 38.25,
    "result": None,  # Aguardando resultado do jogo
    "metadata": {
        "odds": 1.90,
        "kelly_fraction": 0.25,
        "bankroll": 1000.0,
        "drawdown_percent": 2.3,
        "data_source": "blaze_api",
        "colors_analyzed": 100,
        "cor_prevista": "Vermelho"
    },
    "created_at": "2025-12-11T00:15:00",
    "updated_at": "2025-12-11T00:15:00"
}

# ============================================================================
# EXEMPLO 5: DIFERENCIAÇÃO DE MENSAGENS POR JOGO
# ============================================================================

def exemplos_formatacao():
    """Demonstra como as mensagens são diferenciadas"""
    
    # Crash tem multiplicador esperado
    # Double tem odds fixas (1.90x para cores, 14.00x para branco)
    
    print("\n" + "="*60)
    print("DIFERENCIAÇÃO DE SINAIS")
    print("="*60)
    
    sinais = [
        {
            "game": "Crash",
            "signal": "Vermelho",
            "confidence": 0.979,
            "multiplicador": "1.5x - 2.5x",
            "emoji_jogo": "🎮"
        },
        {
            "game": "Double",
            "signal": "Preto",
            "confidence": 0.856,
            "odds": "1.90x",
            "emoji_jogo": "🎲"
        },
        {
            "game": "Double",
            "signal": "Branco",
            "confidence": 0.720,
            "odds": "14.00x",
            "emoji_jogo": "🎲"
        }
    ]
    
    for sinal in sinais:
        jogo = sinal['game']
        
        if jogo == "Crash":
            print(f"\n{sinal['emoji_jogo']} {jogo}")
            print(f"   Sinal: {sinal['signal']}")
            print(f"   Confiança: {sinal['confidence']:.1%}")
            print(f"   Multiplicador: {sinal['multiplicador']}")
            print(f"   Características: Dinâmico, rápido, gráfico linear")
        
        else:  # Double
            print(f"\n{sinal['emoji_jogo']} {jogo}")
            print(f"   Sinal: {sinal['signal']}")
            print(f"   Confiança: {sinal['confidence']:.1%}")
            print(f"   Odds: {sinal['odds']}")
            print(f"   Características: Roleta, cores/branco, odds fixas")

# ============================================================================
# EXEMPLO 6: RECOMENDAÇÕES BASEADAS EM CONFIANÇA
# ============================================================================

def exemplo_recomendacoes():
    """Demonstra as recomendações inteligentes de aposta"""
    
    print("\n" + "="*60)
    print("RECOMENDAÇÕES DE APOSTA")
    print("="*60)
    
    bankroll = 1000.0
    confiancas = [0.979, 0.856, 0.720, 0.650, 0.550]
    
    for conf in confiancas:
        # Determinar % máximo baseado em confiança
        if conf >= 0.90:
            percentual = 5
            nivel = "MUITO ALTA"
            emoji = "🔥"
        elif conf >= 0.80:
            percentual = 4
            nivel = "ALTA"
            emoji = "✅"
        elif conf >= 0.70:
            percentual = 3
            nivel = "MÉDIA"
            emoji = "✅"
        elif conf >= 0.60:
            percentual = 2
            nivel = "MODERADA"
            emoji = "⚠️"
        else:
            percentual = 1
            nivel = "BAIXA"
            emoji = "⚠️"
        
        aposta = bankroll * (percentual / 100)
        
        print(f"\n{emoji} Confiança: {nivel} ({conf:.1%})")
        print(f"   Máximo de risco: {percentual}% do bankroll")
        print(f"   Aposta recomendada: R$ {aposta:.2f}")

# ============================================================================
# EXEMPLO 7: FLUXO COMPLETO DE UM SINAL
# ============================================================================

def exemplo_fluxo_completo():
    """Demonstra o fluxo completo desde geração até resultado"""
    
    print("\n" + "="*60)
    print("FLUXO COMPLETO DE UM SINAL")
    print("="*60)
    
    fluxo = [
        {
            "etapa": "[1] GERAÇÃO",
            "acao": "Coleta 100 jogadas de Crash",
            "status": "✅"
        },
        {
            "etapa": "[2] ANÁLISE",
            "acao": "Analisa padrões estatísticos",
            "status": "✅"
        },
        {
            "etapa": "[3] PIPELINE",
            "acao": "Passa por 6 estratégias de validação",
            "status": "✅"
        },
        {
            "etapa": "[4] KELLY",
            "acao": "Calcula tamanho ideal da aposta",
            "status": "✅"
        },
        {
            "etapa": "[5] PERSISTÊNCIA",
            "acao": "Salva sinal completo no banco de dados",
            "status": "✅"
        },
        {
            "etapa": "[6] FORMATAÇÃO",
            "acao": "Formata mensagem customizada por jogo",
            "status": "✅"
        },
        {
            "etapa": "[7] TELEGRAM",
            "acao": "Envia via Telegram em tempo real",
            "status": "✅"
        },
        {
            "etapa": "[8] RASTREAMENTO",
            "acao": "Monitora resultado e atualiza BD",
            "status": "⏳ Em andamento"
        }
    ]
    
    for item in fluxo:
        print(f"\n{item['etapa']} {item['status']}")
        print(f"   Ação: {item['acao']}")

# ============================================================================
# EXEMPLO 8: QUERIES SQL ÚTEIS
# ============================================================================

def exemplo_queries():
    """Exemplos de queries para análise dos sinais"""
    
    print("\n" + "="*60)
    print("QUERIES SQL ÚTEIS")
    print("="*60)
    
    queries = {
        "Últimos 10 sinais": """
SELECT id, game, signal_type, confidence, strategies_passed, 
       timestamp, result 
FROM signals 
ORDER BY timestamp DESC 
LIMIT 10;
        """,
        
        "Taxa de vitória por jogo": """
SELECT 
    game,
    COUNT(*) as total,
    SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END) as wins,
    ROUND(SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END)::float / COUNT(*), 3) as win_rate
FROM signals
WHERE result IS NOT NULL
GROUP BY game;
        """,
        
        "Performance por confiança": """
SELECT 
    ROUND(confidence, 2) as conf_level,
    COUNT(*) as total_signals,
    SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END) as wins,
    ROUND(100.0 * SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END) / COUNT(*), 1) as win_percent
FROM signals
WHERE result IS NOT NULL
GROUP BY ROUND(confidence, 2)
ORDER BY conf_level DESC;
        """,
        
        "Sinais por hora (padrões)": """
SELECT 
    HOUR(timestamp) as hora,
    COUNT(*) as sinais_gerados,
    ROUND(AVG(confidence), 3) as conf_media,
    SUM(CASE WHEN result='WIN' THEN 1 ELSE 0 END) as vitorias,
    SUM(CASE WHEN result='LOSS' THEN 1 ELSE 0 END) as derrotas
FROM signals
WHERE result IS NOT NULL
GROUP BY HOUR(timestamp)
ORDER BY hora;
        """
    }
    
    for nome, query in queries.items():
        print(f"\n{nome}:")
        print(query)

# ============================================================================
# EXEMPLO 9: ESTRUTURA DE METADATA
# ============================================================================

def exemplo_metadata():
    """Mostra a estrutura completa de metadata armazenada"""
    
    print("\n" + "="*60)
    print("ESTRUTURA DE METADATA")
    print("="*60)
    
    metadata_exemplo = {
        "odds": 2.1,                                    # Odd do jogo
        "kelly_fraction": 0.25,                        # Fração de Kelly
        "bankroll": 1000.0,                            # Saldo da conta
        "drawdown_percent": 2.3,                       # % drawdown
        "data_source": "blaze_api",                    # Origem dos dados
        "colors_analyzed": 100,                        # Cores analisadas
        "multiplicador_esperado": "1.5x - 2.5x",     # Para Crash
        "strategies_detalhes": {
            "pattern_detection": {"passed": True, "score": 0.95},
            "technical_validation": {"passed": True, "score": 0.87},
            "confidence_filter": {"passed": True, "score": 0.92},
            "confirmation_filter": {"passed": False, "score": 0.62},
            "monte_carlo": {"passed": False, "score": 0.68},
            "run_test": {"passed": False, "score": 0.71}
        }
    }
    
    import json
    print(json.dumps(metadata_exemplo, indent=2, ensure_ascii=False))

# ============================================================================
# EXEMPLO 10: COMO USAR O SISTEMA
# ============================================================================

def exemplo_uso_sistema():
    """Exemplos de como usar o sistema na prática"""
    
    print("\n" + "="*60)
    print("COMO USAR O SISTEMA")
    print("="*60)
    
    usos = [
        {
            "modo": "Modo Normal",
            "comando": "python src/main.py --scheduled",
            "intervalo": "A cada 2 minutos",
            "uso": "Operação contínua"
        },
        {
            "modo": "Modo Contínuo",
            "comando": "python src/main.py --scheduled --interval 1",
            "intervalo": "A cada 1 minuto",
            "uso": "Coleta mais frequente"
        },
        {
            "modo": "Modo Teste",
            "comando": "python src/main.py --test",
            "intervalo": "Uma execução",
            "uso": "Validação de sistema"
        }
    ]
    
    for uso in usos:
        print(f"\n{uso['modo']}:")
        print(f"   Comando: {uso['comando']}")
        print(f"   Intervalo: {uso['intervalo']}")
        print(f"   Uso: {uso['uso']}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "EXEMPLOS PRÁTICOS DO NOVO SISTEMA" + " "*10 + "║")
    print("╚" + "="*58 + "╝")
    
    # Executar exemplos
    exemplos_formatacao()
    exemplo_recomendacoes()
    exemplo_fluxo_completo()
    exemplo_queries()
    exemplo_metadata()
    exemplo_uso_sistema()
    
    print("\n" + "="*60)
    print("FIM DOS EXEMPLOS")
    print("="*60 + "\n")
    
    print("✅ Sistema completo e funcional!")
    print("✅ Sinais sendo entregues com qualidade")
    print("✅ Dados persistidos no banco de dados")
    print("✅ Pronto para análise e backtesting")
