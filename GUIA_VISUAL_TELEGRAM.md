# 📱 GUIA VISUAL - Como Obter Chat ID do Telegram

## 🎯 O Que Você Precisa Fazer

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  1. Abra Telegram                                       │
│  2. Procure seu bot                                     │
│  3. Envie /start                                        │
│  4. Envie uma mensagem (qualquer uma)                   │
│  5. Volte ao PowerShell e copie o Chat ID              │
│  6. Atualize .env com o novo ID                         │
│  7. Pronto! Seu projeto receberá mensagens              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📲 Passo 1: Abra o Telegram

```
Telegram é um aplicativo de mensagens. Você pode usar:
- Celular (Android/iOS)
- Computador (Desktop)
- Web (web.telegram.org)
```

---

## 🔍 Passo 2: Procure Seu Bot

### Método 1: Pela Barra de Busca
```
┌─────────────────────────────────────────┐
│ 🔍  Procure por: @seu_bot_name         │
└─────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────┐
│ Clique no bot que aparecer              │
└─────────────────────────────────────────┘
```

### Método 2: Verificar o Nome do Bot
```
1. Procure por @BotFather
2. Digite: /mybots
3. Clique em seu bot
4. Copie o username (exemplo: @MyBettingBot)
5. Use esse nome para procurar
```

---

## 💬 Passo 3: Envie /start

```
┌──────────────────────────────────────────────┐
│ Conversa com seu bot                         │
├──────────────────────────────────────────────┤
│                                              │
│  [Você] /start                               │
│  ↓                                           │
│  [Bot] Bem-vindo! (resposta automática)      │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 📝 Passo 4: Envie Uma Mensagem Qualquer

```
┌──────────────────────────────────────────────┐
│ Conversa com seu bot                         │
├──────────────────────────────────────────────┤
│                                              │
│  [Você] /start                               │
│  [Bot] Bem-vindo!                            │
│  ↓                                           │
│  [Você] oi                                   │
│  [Você] teste                                │
│  [Você] qualquer coisa                       │
│  ↓                                           │
│  (Não precisa responder, apenas enviar)      │
│                                              │
└──────────────────────────────────────────────┘
```

---

## 🖥️ Passo 5: Volte ao PowerShell

Volte à janela do PowerShell onde você executou:
```powershell
.\venv\Scripts\python.exe get_chat_id.py
```

O script está aguardando. Veja a resposta.

---

## 📊 Passo 6: Copie o Chat ID

Você verá algo como:

```
[*] Buscando Chat ID...
[OK] Encontradas 1 mensagens

============================================================
Chat ID: 123456789
Username: seu_usuario
Primeiro Nome: Seu Nome
Última Mensagem: oi
============================================================

[OK] Use o Chat ID acima para configurar .env:
    TELEGRAM_CHANNEL_ID=123456789
```

**Copie este número:** `123456789`

---

## ⚙️ Passo 7: Atualize o .env

### Abrir o arquivo

```powershell
notepad .env
```

Você verá:

```properties
TELEGRAM_BOT_TOKEN=8347334478:AAHGap7AeSEWG1vPG1OyRjg4wHNgCCFbAjg
TELEGRAM_CHANNEL_ID=770356893
BLAZE_API_URL=https://api.blaze.com
...
```

### Trocar o Chat ID

Procure por:
```
TELEGRAM_CHANNEL_ID=770356893
```

Troque para:
```
TELEGRAM_CHANNEL_ID=123456789
```

(Use o número que você copiou)

### Salvar

- Pressione `Ctrl+S`
- Feche o arquivo

---

## 🚀 Passo 8: Rodar Novamente

```powershell
.\venv\Scripts\python.exe src/main.py
```

Você verá:

```
[OK] Bot do Telegram inicializado
[*] Coletando dados...
[OK] Double: 20 registros coletados
[*] Analisando padrões...
[OK] Gerando sinais...
[*] Enviando 1 sinal(is) para Telegram...
[*] Total de sinais enviados: 1/1
[OK] Ciclo de análise concluído com sucesso
```

**E você receberá uma mensagem no Telegram!** 🎉

---

## 🎉 Pronto!

Seu Chat ID foi validado e configurado com sucesso!

Agora você pode rodar em modo contínuo:

```powershell
# A cada 5 minutos
.\venv\Scripts\python.exe src/main.py --scheduled

# A cada 10 minutos
.\venv\Scripts\python.exe src/main.py --scheduled --interval 10
```

---

## ⚠️ Solução de Problemas

### "Nenhuma mensagem encontrada"

**O que fazer:**
1. Certifique-se de estar no bot correto
2. Procure `@BotFather` e veja seu bot
3. Envie `/start` novamente
4. Envie uma mensagem de teste
5. Execute o script novamente

### "Chat not found" ao rodar

**O que fazer:**
1. Volte ao Passo 5-7 acima
2. Use o Chat ID correto do script
3. Atualize `.env`
4. Rode novamente

### "Token inválido"

**O que fazer:**
1. Procure `@BotFather` no Telegram
2. Digite `/mybots`
3. Clique em seu bot
4. Procure o token (chave de acesso)
5. Atualize em `.env`:
   ```
   TELEGRAM_BOT_TOKEN=seu_token_correto_aqui
   ```

---

## 📚 Dicas Importantes

1. **Segurança:** Não compartilhe seu token ou Chat ID
2. **Bot:** Precisa ser criado em `@BotFather` antes
3. **Resposta:** O script pode levar alguns segundos
4. **Mensagem:** Qualquer mensagem serve, não precisa de resposta do bot
5. **Replicar:** Se mudar de computador, execute novamente

---

## ✅ Checklist Final

```
☐ Telegram aberto
☐ Bot encontrado e clicado
☐ /start enviado
☐ Mensagem de teste enviada
☐ Voltei ao PowerShell
☐ Chat ID copiado
☐ .env atualizado com novo ID
☐ src/main.py executado
☐ Recebi mensagem no Telegram
☐ Pronto para usar!
```

---

**Quando tudo estiver funcionando, você receberá mensagens no Telegram automaticamente!** 🚀

