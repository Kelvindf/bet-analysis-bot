@echo off
REM Sistema de Sinais - Executar
REM Este arquivo deve estar na pasta bet_analysis_platform-2

echo ============================================================
echo   🚀 Sistema de Sinais - Iniciando...
echo ============================================================
echo.
echo Verificando diretorio...

IF NOT EXIST "src\main.py" (
    echo [ERRO] Arquivo src\main.py nao encontrado!
    echo.
    echo Voce esta no diretorio: %CD%
    echo.
    echo Execute este arquivo de dentro de:
    echo bet_analysis_platform-2\
    echo.
    pause
    exit /b 1
)

echo [OK] Arquivo encontrado!
echo.
echo Iniciando sistema com Python do venv...
echo.

venv\Scripts\python.exe src\main.py --scheduled --interval 1

echo.
echo ============================================================
echo   Sistema finalizado
echo ============================================================
pause
