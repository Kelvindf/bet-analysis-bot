# 🚀 DEPLOY HEROKU - COMANDOS PRONTOS

## ⚠️ ANTES DE COMEÇAR

1. **Instalar Git**: https://git-scm.com/download/win
2. **Instalar Heroku CLI**: https://cli-assets.heroku.com/heroku-x64.exe

Após instalar ambos, **FECHE E REABRA o PowerShell**

---

## 📋 COMANDOS PARA COPIAR E COLAR

### Passo 1: Ir para o diretório do projeto

```powershell
cd C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2
```

### Passo 2: Login no Heroku

```powershell
heroku login
```

*Vai abrir o navegador. Faça login ou crie conta grátis.*

### Passo 3: Criar aplicação no Heroku

```powershell
heroku create bet-analysis-bot-live
```

### Passo 4: Adicionar PostgreSQL (grátis)

```powershell
heroku addons:create heroku-postgresql:essential-0
```

### Passo 5: Configurar variáveis de ambiente

```powershell
heroku config:set TELEGRAM_BOT_TOKEN="8260416435:AAH7aPa8eL8bYG0051IPyulUXqmaetFxrzQ"
heroku config:set TELEGRAM_CHANNEL_ID="8329919168"
heroku config:set KELLY_BANKROLL="1000.0"
heroku config:set KELLY_FRACTION="0.25"
heroku config:set MAX_DRAWDOWN_PERCENT="5.0"
heroku config:set PYTHONUNBUFFERED="1"
```

### Passo 6: Inicializar Git e fazer deploy

```powershell
git init
git add .
git commit -m "Deploy inicial do bot"
git push heroku main
```

*Se der erro sobre branch, use:*
```powershell
git branch -M main
git push heroku main
```

### Passo 7: Iniciar worker (rodar 24/7)

```powershell
heroku ps:scale worker=1
```

### Passo 8: Ver logs em tempo real

```powershell
heroku logs --tail
```

**Pressione Ctrl+C para sair dos logs** (o bot continua rodando)

---

## ✅ VERIFICAR SE ESTÁ RODANDO

```powershell
# Ver status
heroku ps

# Ver configurações
heroku config

# Abrir dashboard do Heroku
heroku open
```

---

## 🔧 COMANDOS ÚTEIS

### Reiniciar o bot
```powershell
heroku restart
```

### Parar o bot
```powershell
heroku ps:scale worker=0
```

### Ver erros
```powershell
heroku logs --tail --source app
```

### Atualizar código
```powershell
git add .
git commit -m "Atualização"
git push heroku main
```

---

## 💰 CUSTO

- **Grátis por 1000 horas/mês** (suficiente para teste)
- **Eco Dynos**: $5/mês (dorme após 30min inativo)
- **Basic**: $7/mês (sempre rodando 24/7) ✅ RECOMENDADO
- **Standard**: $25/mês (mais recursos)

Para usar o plano Basic (24/7):
```powershell
heroku ps:type worker=basic
```

---

## 🎉 PRONTO!

Após executar todos os comandos acima, seu bot estará:
- ✅ Rodando 24/7 na nuvem
- ✅ Enviando sinais via Telegram
- ✅ Auto-ajustando parâmetros
- ✅ Fazendo backup automático

**URL do seu app**: https://bet-analysis-bot-live.herokuapp.com

**Dashboard Heroku**: https://dashboard.heroku.com/apps/bet-analysis-bot-live

---

## 📞 PRECISA DE AJUDA?

Execute:
```powershell
heroku help
```

Ou visite: https://devcenter.heroku.com/
