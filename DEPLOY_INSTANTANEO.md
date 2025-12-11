# 🚀 DEPLOY INSTANTÂNEO COM HEROKU (5 MINUTOS)

## Opção Mais Rápida - Deploy com Git!

### Passo 1: Instalar Heroku CLI

**No PowerShell (como Administrador)**:
```powershell
Invoke-WebRequest -Uri https://cli-assets.heroku.com/install-get-heroku.ps1 -OutFile install-heroku.ps1
.\install-heroku.ps1
```

OU baixe direto: https://devcenter.heroku.com/articles/heroku-cli

### Passo 2: Login no Heroku

```powershell
cd C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2
heroku login
```

Vai abrir o navegador para você fazer login/criar conta.

### Passo 3: Criar App e Deploy

```powershell
# Criar app
heroku create bet-analysis-$(Get-Random)

# Adicionar PostgreSQL (grátis)
heroku addons:create heroku-postgresql:essential-0

# Configurar variáveis
heroku config:set TELEGRAM_BOT_TOKEN="8260416435:AAH7aPa8eL8bYG0051IPyulUXqmaetFxrzQ"
heroku config:set TELEGRAM_CHANNEL_ID="8329919168"
heroku config:set KELLY_BANKROLL="1000.0"
heroku config:set KELLY_FRACTION="0.25"
heroku config:set MAX_DRAWDOWN_PERCENT="5.0"

# Inicializar Git (se ainda não fez)
git init
git add .
git commit -m "Deploy inicial"

# Deploy!
git push heroku main

# Escalar para rodar 24/7
heroku ps:scale worker=1

# Ver logs ao vivo
heroku logs --tail
```

### ✅ PRONTO! Rodando 24/7!

**Custo**: $7-25/mês (mais fácil que DigitalOcean)

**Ver status**:
```powershell
heroku ps
```

**Parar**:
```powershell
heroku ps:scale worker=0
```

**Reiniciar**:
```powershell
heroku restart
```

---

## 🎯 QUAL ESCOLHER?

### Heroku (RECOMENDO AGORA)
✅ Deploy com git push (1 comando)
✅ Sem SSH, sem servidor
✅ PostgreSQL incluído grátis
✅ 5 minutos total
⚠️ $7-25/mês

### DigitalOcean
✅ Mais barato ($12/mês)
✅ Mais controle
⚠️ Precisa SSH e configuração manual
⚠️ 10-15 minutos

---

## Execute Agora os Comandos Acima!

Copie e cole um por um no PowerShell.
