#!/bin/bash
# Docker Build e Deploy Script - Bet Analysis Platform com Tier 1

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Docker Build e Deploy - Bet Analysis Platform            ║"
echo "║     Com Tier 1: Kelly Criterion + Drawdown Manager           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 1. Stop existing containers
echo "🛑 Parando containers existentes..."
docker-compose down 2>/dev/null || true

# 2. Build images
echo "🔨 Building Docker images..."
docker-compose build

# 3. Start services
echo "🚀 Iniciando serviços..."
docker-compose up -d

# 4. Wait for startup
echo "⏳ Aguardando inicialização..."
sleep 10

# 5. Check health
echo "🏥 Verificando saúde dos serviços..."
echo ""

# App health
echo -n "  App (port 8000): "
if docker-compose exec -T app python scripts/healthcheck.py --max-age 120 > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "⚠️  CHECKING..."
fi

# Exporter health
echo -n "  Prometheus (port 8001): "
if curl -s http://localhost:8001/metrics > /dev/null 2>&1; then
    echo "✅ OK"
else
    echo "⚠️  CHECKING..."
fi

# 6. Display logs
echo ""
echo "📊 Últimas linhas do log:"
docker-compose logs --tail=20 app

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    DEPLOY CONCLUÍDO                          ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║ 📌 Services:                                                 ║"
echo "║   - App (src/main.py): localhost:8000                       ║"
echo "║   - Prometheus Exporter: localhost:8001                     ║"
echo "║                                                              ║"
echo "║ 📊 Prometheus Metrics:                                       ║"
echo "║   curl http://localhost:8001/metrics | grep kelly           ║"
echo "║   curl http://localhost:8001/metrics | grep drawdown        ║"
echo "║                                                              ║"
echo "║ 📝 Logs:                                                     ║"
echo "║   docker-compose logs -f app                                ║"
echo "║   docker-compose logs -f exporter                           ║"
echo "║                                                              ║"
echo "║ 🛑 Stop:                                                     ║"
echo "║   docker-compose down                                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
