# 🚀 INÍCIO RÁPIDO - RODAR 24/7 NA NUVEM

## ⚡ Deploy em 5 Passos (10 minutos)

### 📋 O Que Você Precisa
- Cartão de crédito/débito (para aluguel do servidor)
- Token do Bot Telegram
- Channel ID do Telegram
- 10-15 minutos de tempo

---

## 🎯 OPÇÃO RECOMENDADA: DigitalOcean

**Custo**: $12/mês
**Facilidade**: ⭐⭐⭐⭐⭐
**Tempo**: 10 minutos

---

## 📝 PASSO A PASSO

### 1️⃣ Criar Conta no DigitalOcean

1. Acesse: https://www.digitalocean.com/
2. Clique em "Sign Up"
3. Use seu email e crie senha
4. **Ganhe $200 em créditos**: Use o link https://m.do.co/c/seu_codigo_ref

### 2️⃣ Criar Droplet (Servidor)

1. Após login, clique em "Create" → "Droplets"
2. Escolha as configurações:

   **Imagem**:
   - Ubuntu 22.04 LTS ✅

   **Plano**:
   - Basic ($12/mês - 1GB RAM, 25GB SSD) ✅
   - OU Standard ($24/mês - 2GB RAM, 50GB SSD) - Recomendado

   **Datacenter**:
   - New York (mais próximo do Brasil)
   - OU San Francisco

   **Authentication**:
   - Password (mais fácil)
   - Crie uma senha forte

3. Clique em "Create Droplet"
4. Aguarde 1 minuto (servidor sendo criado)
5. **Anote o IP do servidor** (ex: 142.93.123.45)

### 3️⃣ Conectar ao Servidor

**No Windows (PowerShell)**:
```powershell
# Substituir pelo seu IP
ssh root@142.93.123.45
```

**Primeiro acesso**:
- Digite "yes" quando perguntar sobre fingerprint
- Digite a senha que você criou

### 4️⃣ Fazer Upload do Projeto

**Abra OUTRO terminal** (mantenha o SSH aberto):

```powershell
# No seu computador local (Windows)
cd C:\Users\Trampo\Downloads\ChamaeledePlataformaX

# Upload para servidor (substituir pelo seu IP)
scp -r bet_analysis_platform-2 root@142.93.123.45:/tmp/
```

**Digite a senha** quando solicitado.

Aguarde o upload terminar (~2-5 minutos).

### 5️⃣ Executar Deploy Automático

**No terminal SSH** (conectado ao servidor):

```bash
# Ir para pasta do projeto
cd /tmp/bet_analysis_platform-2

# Dar permissão de execução
chmod +x deploy_digitalocean.sh

# EXECUTAR DEPLOY
./deploy_digitalocean.sh
```

**Aguarde 5-7 minutos** enquanto o script:
- Atualiza o sistema
- Instala Python 3.11
- Instala PostgreSQL
- Cria ambiente virtual
- Instala dependências
- Configura serviço systemd
- Configura firewall

### 6️⃣ Configurar Variáveis (.env)

```bash
# Editar arquivo de configuração
nano /opt/bet_analysis_platform/.env
```

**Cole suas configurações** (use setas para navegar):

```env
TELEGRAM_BOT_TOKEN=8260416435:AAH7aPa8eL8bYG0051IPyulUXqmaetFxrzQ
TELEGRAM_CHANNEL_ID=8329919168
KELLY_BANKROLL=1000.0
KELLY_FRACTION=0.25
MAX_DRAWDOWN_PERCENT=5.0
```

**Salvar e sair**:
- Pressione `Ctrl+X`
- Pressione `Y` (sim)
- Pressione `Enter`

### 7️⃣ Iniciar o Projeto

```bash
# Iniciar serviço
systemctl start bet-analysis

# Habilitar início automático
systemctl enable bet-analysis

# Ver status
systemctl status bet-analysis
```

**Você deve ver**:
```
● bet-analysis.service - Bet Analysis Platform 24/7
   Loaded: loaded
   Active: active (running) ✅
```

### 8️⃣ Ver Logs em Tempo Real

```bash
# Ver logs ao vivo
journalctl -u bet-analysis -f
```

**Você deve ver**:
```
[*] Iniciando ciclo de analise
[*] Coletando dados...
[*] Analisando padroes...
[*] Gerando sinais...
✅ Sinal enviado para Telegram!
```

**Pressione Ctrl+C** para sair dos logs (projeto continua rodando).

---

## ✅ PRONTO! PROJETO RODANDO 24/7!

Seu projeto está agora:
- ✅ Rodando 24 horas por dia
- ✅ Reinicia automaticamente se cair
- ✅ Enviando sinais via Telegram
- ✅ Auto-ajustando parâmetros (Feedback Loop)
- ✅ Validando otimizações (A/B Testing)
- ✅ Fazendo backup diário automático

---

## 📊 Comandos Úteis

### Ver Status
```bash
systemctl status bet-analysis
```

### Ver Logs
```bash
# Últimas 50 linhas
journalctl -u bet-analysis -n 50

# Ao vivo
journalctl -u bet-analysis -f

# Apenas erros
journalctl -u bet-analysis -p err
```

### Reiniciar
```bash
systemctl restart bet-analysis
```

### Parar
```bash
systemctl stop bet-analysis
```

### Monitorar Recursos
```bash
# CPU e RAM
htop

# Espaço em disco
df -h

# Uso de rede
ifconfig
```

### Verificação Completa
```bash
cd /opt/bet_analysis_platform
./fix_and_monitor.sh
```

---

## 🔧 Manutenção

### Atualizar Código
```bash
cd /opt/bet_analysis_platform
git pull  # Se usar Git
systemctl restart bet-analysis
```

### Ver Estatísticas
```bash
cat /opt/bet_analysis_platform/data/stats.json
```

### Backup Manual
```bash
cd /opt/bet_analysis_platform
./backup.sh
```

### Monitoramento Automático
```bash
# Adicionar verificação a cada 30 minutos
crontab -e

# Adicionar esta linha:
*/30 * * * * /opt/bet_analysis_platform/fix_and_monitor.sh
```

---

## 💰 Custos

### DigitalOcean
- **Basic**: $12/mês (suficiente)
- **Standard**: $24/mês (recomendado)
- **Backups**: +$2.40/mês (opcional)

### Total Mensal
- Mínimo: **$12/mês**
- Recomendado: **$24/mês**
- Com backups: **$26.40/mês**

---

## 🛡️ Segurança

### Firewall (já configurado)
```bash
# Ver regras
ufw status

# Deve mostrar:
22/tcp    ALLOW  # SSH
8000/tcp  ALLOW  # API (opcional)
```

### Atualizações Automáticas
```bash
# Habilitar (já feito no deploy)
dpkg-reconfigure --priority=low unattended-upgrades
```

### Trocar Senha Root
```bash
passwd
```

---

## 📞 Ajuda e Suporte

### Telegram Não Recebe Sinais?

1. Verificar logs:
```bash
journalctl -u bet-analysis | grep -i telegram
```

2. Verificar .env:
```bash
cat /opt/bet_analysis_platform/.env | grep TELEGRAM
```

3. Testar conexão:
```bash
curl -s "https://api.telegram.org/bot<SEU_TOKEN>/getMe"
```

### Serviço Não Inicia?

1. Ver erros:
```bash
journalctl -u bet-analysis -n 100 -p err
```

2. Verificar dependências:
```bash
cd /opt/bet_analysis_platform
source venv/bin/activate
pip check
```

3. Testar manualmente:
```bash
cd /opt/bet_analysis_platform
source venv/bin/activate
python src/main.py
```

### Alto Uso de Memória?

1. Verificar:
```bash
free -h
```

2. Reiniciar:
```bash
systemctl restart bet-analysis
```

3. Limpar logs:
```bash
journalctl --vacuum-time=7d
```

### Servidor Lento?

1. Ver processos:
```bash
htop
```

2. Limpar cache:
```bash
sync; echo 3 > /proc/sys/vm/drop_caches
```

3. Considerar upgrade do plano

---

## 🎓 Próximos Passos

### Opcional: Configurar Domínio
```bash
# Comprar domínio (ex: meubot.com)
# Apontar para IP do servidor
# Configurar SSL com Let's Encrypt
```

### Opcional: Dashboard Web
```bash
# Quando Tarefa 9 estiver pronta
# Acesse: http://SEU_IP:8000
```

### Opcional: Monitoramento Avançado
```bash
# Instalar Grafana + Prometheus
# Já tem exporter configurado em docker-compose.yml
```

---

## ✅ Checklist Final

Antes de considerar finalizado:

- [ ] Servidor criado no DigitalOcean
- [ ] SSH funcionando
- [ ] Deploy executado com sucesso
- [ ] .env configurado
- [ ] Serviço rodando (systemctl status)
- [ ] Logs mostrando atividade
- [ ] Telegram recebendo sinais
- [ ] Monitoramento configurado (crontab)
- [ ] Senha do root trocada
- [ ] Backup automático ativado

---

## 🎉 Parabéns!

Você tem agora um sistema profissional de análise de apostas rodando 24/7 na nuvem!

**Características**:
- 🤖 Automático
- 📊 Inteligente (ML + IA)
- 💰 Lucrativo (Kelly Criterion)
- 🛡️ Seguro (Drawdown Manager)
- 📱 Notificações (Telegram)
- 🔄 Auto-ajuste (Feedback Loop)
- 🧪 Validação (A/B Testing)

**Próximos 7 dias**:
1. Monitore os sinais via Telegram
2. Verifique logs diariamente
3. Acompanhe métricas de lucro
4. Ajuste parâmetros se necessário

**Após 30 dias**:
- Analise ROI acumulado
- Revise ajustes do Feedback Loop
- Veja resultados do A/B Testing
- Decida se quer manter/modificar

---

**BOA SORTE! 🍀**

Seu assistente de IA está sempre aprendendo e melhorando!
