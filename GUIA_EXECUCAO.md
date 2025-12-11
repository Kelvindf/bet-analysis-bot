# Guia de Execução - Plataforma de Análise de Apostas

## Status do Projeto ✓

Seu projeto está **100% pronto para rodar**! Todas as dependências foram instaladas e configuradas.

---

## Como Executar

### Opção 1: Script Automático (RECOMENDADO)

Execute o script que faz tudo automaticamente:

```powershell
.\make.ps1
```

**Ou com modo agendado:**

```powershell
.\make.ps1 --scheduled --interval 10
```

---

### Opção 2: Execução Manual

Se preferir rodar manualmente:

```powershell
# 1. Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# 2. Executar análise única
python .\src\main.py

# 3. Ou executar em modo agendado (a cada 10 minutos)
python .\src\main.py --scheduled --interval 10
```

---

## Configuração do Telegram

⚠️ **IMPORTANTE:** O arquivo `.env` já está configurado com valores padrão, mas você **DEVE** atualizá-lo:

1. Abra o arquivo `.env` na raiz do projeto
2. Procure por `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHANNEL_ID`
3. Substitua pelos seus valores reais:
   - **TELEGRAM_BOT_TOKEN**: Obtenha do @BotFather no Telegram
   - **TELEGRAM_CHANNEL_ID**: ID do seu canal/chat no Telegram

**Exemplo:**
```
TELEGRAM_BOT_TOKEN=123456789:ABCDefGHIjklmnoPQRstuvWXYZ
TELEGRAM_CHANNEL_ID=9876543210
```

---

## Estrutura do Projeto

```
bet_analysis_platform-2/
├── src/                          # Código-fonte
│   ├── main.py                   # Ponto de entrada
│   ├── config/settings.py        # Configurações
│   ├── data_collection/          # Coleta de dados da Blaze
│   ├── analysis/                 # Análise estatística
│   └── telegram_bot/             # Gerenciador do Telegram
├── data/
│   ├── raw/                      # Dados brutos coletados
│   └── processed/                # Dados processados
├── logs/                         # Arquivos de log
├── requirements.txt              # Dependências Python
├── .env                          # Variáveis de ambiente
└── make.ps1                      # Script de execução
```

---

## Funcionalidades

- ✅ **Coleta de Dados**: Busca dados em tempo real da API Blaze
- ✅ **Análise Estatística**: Analisa padrões usando scikit-learn e scipy
- ✅ **Geração de Sinais**: Cria sinais baseados em confiança (threshold: 65%)
- ✅ **Envio via Telegram**: Notifica sinais via bot do Telegram
- ✅ **Modo Agendado**: Executa análises em intervalos regulares
- ✅ **Logging Completo**: Registra todos os eventos em `logs/bet_analysis.log`

---

## Modo Agendado (--scheduled)

O modo agendado permite que a plataforma execute análises automaticamente:

```powershell
# Executa a cada 5 minutos (padrão do .env)
.\make.ps1 --scheduled

# Executa a cada 10 minutos
.\make.ps1 --scheduled --interval 10

# Executa a cada 30 minutos
.\make.ps1 --scheduled --interval 30
```

Para sair do modo agendado, pressione **Ctrl+C**.

---

## Logs e Monitoramento

Os logs são salvos em `logs/bet_analysis.log` e também aparecem no console.

Para visualizar os logs em tempo real:

```powershell
# Windows PowerShell
Get-Content logs/bet_analysis.log -Wait

# Ou no terminal
tail -f logs/bet_analysis.log
```

---

## Variáveis de Ambiente (.env)

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `TELEGRAM_BOT_TOKEN` | Token do bot Telegram | *(configure)* |
| `TELEGRAM_CHANNEL_ID` | ID do canal/chat | *(configure)* |
| `BLAZE_API_URL` | URL da API Blaze | `https://api.blaze.com` |
| `ANALYSIS_INTERVAL_MINUTES` | Intervalo de análise | `5` |
| `MIN_CONFIDENCE_LEVEL` | Confiança mínima para sinais | `0.65` |
| `LOG_LEVEL` | Nível de log | `INFO` |

---

## Troubleshooting

### Erro: "requirements.txt não encontrado"
- **Solução**: Execute do diretório raiz do projeto (onde está `make.ps1`)

### Erro: "Módulos não encontrados"
- **Solução**: Certifique-se de que o venv está ativado
- ```powershell
  .\venv\Scripts\Activate.ps1
  ```

### Erro: "Sem dados coletados"
- **Verificação**: A API da Blaze pode estar indisponível
- **Solução**: Verifique `logs/bet_analysis.log` para mais detalhes

### Bot não está enviando mensagens
- **Verificação**: Confira o `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHANNEL_ID` no `.env`
- **Teste**: Envie uma mensagem manual para o bot no Telegram
- **Log**: Verifique `logs/bet_analysis.log` para erros

---

## Próximos Passos

1. ✅ Configure o `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHANNEL_ID` no `.env`
2. ✅ Execute: `.\make.ps1` para teste rápido
3. ✅ Execute: `.\make.ps1 --scheduled --interval 10` para modo contínuo
4. 📊 Monitore os logs em tempo real
5. 🚀 Ajuste os parâmetros conforme necessário

---

**Pronto para usar!** 🎉
