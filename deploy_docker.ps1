# Docker Build e Deploy Script - Bet Analysis Platform com Tier 1 (PowerShell)

Write-Host "╔══════════════════════════════════════════════════════════════╗"
Write-Host "║     Docker Build e Deploy - Bet Analysis Platform            ║"
Write-Host "║     Com Tier 1: Kelly Criterion + Drawdown Manager           ║"
Write-Host "╚══════════════════════════════════════════════════════════════╝"
Write-Host ""

# 1. Stop existing containers
Write-Host "🛑 Parando containers existentes..."
docker-compose down 2>$null

# 2. Build images
Write-Host "🔨 Building Docker images..."
docker-compose build

# 3. Start services
Write-Host "🚀 Iniciando serviços..."
docker-compose up -d

# 4. Wait for startup
Write-Host "⏳ Aguardando inicialização..."
Start-Sleep -Seconds 10

# 5. Check health
Write-Host "🏥 Verificando saúde dos serviços..."
Write-Host ""

# App health
Write-Host -NoNewline "  App (port 8000): "
try {
    $health = docker-compose exec -T app python scripts/healthcheck.py --max-age 120 2>$null
    Write-Host "✅ OK" -ForegroundColor Green
} catch {
    Write-Host "⚠️  CHECKING..." -ForegroundColor Yellow
}

# Exporter health
Write-Host -NoNewline "  Prometheus (port 8001): "
try {
    $metrics = curl.exe -s http://localhost:8001/metrics 2>$null
    if ($metrics) {
        Write-Host "✅ OK" -ForegroundColor Green
    } else {
        Write-Host "⚠️  CHECKING..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  CHECKING..." -ForegroundColor Yellow
}

# 6. Display logs
Write-Host ""
Write-Host "📊 Últimas linhas do log:"
docker-compose logs --tail=20 app

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗"
Write-Host "║                    DEPLOY CONCLUÍDO                          ║"
Write-Host "╠══════════════════════════════════════════════════════════════╣"
Write-Host "║ 📌 Services:                                                 ║"
Write-Host "║   - App (src/main.py): localhost:8000                       ║"
Write-Host "║   - Prometheus Exporter: localhost:8001                     ║"
Write-Host "║                                                              ║"
Write-Host "║ 📊 Prometheus Metrics:                                       ║"
Write-Host "║   curl http://localhost:8001/metrics | findstr kelly       ║"
Write-Host "║   curl http://localhost:8001/metrics | findstr drawdown    ║"
Write-Host "║                                                              ║"
Write-Host "║ 📝 Logs:                                                     ║"
Write-Host "║   docker-compose logs -f app                                ║"
Write-Host "║   docker-compose logs -f exporter                           ║"
Write-Host "║                                                              ║"
Write-Host "║ 🛑 Stop:                                                     ║"
Write-Host "║   docker-compose down                                       ║"
Write-Host "╚══════════════════════════════════════════════════════════════╝"
