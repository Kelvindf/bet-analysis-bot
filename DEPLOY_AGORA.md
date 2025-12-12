# 🚀 COMEÇAR AGORA - 3 PASSOS (2 MINUTOS)

## ✅ PASSO 1: Criar Repositório GitHub (30 segundos)

### Opção A: Navegador (Mais Fácil)
1. Acesse: **https://github.com/new**
2. Nome do repositório: `bet-analysis-bot`
3. Deixe **PÚBLICO** ✅
4. **NÃO** marque "Initialize with README"
5. Clique **"Create repository"**
6. Copie a URL que aparece (algo como `https://github.com/SEU_USUARIO/bet-analysis-bot.git`)

### Opção B: Linha de Comando (Se você já tem conta GitHub)
```powershell
# Execute estes comandos no PowerShell (você já está no diretório certo):
git remote add origin https://github.com/SEU_USUARIO/bet-analysis-bot.git
git branch -M main
git push -u origin main
```

**⚠️ Substitua `SEU_USUARIO` pelo seu nome de usuário do GitHub!**

---

## ✅ PASSO 2: Conectar GitHub ao Render (30 segundos)

1. **Criar conta Render**: https://dashboard.render.com/register
   - Use opção **"Sign up with GitHub"** (1 clique) ✅
   
2. **Autorizar Render** a acessar seus repositórios GitHub
   - Clique "Authorize Render"

---

## ✅ PASSO 3: Fazer Deploy (1 minuto)

1. No dashboard Render: https://dashboard.render.com

2. Clique **"New +"** (botão azul superior direito)

3. Selecione **"Blueprint"**

4. Conecte o repositório **`bet-analysis-bot`**

5. Render detecta automaticamente o arquivo `render.yaml`

6. Clique **"Apply"**

7. **🎉 PRONTO! Bot rodando 24/7 gratuitamente!**

---

## 🔍 VERIFICAR SE FUNCIONOU

### Ver Logs (5 segundos depois)
```
Dashboard Render → "bet-analysis-bot" → Aba "Logs"
```

**O que você deve ver:**
```
🚀 Bet Analysis Bot iniciado em modo 24/7
📊 Processando sinais Crash/Double Blaze...
✅ Sinal enviado ao Telegram (Confiança: 85%)
```

### Ver Sinais no Telegram (1 minuto depois)
- Abra seu canal Telegram: `8329919168`
- Sinais começam a aparecer automaticamente
- Formato: **🎰 Double | Entrada: 3,5 | Stop: 2x | Conf: 87%**

---

## 💡 SE VOCÊ NÃO TEM CONTA GITHUB

### Criar Conta GitHub (1 minuto)
1. Acesse: **https://github.com/signup**
2. Email: seu email
3. Senha: criar senha forte
4. Username: escolher nome de usuário
5. Verificar email
6. **Pronto!** Volte ao PASSO 1 acima

---

## 🆘 COMANDOS PRONTOS (COPIAR/COLAR)

### Se você escolheu criar via navegador (Opção A):
```powershell
# Depois de criar o repositório no GitHub e copiar a URL, execute:
git remote add origin https://github.com/SEU_USUARIO/bet-analysis-bot.git
git branch -M main
git push -u origin main
```

**⚠️ LEMBRE-SE:** Substituir `SEU_USUARIO` pelo seu nome real do GitHub!

### Exemplo com usuário "joaosilva":
```powershell
git remote add origin https://github.com/joaosilva/bet-analysis-bot.git
git branch -M main
git push -u origin main
```

---

## 🎯 APÓS O DEPLOY

### Monitorar Logs
```
Render Dashboard → Seu serviço → "Logs" tab
```

### Testar Mudanças Futuras
```powershell
# Fazer alteração em algum arquivo
git add .
git commit -m "Minha alteração"
git push

# Render faz deploy automático em ~2 minutos!
```

---

## ⏱️ TEMPO TOTAL
- **PASSO 1**: 30 segundos (criar repo GitHub)
- **PASSO 2**: 30 segundos (conectar Render)
- **PASSO 3**: 1 minuto (deploy automático)
- **TOTAL**: ~2 minutos até bot rodando 24/7! 🚀

---

**✅ TUDO CONFIGURADO NO CÓDIGO! Agora é só seguir os 3 passos acima! Qualquer dúvida, me avise! 🎉**
