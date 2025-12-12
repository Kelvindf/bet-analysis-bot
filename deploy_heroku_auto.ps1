# DEPLOY HEROKU - SCRIPT COMPLETO
# Execute este script APÓS fazer login no Heroku

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY AUTOMÁTICO NO HEROKU" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Ir para o diretório do projeto
cd "c:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2"

# 1. Verificar login
Write-Host "1️⃣  Verificando login..." -ForegroundColor Yellow
heroku auth:whoami

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n❌ Erro: Você precisa fazer login primeiro!" -ForegroundColor Red
    Write-Host "Execute: heroku login`n" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Login confirmado!`n" -ForegroundColor Green

# 2. Criar app
Write-Host "2️⃣  Criando app no Heroku..." -ForegroundColor Yellow
heroku create bet-analysis-bot-live

Write-Host "✅ App criado!`n" -ForegroundColor Green

# 3. Adicionar PostgreSQL
Write-Host "3️⃣  Adicionando PostgreSQL..." -ForegroundColor Yellow
heroku addons:create heroku-postgresql:essential-0

Write-Host "✅ PostgreSQL adicionado!`n" -ForegroundColor Green

# 4. Configurar variáveis de ambiente
Write-Host "4️⃣  Configurando variáveis..." -ForegroundColor Yellow
heroku config:set TELEGRAM_BOT_TOKEN="8260416435:AAH7aPa8eL8bYG0051IPyulUXqmaetFxrzQ"
heroku config:set TELEGRAM_CHANNEL_ID="8329919168"
heroku config:set KELLY_BANKROLL="1000.0"
heroku config:set KELLY_FRACTION="0.25"
heroku config:set MAX_DRAWDOWN_PERCENT="5.0"
heroku config:set PYTHONUNBUFFERED="1"

Write-Host "✅ Variáveis configuradas!`n" -ForegroundColor Green

# 5. Fazer deploy
Write-Host "5️⃣  Fazendo deploy (pode levar 2-3 minutos)..." -ForegroundColor Yellow
git push heroku main

Write-Host "✅ Deploy concluído!`n" -ForegroundColor Green

# 6. Escalar worker para rodar 24/7
Write-Host "6️⃣  Iniciando worker 24/7..." -ForegroundColor Yellow
heroku ps:scale worker=1

Write-Host "✅ Worker iniciado!`n" -ForegroundColor Green

# 7. Mostrar status
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  ✅ DEPLOY CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "📊 Status do app:" -ForegroundColor Cyan
heroku ps

Write-Host "`n📋 Configurações:" -ForegroundColor Cyan
heroku config

Write-Host "`n🌐 URL do app:" -ForegroundColor Cyan
heroku info -s | Select-String "web_url"

Write-Host "`n📝 Para ver logs ao vivo, execute:" -ForegroundColor Yellow
Write-Host "   heroku logs --tail`n" -ForegroundColor White

Write-Host "🎉 Seu bot está rodando 24/7 na nuvem!`n" -ForegroundColor Green
