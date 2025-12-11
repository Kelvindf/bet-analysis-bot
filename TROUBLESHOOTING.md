# 🔧 Troubleshooting - Soluções para Problemas

## Problema 1: "Chat not found" no Telegram

### Sintoma
```
[ERRO] Erro ao enviar para Telegram: Chat not found
[*] Total de sinais enviados: 0/1
```

### Causa
O ID do Telegram `770356893` pode estar incorreto ou o bot não reconhece o chat.

### Solução

**Passo 1:** Descobrir seu ID correto
```powershell
.\venv\Scripts\python.exe get_chat_id.py
```

**Passo 2:** No Telegram
1. Procure por seu bot (pelo nome ou username)
2. Se não encontrar, você pode:
   - Procure por `@BotFather`
   - Digite `/mybots`
   - Clique em seu bot
   - Veja o username
3. Adicione seu bot aos contatos
4. Envie `/start`
5. Envie qualquer mensagem (ex: "olá")

**Passo 3:** Volte ao PowerShell
- O script `get_chat_id.py` deve mostrar seu ID
- Copie este ID

**Passo 4:** Atualize `.env`
```properties
TELEGRAM_CHANNEL_ID=seu_id_aqui
```

**Passo 5:** Teste de novo
```powershell
.\venv\Scripts\python.exe src/main.py
```

---

## Problema 2: "ModuleNotFoundError"

### Sintoma
```
ModuleNotFoundError: No module named 'src'
```

### Causa
Executado do diretório errado ou Python path não configurado.

### Solução

**Certifique-se de estar no diretório correto:**
```powershell
cd c:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2
.\venv\Scripts\python.exe src/main.py
```

**Não use:**
```powershell
python src/main.py  # ❌ Usa Python do sistema
cd src
python main.py      # ❌ Perde o path
```

---

## Problema 3: "UnicodeEncodeError" (Emojis)

### Sintoma
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705'
```

### Causa
Windows PowerShell não suporta Unicode (emojis) nativamente.

### Solução

**Opção 1:** Usar Python com UTF-8 (recomendado)
```powershell
$env:PYTHONIOENCODING="utf-8"
.\venv\Scripts\python.exe src/main.py
```

**Opção 2:** Usar Windows Terminal (melhor)
- Windows Terminal suporta Unicode nativamente
- Baixe em: Microsoft Store → "Windows Terminal"
- Use PowerShell nele

**Opção 3:** Remover emojis (já foi feito)
- Os emojis foram removidos do código
- Use `[OK]`, `[ERRO]` no lugar

---

## Problema 4: "No data coletado"

### Sintoma
```
[OK] Crash: 0 registros coletados
[OK] Double: 20 registros coletados
```

### Causa
Crash endpoint pode estar offline ou URL incorreta.

### Solução

**Verificar endpoints:**
```powershell
.\venv\Scripts\python.exe test_blaze_api.py
```

**Checar a URL em `.env`:**
```properties
BLAZE_API_URL=https://api.blaze.com
```

**Se o Blaze mudou a API:**
- Veja `ANALISE_INTEGRACAO_API.md`
- Seção "Mapeando Endpoints Reais"

---

## Problema 5: "Nenhum sinal gerado"

### Sintoma
```
[*] Nenhum sinal com confianca suficiente gerado
```

### Causa
Os padrões nos dados não atingem 65% de confiança.

### Solução

**Opção 1:** Diminuir requisito de confiança
```properties
MIN_CONFIDENCE_LEVEL=0.50  # Era 0.65
```

**Opção 2:** Coletar mais dados
```python
# Em blaze_client.py, aumente limit
crash_data = self.get_crash_history(limit=200)  # Era 50
```

**Opção 3:** Executar múltiplas vezes
```powershell
.\venv\Scripts\python.exe src/main.py --scheduled --interval 1
# Rodará a cada 1 minuto
```

---

## Problema 6: "Connection timeout"

### Sintoma
```
Erro ao buscar histórico Crash: Connection timeout
```

### Causa
Blaze API está lenta ou indisponível.

### Solução

**Verificar conexão:**
```powershell
Invoke-WebRequest https://api.blaze.com -UseBasicParsing
```

Se retornar 200, a API está online.

**Aguardar e tentar de novo:**
```powershell
Start-Sleep -Seconds 30
.\venv\Scripts\python.exe src/main.py
```

**Aumentar timeout:**
```python
# Em blaze_client.py
response = self.session.get(url, params=params, timeout=30)  # Era 10
```

---

## Problema 7: "PostgreSQL connection error"

### Sintoma
```
ERRO: Erro ao conectar ao banco de dados
```

### Causa
Database não está configurado (banco não é obrigatório ainda).

### Solução

**Opção 1:** Ignorar (recomendado por enquanto)
- A aplicação não depende de DB ainda
- Todos os dados vão para JSON

**Opção 2:** Configurar PostgreSQL
```properties
DATABASE_URL=postgresql://appuser:apppass@localhost:5432/appdb
POSTGRES_USER=appuser
POSTGRES_PASSWORD=apppass
```

Para usar Docker:
```powershell
docker-compose up -d
```

---

## Problema 8: "Variáveis de ambiente não carregadas"

### Sintoma
```
TELEGRAM_BOT_TOKEN não está configurado
```

### Causa
`.env` não está sendo lido ou está no lugar errado.

### Solução

**Verificar localização:**
```powershell
cd c:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2
ls -Name .env  # Deve aparecer .env
```

**Validar valores:**
```powershell
.\venv\Scripts\python.exe .\scripts\validate_telegram_env.py
```

Se não aparecer nada, recreie o `.env`:
```powershell
# Abra o arquivo em um editor e salve novamente
notepad .env
```

---

## Problema 9: "Script não roda em background"

### Sintoma
O programa para quando você fecha o PowerShell.

### Solução

**Opção 1:** Usar Task Scheduler do Windows
```powershell
# Criar tarefa agendada que roda a cada 5 minutos
$action = New-ScheduledTaskAction -Execute "C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2\venv\Scripts\python.exe" -Argument "C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2\src\main.py"
$trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 5) -At (Get-Date) -RepeatIndefinitely
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "BetAnalysis" -Description "Análise de apostas"
```

**Opção 2:** Usar screen/tmux (WSL)
```bash
# No WSL
tmux new-session -d -s bet python src/main.py --scheduled
```

**Opção 3:** Criar BAT que inicia sem janela
```batch
@echo off
cd C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2
start "" venv\Scripts\python.exe src/main.py --scheduled
```

Salve como `rodar_continuo.bat` e clique 2x.

---

## Problema 10: "Altos uso de CPU"

### Sintoma
Python usando 50%+ CPU

### Causa
Loop infinito em `--scheduled` com intervalo muito pequeno.

### Solução

**Aumentar intervalo:**
```powershell
.\venv\Scripts\python.exe src/main.py --scheduled --interval 10
# Rodará a cada 10 minutos
```

**Ou adicionar delay:**
```python
# Em src/main.py, adicione:
time.sleep(5)  # Aguarda 5 segundos entre ciclos
```

---

## 🔍 Checklist de Debug

Antes de qualquer execução:

```
☐ Estou no diretório correto?
  cd c:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2

☐ Virtual environment está ativo?
  .\venv\Scripts\Activate.ps1

☐ Credenciais estão no .env?
  cat .env | grep TELEGRAM

☐ Arquivo .env existe?
  ls .env

☐ Internet está funcionando?
  Test-NetConnection api.blaze.com -Port 443

☐ Bot foi iniciado no Telegram?
  Procure e envie /start para seu bot

☐ Chat ID está correto?
  .\venv\Scripts\python.exe get_chat_id.py
```

---

## 📞 Informações Úteis

**Logs:**
```powershell
# Ver últimas 50 linhas
Get-Content logs/bet_analysis.log -Tail 50

# Seguir em tempo real
Get-Content logs/bet_analysis.log -Wait
```

**Testes:**
```powershell
# Testar Blaze API
.\venv\Scripts\python.exe test_blaze_api.py

# Validar Telegram
.\venv\Scripts\python.exe .\scripts\validate_telegram_env.py

# Obter Chat ID
.\venv\Scripts\python.exe get_chat_id.py
```

**Parar execução:**
```
Ctrl+C
```

---

## 🆘 Se Nada Funcionar

1. Leia `PRONTO_RODAR.md`
2. Verifique `RESUMO_EXECUCAO.md`
3. Execute todos os testes:
   - `validate_telegram_env.py`
   - `get_chat_id.py`
   - `test_blaze_api.py`
4. Veja os logs: `logs/bet_analysis.log`
5. Compare com este documento

---

**Last Updated:** 2025-12-05  
**Status:** ✅ Projeto Funcional  

