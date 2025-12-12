# 🚀 DEPLOY GRATUITO - RENDER.COM (SEM CARTÃO)

## ✅ Por que Render.com?

- **100% GRATUITO** - Sem cartão de crédito necessário
- **24/7 AUTOMÁTICO** - Roda continuamente sem parar
- **DEPLOY EM 2 MINUTOS** - Só conectar GitHub e pronto
- **750 HORAS/MÊS GRÁTIS** - Suficiente para rodar sempre

---

## 📋 PASSO A PASSO (2 MINUTOS)

### 1️⃣ Criar Conta Render (30 segundos)

```
🔗 https://dashboard.render.com/register
```

**Opções de cadastro:**
- GitHub (RECOMENDADO - 1 clique)
- Google
- Email

### 2️⃣ Criar Repositório GitHub (1 minuto)

**Opção A: Via navegador**
1. Acesse: https://github.com/new
2. Nome: `bet-analysis-bot`
3. Deixe PÚBLICO
4. Clique "Create repository"

**Opção B: Via linha de comando** (você já tem Git configurado):
```powershell
# No diretório do projeto (você já está lá)
git remote add origin https://github.com/SEU_USUARIO/bet-analysis-bot.git
git push -u origin main
```

### 3️⃣ Deploy no Render (30 segundos)

1. **No dashboard Render**: https://dashboard.render.com
2. Clique **"New +"** → **"Blueprint"**
3. Conecte seu repositório GitHub `bet-analysis-bot`
4. Render detecta automaticamente o `render.yaml`
5. Clique **"Apply"**
6. ✅ **PRONTO! Bot rodando 24/7**

---

## 🔍 VERIFICAR SE ESTÁ FUNCIONANDO

### Ver Logs em Tempo Real
```
Dashboard Render → Seu serviço → Aba "Logs"
```

**O que você deve ver:**
```
🚀 Bet Analysis Bot iniciado...
📊 Processando sinais...
✅ Sinal enviado: Crash Blaze (Confiança: 87%)
```

### Verificar no Telegram
- Abra o canal: `8329919168`
- Sinais devem aparecer automaticamente
- Formato: **Jogo | Entrada | Stop | Confiança**

---

## 🎯 ALTERNATIVAS SE RENDER NÃO FUNCIONAR

### Railway.app (Com $5 Grátis)
```
🔗 https://railway.app
- Cadastro com GitHub
- $5 crédito inicial (roda ~1 mês grátis)
- Deploy similar ao Render
```

### Fly.io (Gratuito com Limites)
```
🔗 https://fly.io
- 3 VMs gratuitas 24/7
- Sem cartão necessário
- Deploy via CLI
```

---

## ⚙️ CONFIGURAÇÕES IMPORTANTES

### Variáveis de Ambiente (Já Configuradas no render.yaml)
```yaml
TELEGRAM_BOT_TOKEN: 8260416435:AAH7aPa8eL8bYG0051IPyulUXqmaetFxrzQ
TELEGRAM_CHANNEL_ID: 8329919168
KELLY_BANKROLL: 1000.0
KELLY_FRACTION: 0.25
MAX_DRAWDOWN_PERCENT: 5.0
PYTHONUNBUFFERED: 1
```

### Plano Gratuito - Limites
- **750 horas/mês** = 31 dias rodando 24/7 ✅
- **512 MB RAM** = Suficiente para o bot ✅
- **Sleep após 15min inatividade** = Nosso bot roda sempre, não dorme ✅

---

## 🐛 TROUBLESHOOTING

### "Build Failed"
**Solução**: Verificar se `requirements.txt` está no repositório
```powershell
git add requirements.txt
git commit -m "Add requirements"
git push
```

### "Service não inicia"
**Solução**: Ver logs no dashboard e verificar variáveis de ambiente

### "Bot não envia mensagens"
**Solução**: Verificar se bot foi adicionado ao canal Telegram como admin

---

## 📊 MONITORAMENTO

### Dashboard Render
```
- CPU Usage: Deve ficar em ~10-20%
- Memory: ~200-300 MB
- Logs: Devem mostrar processamento contínuo
```

### Telegram
```
- Sinais aparecem a cada análise (intervalo de 1 minuto configurado)
- Formato correto com confiança %
- Sem erros de autenticação
```

---

## 🎉 VANTAGENS DO RENDER

| Recurso | Render.com | Heroku |
|---------|------------|--------|
| **Preço** | 100% Gratuito | Requer cartão |
| **Uptime** | 24/7 sempre | 550h/mês free |
| **Deploy** | Automático | Manual |
| **Sleep** | Não dorme | Dorme após 30min |
| **Reinício** | Auto-restart | Manual |

---

## 📝 PRÓXIMOS PASSOS APÓS DEPLOY

1. ✅ Verificar logs (primeiro sinal em ~1 min)
2. ✅ Acompanhar Telegram por 10 minutos
3. ✅ Validar formato dos sinais
4. 🎯 (Opcional) Implementar Dashboard (Tarefa 9)

---

## 💡 DICAS PRO

### Auto-Deploy Ativado
- Cada `git push` → Render faz deploy automático
- Testar mudanças: commit → push → aguardar 2min

### Logs Persistentes
```
Dashboard → Logs → Download
```

### Múltiplos Ambientes
- Criar branch `staging` para testes
- Branch `main` = produção 24/7

---

**✅ TUDO CONFIGURADO! Basta seguir os 3 passos acima e seu bot estará rodando 24/7 GRATUITAMENTE! 🚀**
