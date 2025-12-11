#!/bin/bash
#
# Deploy Script para DigitalOcean (Ubuntu 22.04)
# Este script configura e inicia o projeto automaticamente
#
# Uso:
#   chmod +x deploy_digitalocean.sh
#   ./deploy_digitalocean.sh
#

set -e  # Parar se houver erro

echo "=========================================="
echo "🚀 BET ANALYSIS PLATFORM - DEPLOY 24/7"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função de log
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se é root
if [ "$EUID" -ne 0 ]; then 
    log_error "Execute como root: sudo ./deploy_digitalocean.sh"
    exit 1
fi

log_info "Iniciando deploy..."

# 1. Atualizar sistema
log_info "Atualizando sistema..."
apt update -qq
apt upgrade -y -qq
apt autoremove -y -qq

# 2. Instalar dependências
log_info "Instalando dependências..."
apt install -y -qq \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    git \
    curl \
    wget \
    htop \
    vim \
    ufw \
    postgresql \
    postgresql-contrib \
    build-essential

# 3. Configurar Python
log_info "Configurando Python 3.11..."
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
python3 --version

# 4. Criar diretório do projeto
PROJECT_DIR="/opt/bet_analysis_platform"
log_info "Criando diretório do projeto: $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    log_warning "Diretório já existe. Fazendo backup..."
    mv "$PROJECT_DIR" "${PROJECT_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 5. Copiar arquivos do projeto
log_info "Copiando arquivos do projeto..."
# Assumindo que você já tem os arquivos localmente ou via git
# Opção 1: Se tiver repositório Git
# git clone https://github.com/SEU_USUARIO/SEU_REPO.git .

# Opção 2: Se os arquivos estão localmente
if [ -d "/root/bet_analysis_platform-2" ]; then
    cp -r /root/bet_analysis_platform-2/* "$PROJECT_DIR/"
elif [ -d "/tmp/bet_analysis_platform-2" ]; then
    cp -r /tmp/bet_analysis_platform-2/* "$PROJECT_DIR/"
else
    log_error "Arquivos do projeto não encontrados!"
    log_info "Por favor, faça upload dos arquivos para /root/bet_analysis_platform-2 antes de executar este script"
    exit 1
fi

# 6. Criar virtualenv
log_info "Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# 7. Instalar dependências Python
log_info "Instalando dependências Python..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 8. Criar estrutura de diretórios
log_info "Criando estrutura de diretórios..."
mkdir -p logs data/raw data/processed

# 9. Configurar PostgreSQL
log_info "Configurando PostgreSQL..."
sudo -u postgres psql -c "CREATE USER appuser WITH PASSWORD 'apppass';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE appdb OWNER appuser;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE appdb TO appuser;" 2>/dev/null || true

# 10. Verificar se .env existe
if [ ! -f ".env" ]; then
    log_warning "Arquivo .env não encontrado. Criando a partir de .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        log_warning "IMPORTANTE: Edite o arquivo .env com suas configurações!"
        log_warning "Execute: nano $PROJECT_DIR/.env"
    else
        log_error "Arquivo .env.example não encontrado!"
        exit 1
    fi
fi

# 11. Criar systemd service
log_info "Criando serviço systemd..."
cat > /etc/systemd/system/bet-analysis.service <<EOF
[Unit]
Description=Bet Analysis Platform 24/7
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python src/main.py --scheduled --interval 1
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Limites de recursos
MemoryLimit=1G
CPUQuota=80%

[Install]
WantedBy=multi-user.target
EOF

# 12. Configurar firewall
log_info "Configurando firewall (UFW)..."
ufw --force enable
ufw allow 22/tcp  # SSH
ufw allow 8000/tcp  # API (se necessário)
ufw reload

# 13. Configurar log rotation
log_info "Configurando rotação de logs..."
cat > /etc/logrotate.d/bet-analysis <<EOF
$PROJECT_DIR/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF

# 14. Criar script de monitoramento
log_info "Criando script de monitoramento..."
cat > "$PROJECT_DIR/monitor.sh" <<'EOF'
#!/bin/bash
echo "=========================================="
echo "📊 BET ANALYSIS - STATUS"
echo "=========================================="
echo ""
echo "🔹 Serviço:"
systemctl status bet-analysis --no-pager | head -10
echo ""
echo "🔹 Uso de Recursos:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')%"
echo "RAM: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "Disco: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " usado)"}')"
echo ""
echo "🔹 Últimos 10 logs:"
journalctl -u bet-analysis -n 10 --no-pager
echo ""
echo "=========================================="
EOF
chmod +x "$PROJECT_DIR/monitor.sh"

# 15. Criar script de backup
log_info "Criando script de backup..."
cat > "$PROJECT_DIR/backup.sh" <<'EOF'
#!/bin/bash
BACKUP_DIR="/root/backups"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/bet-analysis-backup-$(date +%Y%m%d_%H%M%S).tar.gz"
tar -czf "$BACKUP_FILE" /opt/bet_analysis_platform/data /opt/bet_analysis_platform/logs /opt/bet_analysis_platform/.env
echo "Backup criado: $BACKUP_FILE"
# Manter apenas os últimos 7 backups
ls -t "$BACKUP_DIR"/bet-analysis-backup-*.tar.gz | tail -n +8 | xargs -r rm
EOF
chmod +x "$PROJECT_DIR/backup.sh"

# Adicionar backup diário ao crontab
(crontab -l 2>/dev/null; echo "0 3 * * * $PROJECT_DIR/backup.sh") | crontab -

# 16. Criar script de atualização
log_info "Criando script de atualização..."
cat > "$PROJECT_DIR/update.sh" <<'EOF'
#!/bin/bash
echo "Atualizando projeto..."
cd /opt/bet_analysis_platform
source venv/bin/activate
git pull  # Se usando Git
pip install -r requirements.txt --upgrade
systemctl restart bet-analysis
echo "Atualização concluída!"
systemctl status bet-analysis
EOF
chmod +x "$PROJECT_DIR/update.sh"

# 17. Recarregar systemd
log_info "Recarregando systemd..."
systemctl daemon-reload

# 18. Habilitar serviço
log_info "Habilitando serviço para iniciar automaticamente..."
systemctl enable bet-analysis

# 19. Testar configuração
log_info "Testando instalação..."
source venv/bin/activate
python3 -c "import sys; print(f'Python version: {sys.version}')"
python3 -c "import pandas, numpy, sklearn; print('Dependências OK')"

echo ""
echo "=========================================="
echo "✅ DEPLOY CONCLUÍDO COM SUCESSO!"
echo "=========================================="
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1️⃣  Edite o arquivo .env com suas configurações:"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2️⃣  Inicie o serviço:"
echo "   systemctl start bet-analysis"
echo ""
echo "3️⃣  Verifique o status:"
echo "   systemctl status bet-analysis"
echo ""
echo "4️⃣  Veja os logs em tempo real:"
echo "   journalctl -u bet-analysis -f"
echo ""
echo "📊 Scripts úteis:"
echo "   Monitor: $PROJECT_DIR/monitor.sh"
echo "   Backup:  $PROJECT_DIR/backup.sh"
echo "   Update:  $PROJECT_DIR/update.sh"
echo ""
echo "🔗 Informações do servidor:"
echo "   IP: $(curl -s ifconfig.me)"
echo "   OS: $(lsb_release -d | cut -f2)"
echo "   Kernel: $(uname -r)"
echo ""
echo "=========================================="
echo "🎉 PROJETO PRONTO PARA RODAR 24/7!"
echo "=========================================="
