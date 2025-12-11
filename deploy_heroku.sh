#!/bin/bash
# Heroku Deploy - Deploy com 1 comando!

# 1. Instalar Heroku CLI
# Windows: https://devcenter.heroku.com/articles/heroku-cli
# Ou via PowerShell:
# Invoke-WebRequest -Uri https://cli-assets.heroku.com/install-get-heroku.ps1 -OutFile install-heroku.ps1
# .\install-heroku.ps1

# 2. Login
heroku login

# 3. Criar app
heroku create bet-analysis-bot-$(date +%s)

# 4. Adicionar PostgreSQL
heroku addons:create heroku-postgresql:mini

# 5. Configurar variáveis
heroku config:set TELEGRAM_BOT_TOKEN="8260416435:AAH7aPa8eL8bYG0051IPyulUXqmaetFxrzQ"
heroku config:set TELEGRAM_CHANNEL_ID="8329919168"
heroku config:set KELLY_BANKROLL="1000.0"
heroku config:set KELLY_FRACTION="0.25"
heroku config:set MAX_DRAWDOWN_PERCENT="5.0"

# 6. Deploy
git init
git add .
git commit -m "Initial deploy"
git push heroku main

# 7. Escalar para rodar 24/7
heroku ps:scale worker=1

# 8. Ver logs
heroku logs --tail

echo "✅ Deploy concluído! App rodando 24/7"
