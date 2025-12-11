# 🔴 MODO 24/7 - GUIA COMPLETO

## O QUE É?

Sistema que coleta dados e envia sinais **continuamente** sem parar, 24 horas por dia.

---

## 🚀 3 FORMAS DE USAR

### OPÇÃO 1: Rodar INDEFINIDAMENTE (24/7 Contínuo)

```powershell
cd 'C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2'
python scripts\modo_24_7.py
```

**O que acontece:**
- Sistema roda continuamente
- Coleta dados a cada 30 segundos
- Envia sinais via Telegram (quando encontra)
- Para quando você pressiona **Ctrl+C**

**Tempo:** ⏳ Indefinido (até você parar)

---

### OPÇÃO 2: Rodar por Tempo Definido

```powershell
# Rodar por 48 horas (2 dias)
python scripts\modo_24_7.py --duration 48

# Rodar por 24 horas (1 dia)
python scripts\modo_24_7.py --duration 24

# Rodar por 1 hora (teste)
python scripts\modo_24_7.py --duration 1
```

**O que acontece:**
- Sistema roda pelo tempo especificado
- Para automaticamente quando tempo acabar
- Envia relatório final ao Telegram

**Tempo:** ⏰ Exatamente N horas depois

---

### OPÇÃO 3: Com Intervalo Customizado

```powershell
# Coletar a cada 10 segundos (mais agressivo)
python scripts\modo_24_7.py --interval 10

# Coletar a cada 60 segundos (mais leve)
python scripts\modo_24_7.py --interval 60

# 48h com intervalo de 15s
python scripts\modo_24_7.py --duration 48 --interval 15
```

**Intervalo recomendado:** 30-60 segundos

---

## 📊 O QUE O SISTEMA FAZ

```
┌─────────────────────────────────────┐
│ INICIALIZAÇÃO                       │
│ ✅ Carregar configurações           │
│ ✅ Conectar ao Telegram             │
│ ✅ Preparar pipeline de 6 estratégias│
└──────────────┬──────────────────────┘
               │
       ┌───────▼────────┐
       │ LOOP CONTÍNUO   │
       └───────┬────────┘
               │
    ┌──────────▼──────────┐
    │ A CADA 30 SEGUNDOS: │
    ├─────────────────────┤
    │ 1. Coletar dados    │
    │    da Blaze         │
    │ 2. Analisar padrões │
    │ 3. Processar 6      │
    │    estratégias      │
    │ 4. Gerar sinais     │
    │ 5. Enviar via       │
    │    Telegram         │
    │ 6. Salvar logs      │
    └──────────┬──────────┘
               │
        ┌──────▼──────┐
        │ FINALIZAÇÃO │
        │ (Ctrl+C)    │
        │ • Relatório │
        │ • Estatísticas
        │ • Notif.Telegram
        └─────────────┘
```

---

## 📈 EXEMPLO DE EXECUÇÃO

```
C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2> python scripts\modo_24_7.py
================================================================================
SISTEMA 24/7 INICIALIZADO
================================================================================
Início: 2025-12-05 20:30:45.123456
Status: AGUARDANDO CONFIGURAÇÃO
================================================================================
✅ Sistema configurado para rodar INDEFINIDAMENTE (24/7)
   Pressione Ctrl+C para parar

================================================================================
🚀 INICIANDO SISTEMA 24/7
================================================================================

[CICLO 1] Iniciando análise...
2025-12-05 20:30:45 - [INFO] - [*] Iniciando ciclo de analise com Pipeline (6 estratégias)
2025-12-05 20:30:46 - [INFO] - [*] Coletando dados...
2025-12-05 20:30:47 - [INFO] - [*] Analisando padroes...
2025-12-05 20:30:47 - [INFO] - [*] Gerando sinais com Pipeline (6 estratégias)...
2025-12-05 20:30:48 - [INFO] - [✅] 2 sinais válidos encontrados!
2025-12-05 20:30:48 - [INFO] - [*] Enviando 2 sinal(is) válido(s) para Telegram...
2025-12-05 20:30:49 - [INFO] - [OK] Ciclo de analise concluido com sucesso
[CICLO 1] ✅ Concluído com sucesso
Aguardando 30s até próximo ciclo...

[CICLO 2] Iniciando análise...
...
```

---

## 🛑 COMO PARAR O SISTEMA

### Opção 1: Pressionar Ctrl+C
```
[CICLO 45] Iniciando análise...
...
^C
⏹️  Interrupção do usuário detectada

================================================================================
📋 RELATÓRIO FINAL
================================================================================
Tempo total de execução: 23h 45m
Total de ciclos: 1425
Sinais processados: 1425
Sinais enviados: 28
Taxa de conversão: 1.96%
Erros encontrados: 2
================================================================================

✅ Sistema finalizado com sucesso
```

### Opção 2: Fechar Terminal
- Fechando a janela PowerShell também para o sistema

### Opção 3: Usar Task Manager
```
Ctrl+Shift+Esc → Encontrar python → Finalizar processo
```

---

## 📱 NOTIFICAÇÕES TELEGRAM

O sistema envia automaticamente:

### Ao Iniciar
```
✅ Sistema 24/7 iniciado
Hora: 2025-12-05 20:30:45
Pressione Ctrl+C para parar
```

### Quando Encontra Sinal
```
🎯 SINAL GERADO!
Tipo: RED
Confiança: 99.5%
Hora: 2025-12-05 20:31:12
```

### Ao Finalizar
```
📋 SISTEMA 24/7 FINALIZADO

⏱️ Tempo total: 48h 15m
🔄 Ciclos: 5760
📊 Sinais: 115/5760
📈 Taxa de conversão: 2.0%
⚠️ Erros: 3

Fim: 2025-12-05 22:30:45
```

### Em Caso de Erro
```
⚠️ ERRO no sistema 24/7:
[Descrição do erro]
```

---

## 📊 MONITORAMENTO EM TEMPO REAL

Enquanto o sistema roda, você pode acompanhar:

### Ver Últimas Linhas do Log
```powershell
# PowerShell 5.1
Get-Content logs\modo_24_7.log -Tail 20 -Wait

# PowerShell 7+
tail -f logs\modo_24_7.log
```

### Ver Cache de Dados
```powershell
python -c "import json; cache = json.load(open('data/raw/blaze_data_cache.json')); print(f'Double: {len(cache[\"double\"])}, Crash: {len(cache[\"crash\"])}')"
```

### Status do Telegram
```powershell
python scripts\dashboard_monitoramento.py
```

---

## ⚙️ CONFIGURAÇÕES RECOMENDADAS

### Para Máquina Pessoal
```powershell
python scripts\modo_24_7.py --duration 24 --interval 30
```
- Roda 1 dia com intervalo confortável

### Para Server/VPS
```powershell
python scripts\modo_24_7.py --interval 15
```
- Roda indefinidamente com coleta mais agressiva

### Para Teste Rápido
```powershell
python scripts\modo_24_7.py --duration 1 --interval 10
```
- Roda 1 hora com intervalo de 10s

---

## 🔧 TROUBLESHOOTING

### Sistema para inesperadamente?
```powershell
# Verificar último erro
Get-Content logs\modo_24_7.log | Select-Object -Last 50
```

### Telegram não recebe notificações?
```powershell
# Verificar token
python -c "import os; print(os.getenv('TELEGRAM_BOT_TOKEN'))"

# Testar conexão
python scripts\diagnostico_conexoes.py
```

### Usar muita CPU/Memória?
```powershell
# Aumentar intervalo entre ciclos
python scripts\modo_24_7.py --interval 60
```

### Dados não estão sendo salvos?
```powershell
# Verificar permissões
ls -la data/raw/
ls -la logs/
```

---

## 📈 MÉTRICAS ESPERADAS

Após 24 horas:

| Métrica | Esperado |
|---------|----------|
| Ciclos | ~2880 |
| Sinais processados | ~2880 |
| Sinais enviados | 50-100 |
| Taxa de conversão | 1.5-3.5% |
| Erros | 0-5 |
| Taxa de uptime | 99%+ |

---

## 💾 ARQUIVOS GERADOS

O sistema cria/atualiza:

```
logs/modo_24_7.log
├─ Log detalhado de cada ciclo
├─ Erros e warnings
└─ Resumo de execução

data/raw/blaze_data_cache.json
├─ Cache atualizado continuamente
├─ Histórico de cores
└─ Timestamps de coleta
```

---

## 🎯 EXEMPLO: Rodar 48 Horas

**Melhor forma:**

```powershell
# 1. Abrir terminal
cd 'C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2'

# 2. Iniciar sistema (vai rodar 48h automático)
python scripts\modo_24_7.py --duration 48

# 3. Em outro terminal, monitorar (opcional)
Get-Content logs\modo_24_7.log -Tail 20 -Wait
```

**Resultado esperado:**
- 2880 ciclos executados
- 50-100 sinais gerados
- Relatório automático ao Telegram
- Sistema para automaticamente após 48h

---

## 🚨 IMPORTANTE

### Deixar Rodando em Background (Windows)

Se você fechar o PowerShell, o sistema para. Para deixar rodando:

**Opção 1: Task Scheduler (Recomendado)**
```powershell
# Criar tarefa agendada
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2\scripts\modo_24_7.py"
Register-ScheduledTask -TaskName "Modo247" -Trigger $trigger -Principal $principal -Action $action
```

**Opção 2: Detached Process**
```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\...'; python scripts\modo_24_7.py"
```

**Opção 3: Screen/Tmux (em Linux/WSL)**
```bash
screen -S modo247 -d -m python scripts/modo_24_7.py
```

---

## ✅ CHECKLIST ANTES DE INICIAR

- [ ] Python instalado e testado
- [ ] Virtual environment ativo
- [ ] Telegram bot token configurado
- [ ] Blaze API acessível
- [ ] Espaço em disco disponível (mínimo 100MB)
- [ ] Conexão de internet estável
- [ ] Log criado e acessível

---

## 🎯 COMECE AGORA!

**Comando mais simples:**

```powershell
python scripts\modo_24_7.py
```

**Pronto! O sistema está rodando 24/7!**

---

**Sistema 24/7 - Pronto para produção! 🚀**
