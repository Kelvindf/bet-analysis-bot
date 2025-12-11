# 🎯 Plataforma de Análise de Apostas

Plataforma para análise estatística de dados de apostas e envio de sinais via Telegram.

## ⚡ Funcionalidades

- 📊 Coleta de dados em tempo real da Blaze
- 📈 Análise estatística de padrões
- 🔔 Geração de sinais baseados em confiança
- 🤖 Envio automático para Telegram
- ⚙️ Configuração flexível

## 🚀 Instalação

1. **Clone o projeto**:

## Execução rápida (scripts)
Escolha o script conforme seu sistema e execute a partir da raiz do projeto:

**macOS/Linux (bash)**
```bash
chmod +x make.sh
./make.sh            # execução padrão
./make.sh --scheduled --interval 10
```

**Windows (CMD)**
```cmd
make.cmd
make.cmd --scheduled --interval 10
```

**Windows (PowerShell)**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\make.ps1
.\make.ps1 --scheduled --interval 10
```
Os scripts:
- Criam/ativam o `venv` automaticamente.
- Instalam `requirements.txt` (se existir).
- Geram `.env` a partir de `.env.example` (se ainda não existir).
- Executam `python src/main.py` passando os argumentos opcionais.

---

## Banco de Dados e Tabelas
Para criar/atualizar as tabelas localmente (fora do Docker):
```bash
# macOS/Linux
./make.sh --init-db
# Windows (CMD)
make.cmd --init-db
# Windows (PowerShell)
.\make.ps1 --init-db
```

O script usa `DATABASE_URL` (ou POSTGRES_* do `.env`). O SQL base está em `scripts/create_tables.sql`.

## Logs Verbosos
Use `--verbose` para ativar `LOG_LEVEL=DEBUG`.
```bash
./make.sh --verbose --scheduled --interval 10
make.cmd --verbose
.\make.ps1 --verbose
```

## Docker (app + Postgres + Adminer)
1. Copie `.env.example` para `.env` e ajuste se necessário.
2. Suba os serviços:
```bash
docker compose up --build
```
- App: inicia, aguarda o DB, roda `init_db.py` e executa `src/main.py --scheduled`.
- Postgres: disponível em `localhost:5432` (user/pass/db no `.env`).
- Adminer: acesse http://localhost:8080 (Server: `db`, User/Pass do `.env`).

Para derrubar:
```bash
docker compose down
```

## Dicas
- Os logs do app ficam em tempo real no console (PYTHONUNBUFFERED=1).
- Ajuste o comando do serviço `app` no `docker-compose.yml` se quiser modo não-agendado.
- Se seu `src/main.py` já configura logging, o `LOG_LEVEL` será apenas um padrão; pode sobrepor no seu código.
