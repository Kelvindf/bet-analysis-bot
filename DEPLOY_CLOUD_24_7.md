# 🚀 DEPLOY 24/7 NA NUVEM - GUIA COMPLETO

## 📋 Índice
1. [Opções de Hospedagem](#opções-de-hospedagem)
2. [Custos Mensais](#custos-mensais)
3. [Deploy Automático](#deploy-automático)
4. [Monitoramento](#monitoramento)
5. [Manutenção](#manutenção)

---

## 💰 Opções de Hospedagem (Mensal)

### 🥇 OPÇÃO 1: DigitalOcean (RECOMENDADO)
**Custo: $12-24/mês**

✅ **Vantagens**:
- Interface simples
- Deploy em 5 minutos
- Ótima documentação
- Suporte 24/7
- Backups automáticos

**Planos**:
- Basic ($12/mês): 1GB RAM, 1 CPU - SUFICIENTE
- Standard ($24/mês): 2GB RAM, 2 CPU - RECOMENDADO

**Como fazer**:
1. Criar conta: https://digitalocean.com
2. Criar Droplet Ubuntu 22.04
3. SSH no servidor
4. Executar `deploy_digitalocean.sh` (criado abaixo)

---

### 🥈 OPÇÃO 2: AWS EC2
**Custo: $10-30/mês**

✅ **Vantagens**:
- Tier gratuito (12 meses)
- Escalabilidade
- Integração com outros serviços

**Planos**:
- t3.micro: $8.35/mês - MÍNIMO
- t3.small: $16.79/mês - RECOMENDADO

**Como fazer**:
1. Criar conta: https://aws.amazon.com
2. Lançar EC2 Ubuntu 22.04
3. Executar `deploy_aws.sh`

---

### 🥉 OPÇÃO 3: Google Cloud
**Custo: $13-25/mês**

✅ **Vantagens**:
- $300 créditos gratuitos
- Always Free tier
- Boa performance

**Planos**:
- e2-micro: $13/mês - MÍNIMO
- e2-small: $24/mês - RECOMENDADO

---

### 🔹 OPÇÃO 4: Contabo VPS (MAIS BARATO)
**Custo: €4-8/mês (~$4.50-9/mês)**

✅ **Vantagens**:
- MUITO BARATO
- Bom hardware
- Datacenters Europa/EUA

**Planos**:
- VPS S: €4.99/mês (4GB RAM!) - EXCELENTE CUSTO-BENEFÍCIO

---

### 🔹 OPÇÃO 5: Heroku (MAIS FÁCIL)
**Custo: $7-25/mês**

✅ **Vantagens**:
- Deploy com 1 comando
- Gerenciamento zero
- Integração Git

**Planos**:
- Eco Dynos: $5/mês (sleep após inatividade)
- Basic: $7/mês (sempre ligado)
- Standard 1X: $25/mês (melhor performance)

---

## 📊 Comparação de Custos (Tabela)

| Provedor | Custo/Mês | RAM | CPU | Facilidade | Nota |
|----------|-----------|-----|-----|------------|------|
| **Contabo** | $5-9 | 4-8GB | 2-4 | ⭐⭐⭐ | Melhor custo |
| **DigitalOcean** | $12-24 | 1-2GB | 1-2 | ⭐⭐⭐⭐⭐ | **RECOMENDADO** |
| **Heroku** | $7-25 | 512MB-1GB | 1 | ⭐⭐⭐⭐⭐ | Mais fácil |
| **AWS EC2** | $10-30 | 1-2GB | 1-2 | ⭐⭐⭐ | Mais complexo |
| **Google Cloud** | $13-25 | 1-2GB | 1-2 | ⭐⭐⭐ | Bons créditos |

---

## 🎯 RECOMENDAÇÃO FINAL

### Para você (iniciante): **DigitalOcean**
- ✅ Fácil de usar
- ✅ Preço justo ($12/mês)
- ✅ Deploy em 5 minutos
- ✅ Suporte excelente
- ✅ Scripts prontos (veja abaixo)

### Se quer economizar: **Contabo**
- ✅ Apenas $5/mês
- ✅ 4GB RAM (excelente)
- ⚠️ Interface menos intuitiva

### Se quer simplicidade máxima: **Heroku**
- ✅ Deploy com git push
- ✅ Zero configuração
- ⚠️ Preço um pouco maior ($25/mês para bom plano)

---

## 🚀 DEPLOY RÁPIDO (DigitalOcean)

### Passo 1: Criar Droplet
1. Acesse: https://cloud.digitalocean.com/droplets/new
2. Escolha:
   - **Imagem**: Ubuntu 22.04 LTS
   - **Plano**: Basic ($12/mês ou $24/mês)
   - **Datacenter**: New York ou San Francisco
   - **Authentication**: SSH Key (recomendado) ou Password

### Passo 2: Conectar via SSH
```bash
ssh root@SEU_IP_AQUI
```

### Passo 3: Executar Deploy
```bash
# Baixar script de deploy
curl -O https://raw.githubusercontent.com/SEU_REPO/deploy_digitalocean.sh
chmod +x deploy_digitalocean.sh

# Executar
./deploy_digitalocean.sh
```

### Passo 4: Configurar .env
```bash
cd /opt/bet_analysis_platform
nano .env
```

Cole suas configurações:
```env
TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI
TELEGRAM_CHANNEL_ID=SEU_CHANNEL_ID
KELLY_BANKROLL=1000.0
KELLY_FRACTION=0.25
MAX_DRAWDOWN_PERCENT=5.0
```

### Passo 5: Iniciar Projeto
```bash
systemctl start bet-analysis
systemctl enable bet-analysis  # Iniciar automaticamente
systemctl status bet-analysis  # Ver status
```

**PRONTO! Projeto rodando 24/7!** 🎉

---

## 📊 Monitoramento

### Ver logs em tempo real:
```bash
journalctl -u bet-analysis -f
```

### Ver últimos 100 logs:
```bash
journalctl -u bet-analysis -n 100
```

### Ver status:
```bash
systemctl status bet-analysis
```

### Estatísticas:
```bash
cd /opt/bet_analysis_platform
cat data/stats.json
```

---

## 🔧 Manutenção

### Atualizar código:
```bash
cd /opt/bet_analysis_platform
git pull
systemctl restart bet-analysis
```

### Reiniciar serviço:
```bash
systemctl restart bet-analysis
```

### Parar serviço:
```bash
systemctl stop bet-analysis
```

### Ver uso de recursos:
```bash
htop  # CPU e RAM
df -h  # Disco
```

---

## 🛡️ Segurança

### Firewall (UFW):
```bash
ufw allow 22/tcp    # SSH
ufw allow 8000/tcp  # API (opcional)
ufw enable
```

### Atualizações automáticas:
```bash
apt install unattended-upgrades
dpkg-reconfigure --priority=low unattended-upgrades
```

### Backup automático:
```bash
# DigitalOcean oferece backups por +$2.40/mês
# Habilitar no painel de controle
```

---

## 📞 Suporte

### DigitalOcean:
- Tickets 24/7: https://cloud.digitalocean.com/support
- Documentação: https://docs.digitalocean.com
- Comunidade: https://www.digitalocean.com/community

### Logs de erro:
```bash
tail -f /opt/bet_analysis_platform/logs/bet_analysis.log
```

---

## ⚡ INÍCIO RÁPIDO (5 MINUTOS)

```bash
# 1. Criar Droplet no DigitalOcean ($12/mês)
# 2. SSH no servidor
ssh root@SEU_IP

# 3. Executar estes comandos:
apt update && apt upgrade -y
apt install -y python3.11 python3.11-venv git
git clone SEU_REPOSITORIO /opt/bet_analysis_platform
cd /opt/bet_analysis_platform
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configurar .env
nano .env  # Cole suas configurações

# 5. Criar systemd service
cat > /etc/systemd/system/bet-analysis.service <<EOF
[Unit]
Description=Bet Analysis Platform
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/bet_analysis_platform
ExecStart=/opt/bet_analysis_platform/venv/bin/python src/main.py --scheduled --interval 1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 6. Iniciar
systemctl daemon-reload
systemctl start bet-analysis
systemctl enable bet-analysis

# 7. Verificar
systemctl status bet-analysis
```

**PRONTO! Rodando 24/7 na nuvem!** 🚀

---

## 💡 Dicas Extras

### 1. Usar Docker (mais fácil)
```bash
# Já existe docker-compose.yml no projeto
docker-compose up -d
```

### 2. Monitorar com Telegram
O sistema já envia alertas via Telegram automaticamente!

### 3. Backup diário
```bash
# Adicionar ao crontab
0 3 * * * tar -czf /root/backup-$(date +\%Y\%m\%d).tar.gz /opt/bet_analysis_platform/data
```

---

## 🎓 Conclusão

**Custo total mensal**: $12-24 (DigitalOcean)
**Tempo de setup**: 5-10 minutos
**Uptime**: 99.9%+ garantido
**Suporte**: 24/7 incluído

Seu projeto vai rodar continuamente, enviar sinais via Telegram e se auto-ajustar com o Feedback Loop e A/B Testing!

Qualquer dúvida, consulte os scripts de deploy criados ou entre em contato com o suporte do provedor escolhido.

**BOA SORTE! 🍀**
