#!/bin/bash
#
# Script de Monitoramento e Correção Automática de Bugs
# Executa verificações periódicas e corrige problemas automaticamente
#
# Uso:
#   chmod +x fix_and_monitor.sh
#   ./fix_and_monitor.sh
#

set -e

PROJECT_DIR="/opt/bet_analysis_platform"
LOG_FILE="$PROJECT_DIR/logs/monitor.log"
ERROR_LOG="$PROJECT_DIR/logs/errors.log"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$ERROR_LOG"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

echo "=========================================="
echo "🔧 BET ANALYSIS - CORREÇÃO DE BUGS"
echo "=========================================="
echo ""

cd "$PROJECT_DIR" || exit 1

# 1. Verificar se o serviço está rodando
log "Verificando status do serviço..."
if ! systemctl is-active --quiet bet-analysis; then
    log_error "Serviço parado! Tentando reiniciar..."
    systemctl restart bet-analysis
    sleep 5
    if systemctl is-active --quiet bet-analysis; then
        log "✅ Serviço reiniciado com sucesso"
    else
        log_error "❌ Falha ao reiniciar serviço"
        journalctl -u bet-analysis -n 50 --no-pager | tee -a "$ERROR_LOG"
    fi
else
    log "✅ Serviço está rodando"
fi

# 2. Verificar uso de memória
log "Verificando uso de memória..."
MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
MEM_USAGE_INT=${MEM_USAGE%.*}
if [ "$MEM_USAGE_INT" -gt 90 ]; then
    log_warning "⚠️  Uso de memória alto: ${MEM_USAGE}%"
    log "Reiniciando serviço para liberar memória..."
    systemctl restart bet-analysis
else
    log "✅ Uso de memória OK: ${MEM_USAGE}%"
fi

# 3. Verificar espaço em disco
log "Verificando espaço em disco..."
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 85 ]; then
    log_warning "⚠️  Espaço em disco baixo: ${DISK_USAGE}%"
    log "Limpando logs antigos..."
    find "$PROJECT_DIR/logs" -name "*.log" -mtime +7 -delete
    find "$PROJECT_DIR/data" -name "*.old" -delete
    journalctl --vacuum-time=7d
    log "✅ Limpeza concluída"
else
    log "✅ Espaço em disco OK: ${DISK_USAGE}%"
fi

# 4. Verificar dependências Python
log "Verificando dependências Python..."
source venv/bin/activate
if pip check > /dev/null 2>&1; then
    log "✅ Dependências Python OK"
else
    log_warning "⚠️  Problemas nas dependências detectados"
    log "Reinstalando dependências..."
    pip install -r requirements.txt --upgrade --quiet
    log "✅ Dependências atualizadas"
fi

# 5. Verificar banco de dados PostgreSQL
log "Verificando banco de dados..."
if systemctl is-active --quiet postgresql; then
    log "✅ PostgreSQL está rodando"
    
    # Testar conexão
    if sudo -u postgres psql -c '\l' > /dev/null 2>&1; then
        log "✅ Conexão com PostgreSQL OK"
    else
        log_error "❌ Falha ao conectar com PostgreSQL"
        systemctl restart postgresql
        sleep 3
    fi
else
    log_error "PostgreSQL parado! Iniciando..."
    systemctl start postgresql
    sleep 3
fi

# 6. Verificar logs de erro recentes
log "Analisando logs de erro..."
ERROR_COUNT=$(journalctl -u bet-analysis --since "1 hour ago" | grep -ci "error" || echo "0")
if [ "$ERROR_COUNT" -gt 10 ]; then
    log_warning "⚠️  ${ERROR_COUNT} erros detectados na última hora"
    log "Últimos erros:"
    journalctl -u bet-analysis --since "1 hour ago" | grep -i "error" | tail -5 | tee -a "$ERROR_LOG"
else
    log "✅ Nível de erros aceitável: ${ERROR_COUNT} erros na última hora"
fi

# 7. Verificar conectividade com APIs
log "Verificando conectividade com APIs externas..."
if curl -s --connect-timeout 5 https://api.blaze.com > /dev/null 2>&1; then
    log "✅ Conexão com Blaze API OK"
else
    log_warning "⚠️  Falha ao conectar com Blaze API"
fi

if curl -s --connect-timeout 5 https://api.telegram.org > /dev/null 2>&1; then
    log "✅ Conexão com Telegram API OK"
else
    log_warning "⚠️  Falha ao conectar com Telegram API"
fi

# 8. Verificar arquivos críticos
log "Verificando arquivos críticos..."
CRITICAL_FILES=(
    "src/main.py"
    ".env"
    "requirements.txt"
    "src/learning/feedback_loop.py"
    "src/learning/ab_test.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        log "✅ $file existe"
    else
        log_error "❌ $file não encontrado!"
    fi
done

# 9. Limpar arquivos temporários
log "Limpando arquivos temporários..."
find "$PROJECT_DIR" -name "*.pyc" -delete
find "$PROJECT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
log "✅ Limpeza de temporários concluída"

# 10. Verificar processos Python órfãos
log "Verificando processos órfãos..."
ORPHAN_COUNT=$(ps aux | grep "[p]ython.*main.py" | grep -v "systemd" | wc -l)
if [ "$ORPHAN_COUNT" -gt 1 ]; then
    log_warning "⚠️  Processos órfãos detectados: $ORPHAN_COUNT"
    log "Limpando processos órfãos..."
    ps aux | grep "[p]ython.*main.py" | grep -v "systemd" | awk '{print $2}' | xargs -r kill -9
    systemctl restart bet-analysis
else
    log "✅ Nenhum processo órfão detectado"
fi

# 11. Backup automático
log "Realizando backup..."
BACKUP_DIR="/root/backups"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/auto-backup-$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$BACKUP_FILE" \
    "$PROJECT_DIR/data" \
    "$PROJECT_DIR/logs" \
    "$PROJECT_DIR/.env" \
    2>/dev/null || log_warning "⚠️  Backup parcial realizado"
log "✅ Backup salvo: $BACKUP_FILE"

# Manter apenas os últimos 3 backups automáticos
ls -t "$BACKUP_DIR"/auto-backup-*.tar.gz | tail -n +4 | xargs -r rm
log "✅ Backups antigos removidos"

# 12. Estatísticas do sistema
log "Coletando estatísticas..."
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
UPTIME=$(uptime -p)
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}')

echo ""
log_info "📊 Estatísticas do Sistema:"
log_info "   CPU: ${CPU_USAGE}%"
log_info "   RAM: ${MEM_USAGE}%"
log_info "   Disco: ${DISK_USAGE}%"
log_info "   Uptime: ${UPTIME}"
log_info "   Load Average:${LOAD_AVG}"

# 13. Verificar atualizações disponíveis
log "Verificando atualizações do sistema..."
UPDATE_COUNT=$(apt list --upgradable 2>/dev/null | grep -c "upgradable" || echo "0")
if [ "$UPDATE_COUNT" -gt 50 ]; then
    log_warning "⚠️  $UPDATE_COUNT atualizações disponíveis"
    log_info "Execute: apt update && apt upgrade"
else
    log "✅ Sistema atualizado ($UPDATE_COUNT atualizações disponíveis)"
fi

# 14. Relatório final
echo ""
echo "=========================================="
echo "✅ VERIFICAÇÃO CONCLUÍDA"
echo "=========================================="
echo ""
log_info "📄 Logs salvos em:"
log_info "   Monitor: $LOG_FILE"
log_info "   Erros: $ERROR_LOG"
echo ""
log_info "🔄 Próxima execução: Configure no crontab"
log_info "   Exemplo: */30 * * * * $PROJECT_DIR/fix_and_monitor.sh"
echo ""

# 15. Enviar notificação via Telegram (opcional)
if [ -f ".env" ]; then
    source .env
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHANNEL_ID" ]; then
        MESSAGE="🤖 *Monitor Automático*%0A%0A✅ Sistema verificado%0A📊 CPU: ${CPU_USAGE}%%0A💾 RAM: ${MEM_USAGE}%%0A💿 Disco: ${DISK_USAGE}%%0A🔧 Erros/hora: ${ERROR_COUNT}%0A%0A_$(date +'%Y-%m-%d %H:%M:%S')_"
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHANNEL_ID}" \
            -d "text=${MESSAGE}" \
            -d "parse_mode=Markdown" > /dev/null 2>&1 || true
    fi
fi

log "🎉 Monitoramento concluído com sucesso!"
