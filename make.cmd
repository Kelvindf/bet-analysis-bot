@echo off
setlocal enabledelayedexpansion
REM 1) Create venv if missing
if not exist venv (
  python -m venv venv
)

REM 2) Activate venv
call venv\Scripts\activate

REM 3) Install requirements (if file exists)
if exist requirements.txt (
  python -m pip install --upgrade pip
  pip install -r requirements.txt
)

REM 4) Ensure .env exists
if not exist .env (
  if exist .env.example (
    copy /Y .env.example .env >nul
    echo [make.cmd] .env criado a partir de .env.example - ajuste os valores conforme necessário.
  )
)

REM 5) Run the app (pass through args like --scheduled --interval 10)
\
            set LOG_LEVEL=
            set INIT_DB=0
            set VERBOSE=0
            set ARGS=

            :parse
            if "%~1"=="" goto after_parse
            if "%~1"=="--init-db" (
              set INIT_DB=1
            ) else if "%~1"=="--verbose" (
              set VERBOSE=1
            ) else (
              set ARGS=%ARGS% %1
            )
            shift
            goto parse

            :after_parse
            if %VERBOSE%==1 (
              set LOG_LEVEL=DEBUG
              echo [make.cmd] LOG_LEVEL=DEBUG
            )
            if %INIT_DB%==1 (
              echo [make.cmd] Inicializando banco de dados...
              python scripts\init_db.py
            )
            python src\main.py %ARGS%

