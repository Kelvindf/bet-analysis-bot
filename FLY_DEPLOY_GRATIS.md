# Deploy 100% Grátis com Fly.io (sem cartão)

Fly.io oferece VMs gratuitas suficientes para rodar um worker leve 24/7. Não precisa cartão.

## Pré-requisitos
- Conta Fly.io: https://fly.io
- Fly CLI (Windows): https://fly.io/docs/hands-on/installing/

## Passo a passo

### 1. Login
```powershell
fly auth signup   # criar conta
fly auth login    # login
```

### 2. Criar app
```powershell
cd c:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2
fly apps create bet-analysis-bot
```

### 3. Configurar secrets (token do Telegram)
```powershell
fly secrets set TELEGRAM_BOT_TOKEN=8260416435:AAH7aPa8eL8bYG0051IPyulUXqmaetFxrzQ
```

### 4. Deploy
```powershell
fly deploy --remote-only
```

### 5. Escalar como worker
```powershell
fly scale count 1 --process worker
```

### 6. Logs
```powershell
fly logs
```

## Arquivo de configuração
- `fly.toml` já criado com:
  - Processo `worker`: `python src/main.py --scheduled --interval 1`
  - Variáveis default: `PYTHONUNBUFFERED`, `KELLY_*`, `MAX_DRAWDOWN_PERCENT`, `TELEGRAM_CHANNEL_ID`

## Observações
- Free tier: VMs pequenas (aprox. 1 shared CPU, 256–512MB RAM)
- Se a região `gig` (Guarulhos) não estiver disponível, use `sjc`, `mia`, ou `dfw`.
- Se pedir verificação adicional, é apenas email; não há cobrança.

## Troubleshooting
- Build falhou: ver `Dockerfile` e `requirements.txt`
- Sem logs: ver `fly apps list` e `fly status`
- Bot não envia: checar `TELEGRAM_BOT_TOKEN` e acesso ao canal 8329919168

## Atualizações
```powershell
git add .
git commit -m "Atualizacao"
git push
fly deploy --remote-only
```
