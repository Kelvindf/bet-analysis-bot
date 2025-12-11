# Script de Instalação - Scraper Realtime Blaze
# ===============================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " INSTALAÇÃO: Blaze Realtime Scraper" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Python
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Python não encontrado!" -ForegroundColor Red
    Write-Host "  Instale Python em https://python.org" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/5] Instalando Selenium..." -ForegroundColor Yellow
pip install selenium --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Selenium instalado" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Erro ao instalar Selenium" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/5] Instalando WebDriver Manager..." -ForegroundColor Yellow
pip install webdriver-manager --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ WebDriver Manager instalado" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Erro ao instalar WebDriver Manager" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/5] Instalando WebSocket Client..." -ForegroundColor Yellow
pip install websocket-client --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ WebSocket Client instalado" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Erro ao instalar WebSocket Client" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/5] Verificando instalação..." -ForegroundColor Yellow
python -c "import selenium; import webdriver_manager; import websocket; print('✅ Todos os pacotes importados com sucesso')" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Instalação concluída!" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Alguns pacotes podem não ter sido instalados corretamente" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host " PROXIMOS PASSOS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Testar scraper:" -ForegroundColor White
Write-Host "   python src/data_collection/blaze_realtime_scraper.py" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Verificar dados capturados:" -ForegroundColor White
Write-Host "   dir data\realtime\" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Integrar no sistema principal (ver GUIA_COLETA_DADOS_REAIS.md)" -ForegroundColor White
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
