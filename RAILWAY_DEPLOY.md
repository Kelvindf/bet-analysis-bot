# 🚀 DEPLOY RAILWAY.APP - 100% GRÁTIS

Railway é mais simples que Fly.io e **não precisa de cartão de crédito**. Você ganha $5 de crédito (suficiente para ~2 meses).

## 3 Passos Simples

### 1️⃣ Criar Conta Railway
```
Acesse: https://railway.app
Clique "Sign in with GitHub"
Autorize Railway
```

### 2️⃣ Conectar seu Repositório GitHub
```
Dashboard Railway → New Project → Deploy from GitHub repo
Escolha: Kelvindf/bet-analysis-bot
```

### 3️⃣ Configurar Variáveis de Ambiente
No Railway, após conectar repo:
- Clique na aba "Variables"
- Adicione:
  - `TELEGRAM_BOT_TOKEN`: 8260416435:AAH7aPa8eL8bYG0051IPyulUXqmaetFxrzQ
  - `TELEGRAM_CHANNEL_ID`: 8329919168
  - `KELLY_BANKROLL`: 1000.0
  - `KELLY_FRACTION`: 0.25
  - `MAX_DRAWDOWN_PERCENT`: 5.0
  - `PYTHONUNBUFFERED`: 1

### 4️⃣ Deploy
- Build command: `pip install -r requirements.txt`
- Start command: `python src/main.py --scheduled --interval 1`
- Clique "Deploy"

---

## ✅ Resultado

- **Bot rodando 24/7** em ~2-3 minutos
- **Sinais no Telegram** a cada minuto
- **$5 grátis**: suficiente para ~2 meses
- **Zero custos mensais**

---

## 📊 Comparação

| Plataforma | Custo | Cartão | Tempo Deploy | Status |
|-----------|-------|--------|-------------|--------|
| **Railway** | $0 (5$ grátis) | ❌ Não | 2-3 min | ✅ RECOMENDADO |
| Fly.io | Free (precisa cart) | ✅ Sim | 3-5 min | ⏸️ Bloqueado |
| Heroku | $7+/mês | ✅ Sim | 2-3 min | ❌ Pago |
| Render | Free (limitado) | ❌ Não | 2-3 min | ⏸️ Plano restringe |

---

## 🎯 Próximos Passos

1. Acesse: https://railway.app
2. Sign up com GitHub
3. "New Project" → "Deploy from GitHub"
4. Selecione `Kelvindf/bet-analysis-bot`
5. Configure variáveis (copie de cima)
6. Deploy

**Pronto! Seu bot estará rodando 24/7!**

---

## 📝 Se precisar ajuda

Railway detecta automaticamente:
- Dockerfile (se existir)
- requirements.txt
- python (no Dockerfile ou package.json)

Tudo já está no seu repo, então é só conectar! 🚀
