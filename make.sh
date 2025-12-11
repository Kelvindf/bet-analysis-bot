#!/usr/bin/env bash
set -e

# Detect OS
OS_NAME="$(uname -s)"

# 1) Create venv if missing
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# 2) Activate venv
if [[ "$OS_NAME" == "Darwin" || "$OS_NAME" == "Linux" ]]; then
  source venv/bin/activate
else
  # Fallback for environments that treat bash on Windows
  source venv/Scripts/activate
fi

# 3) Install requirements (if file exists)
if [ -f "requirements.txt" ]; then
  pip install --upgrade pip
  pip install -r requirements.txt
fi

# 4) Ensure .env exists
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  cp .env.example .env
  echo "[make.sh] .env criado a partir de .env.example - ajuste os valores conforme necessário."
fi

# 5) Parse custom flags
VERBOSE=""
INIT_DB=""
ARGS=()
for arg in "$@"; do
  case "$arg" in
    --verbose) VERBOSE="1" ;;
    --init-db) INIT_DB="1" ;;
    *) ARGS+=("$arg") ;;
  esac
done

# 6) Optionally set verbose logs
if [ "$VERBOSE" = "1" ]; then
  export LOG_LEVEL=DEBUG
  echo "[make.sh] LOG_LEVEL=DEBUG"
fi

# 7) Optionally init DB
if [ "$INIT_DB" = "1" ]; then
  echo "[make.sh] Inicializando banco de dados..."
  python scripts/init_db.py
fi

# 8) Run the app (pass-through args)
python src/main.py "${ARGS[@]}"

