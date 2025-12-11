# 🤖 Configurando Telegram para Receber Sinais de Apostas

## Erro Encontrado

```
Chat not found
```

Este erro significa que o bot não conseguiu enviar mensagens para o ID fornecido.

---

## ✅ Solução Passo a Passo

### Passo 1: Confirme que o Bot Existe

Abra o Telegram e procure pelo seu bot usando o token:
```
https://t.me/bot8347334478:AAHGap7AeSEWG1vPG1OyRjg4wHNgCCFbAjg
```

⚠️ **Isso não funciona. Você precisa fazer diferente:**

### Passo 2: Encontre o Username do Seu Bot

1. Abra o Telegram
2. Procure por `@BotFather`
3. Envie `/mybots`
4. Clique no seu bot (deve estar criado)
5. Copie o **username** (por exemplo: `@seu_bot_name`)

### Passo 3: Inicie uma Conversa com Seu Bot

1. No Telegram, procure pelo username do seu bot
2. Clique nele
3. Envie a mensagem: `/start`

Agora o bot conhece seu chat!

### Passo 4: Obtenha Seu Chat ID Real

Execute este script para descobrir seu ID:

```python
import requests
import json

TOKEN = "8347334478:AAHGap7AeSEWG1vPG1OyRjg4wHNgCCFbAjg"

# Obter últimas mensagens
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
response = requests.get(url)
data = response.json()

print(json.dumps(data, indent=2))

# Procure por 'chat' -> 'id' na resposta
```

Execute:
```bash
python get_chat_id.py
```

Na resposta, procure por um bloco assim:
```json
{
  "message": {
    "chat": {
      "id": AQUI_ESTA_SEU_ID
    }
  }
}
```

### Passo 5: Atualize o .env

Depois de encontrar seu Chat ID real, atualize:

```
TELEGRAM_CHANNEL_ID=seu_id_aqui
```

---

## 🔍 Verificando Se Está Funcionando

Execute o script de validação:

```bash
cd bet_analysis_platform-2
.\venv\Scripts\python.exe .\scripts\validate_telegram_env.py
```

Você verá algo como:
```
TELEGRAM_BOT_TOKEN: 8347334478:AAHGap7AeSEWG1vPG1OyRjg4wHNgCCFbAjg
TELEGRAM_CHANNEL_ID: 770356893
```

---

## 📌 Alternativa: Usar Grupo

Se quiser receber sinais em um grupo:

1. Crie um grupo no Telegram
2. Adicione seu bot ao grupo
3. Execute o script `get_chat_id.py` acima
4. Envie uma mensagem no grupo
5. O ID aparecerá na resposta do script (será negativo, ex: `-1001234567890`)

---

## 🚀 Depois de Configurar

Execute o programa:

```bash
# Uma vez
.\venv\Scripts\python.exe src/main.py

# Continuamente a cada 5 minutos
.\venv\Scripts\python.exe src/main.py --scheduled
```

Você deve receber uma mensagem no Telegram quando sinais forem gerados!

---

## 💡 Resumo Rápido

| Passo | O Que Fazer |
|-------|-----------|
| 1 | Procure seu bot no Telegram |
| 2 | Envie `/start` para iniciar |
| 3 | Execute `get_chat_id.py` |
| 4 | Copie o `chat.id` da resposta |
| 5 | Atualize `.env` com seu ID real |
| 6 | Rode o programa de novo |

---

**Seu Token do Bot está certo:** ✅ `8347334478:AAHGap7AeSEWG1vPG1OyRjg4wHNgCCFbAjg`

**Seu ID que foi dado:** `770356893` (pode estar errado, valide com o script acima)

