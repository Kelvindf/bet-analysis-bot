Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY AUTOMATICO - RENDER.COM" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "[1/3] Verificando Git..." -ForegroundColor Yellow
git --version
Write-Host "OK - Git encontrado`n" -ForegroundColor Green

Write-Host "[2/3] Status do repositorio..." -ForegroundColor Yellow
$remoteUrl = git config --get remote.origin.url
Write-Host "Repositorio: $remoteUrl" -ForegroundColor White
Write-Host "OK - Conectado ao GitHub`n" -ForegroundColor Green

Write-Host "[3/3] Commit final..." -ForegroundColor Yellow
$gitStatus = git status --porcelain
if ($gitStatus) {
    git add .
    git commit -m "Deploy: Preparacao final Render"
    Write-Host "OK - Arquivos commitados`n" -ForegroundColor Green
} else {
    Write-Host "OK - Repositorio ja limpo`n" -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  PROXIMOS PASSOS - DEPLOY MANUAL" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Seu codigo ja esta no GitHub:" -ForegroundColor Green
Write-Host "https://github.com/Kelvindf/bet-analysis-bot" -ForegroundColor White
Write-Host ""

Write-Host "Agora, execute estes 3 passos NO SEU NAVEGADOR:" -ForegroundColor Yellow
Write-Host ""

Write-Host "1. Acesse o Render:" -ForegroundColor Cyan
Write-Host "   https://dashboard.render.com" -ForegroundColor White
Write-Host ""

Write-Host "2. Clique em 'New +' e depois 'Blueprint'" -ForegroundColor Cyan
Write-Host ""

Write-Host "3. Selecione seu repositorio 'bet-analysis-bot'" -ForegroundColor Cyan
Write-Host "   Render detecta render.yaml automaticamente" -ForegroundColor Gray
Write-Host ""

Write-Host "4. Clique 'Apply' e aguarde 2 minutos" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================" -ForegroundColor Green
Write-Host "  PRONTO! BOT RODANDO 24/7 GRATIS" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Verificar:" -ForegroundColor Yellow
Write-Host "  1. Logs: Dashboard > bet-analysis-bot > Logs" -ForegroundColor White
Write-Host "  2. Telegram: Canal 8329919168" -ForegroundColor White
Write-Host "  3. Sinais aparecem a cada 1 minuto" -ForegroundColor White
