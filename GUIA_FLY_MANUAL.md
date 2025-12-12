# 🚀 DEPLOY FLY.IO - GUIA MANUAL (SE SCOOP FALHAR)

## Instalação Rápida (Windows)

### Opção A: Chocolatey (Recomendado)
```powershell
choco install flyctl
```

### Opção B: Scoop
```powershell
scoop install flyctl
```

### Opção C: Download Direto
1. Acesse: https://github.com/superfly/flyctl/releases
2. Baixe: `flyctl_windows_amd64.zip`
3. Extraia para: `C:\Program Files\flyctl`
4. Adicione ao PATH:
   - Win+Pause → Variáveis de Ambiente
   - PATH → Editar
   - Adicione: `C:\Program Files\flyctl`
   - Reinicie PowerShell

### Verificar
```powershell
flyctl version
```

---

## Deploy Passo a Passo

Após instalar flyctl, execute:

```powershell
cd C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2

# [1] Login/Signup
flyctl auth login

# [2] Criar app
flyctl apps create bet-analysis-bot

# [3] Setar token do Telegram
flyctl secrets set TELEGRAM_BOT_TOKEN=8260416435:AAH7aPa8eL8bYG0051IPyulUXqmaetFxrzQ --app bet-analysis-bot

# [4] Deploy (isso vai levar 2-5 minutos)
flyctl deploy --remote-only --app bet-analysis-bot

# [5] Escalar worker
flyctl scale count 1 --app bet-analysis-bot

# [6] Ver logs
flyctl logs --app bet-analysis-bot
```

---

## Ou Execute o Script Automatico

Depois que flyctl estiver instalado:

```powershell
cd C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2
powershell -ExecutionPolicy Bypass -File deploy_fly_auto.ps1
```

---

## Esperado

- **Build**: ~2 minutos (Python install, pip install)
- **Execução**: Inicia automaticamente
- **Telegram**: Sinais aparecem no canal 8329919168 a cada minuto
- **Logs**: `flyctl logs --app bet-analysis-bot` mostra tudo em tempo real

---

## Custos

- **Fly.io Free Tier**: 
  - 3 VMs compartilhadas gratuitas
  - 160 GB transfer/mês
  - Suficiente para um worker Python leve rodando 24/7
  
- **Seu Bot**: 
  - Usando 1 VM (worker processo)
  - ~10 MB transfer/mês
  - **CUSTO: $0.00**

---

## Troubleshooting

### "flyctl: O termo não é reconhecido"
- Flyctl não está no PATH
- Solução: Reinicie PowerShell **como admin** após instalar

### "Build failed"
- Ver erro em `flyctl logs`
- Comum: falta dependência em `requirements.txt`
- Solução: `git add requirements.txt && git push` → rebuild automático

### "Bot não envia sinais"
- Verificar: `flyctl logs` para erros
- Verificar: token Telegram em `flyctl secrets list`
- Verificar: canal Telegram 8329919168 existe e bot é admin

### "Help, nada funciona"
- Redeploy: `flyctl deploy --remote-only --app bet-analysis-bot`
- Reiniciar: `flyctl restart --app bet-analysis-bot`
- Destruir e recriar: `flyctl apps destroy bet-analysis-bot` (depois `create` novamente)

---

## Próximas Atualizações

```powershell
# Editar código local
git add .
git commit -m "Mudanca"
git push

# Redeploy automático (ou manual)
flyctl deploy --remote-only --app bet-analysis-bot
```
