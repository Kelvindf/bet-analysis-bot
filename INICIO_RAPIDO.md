## INICIO RÁPIDO - Plataforma de Análise de Apostas

### Status: ✅ TUDO PRONTO!

Seu projeto foi completamente configurado e testado. Você pode rodar agora!

---

## 1️⃣ CONFIGURE O TELEGRAM (OBRIGATÓRIO)

Abra o arquivo `.env` neste diretório e atualize:

```
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHANNEL_ID=seu_id_aqui
```

**Como obter:**
- Token: Fale com @BotFather no Telegram
- Channel ID: @userinfobot no Telegram (me)

---

## 2️⃣ EXECUTE O PROJETO

### Opção A: Execução Única (teste rápido)
```powershell
.\make.ps1
```

### Opção B: Execução Contínua (30 minutos)
```powershell
.\make.ps1 --scheduled --interval 30
```

### Opção C: Execução Manual
```powershell
.\venv\Scripts\Activate.ps1
python .\src\main.py --scheduled --interval 10
```

---

## 3️⃣ MONITORE OS LOGS

```powershell
Get-Content logs/bet_analysis.log -Wait
```

---

## O que foi corrigido/configurado:

✅ Python 3.13.9 (venv)
✅ 13 dependências instaladas
✅ Configuração de ambiente (.env)
✅ Estrutura de diretórios (logs, data)
✅ Encoding para Windows (sem erros de emojis)
✅ Testes de importação
✅ Testes de execução

---

## Comandos Importantes

| Comando | Descrição |
|---------|-----------|
| `.\make.ps1` | Executa uma vez |
| `.\make.ps1 --scheduled --interval 10` | Executa a cada 10 minutos |
| `.\make.ps1 --verbose` | Executa com logs detalhados |
| `.\make.ps1 --init-db` | Inicializa banco de dados |

---

## Estrutura Criada

```
bet_analysis_platform-2/
├── logs/              ← Arquivos de log aqui
├── data/
│   ├── raw/          ← Dados brutos
│   └── processed/    ← Dados processados
├── src/              ← Código-fonte
├── .env              ← Configure aqui!
├── make.ps1          ← Script de execução
└── venv/             ← Ambiente virtual
```

---

## Próximos Passos

1. Configure o Telegram no `.env` (CRÍTICO!)
2. Rode: `.\make.ps1`
3. Observe os logs: `Get-Content logs/bet_analysis.log -Wait`
4. Para contínuo: `.\make.ps1 --scheduled --interval 10`

---

**Qualquer dúvida, verifique os arquivos:**
- `GUIA_EXECUCAO.md` - Guia completo
- `RESUMO_CONFIGURACAO.md` - Resumo técnico

**Pronto para usar! 🚀**
