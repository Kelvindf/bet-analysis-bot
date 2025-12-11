@echo off
REM Teste rápido do quick_start.py
REM Valida se o script existe e pode ser executado

cd /d "c:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2"

echo ============================================
echo Testando quick_start.py
echo ============================================
echo.

if exist "scripts\quick_start.py" (
    echo [OK] Script quick_start.py encontrado
    echo.
    echo Para executar:
    echo   python scripts\quick_start.py
    echo.
    echo Ou do PowerShell:
    echo   .\venv\Scripts\python.exe scripts\quick_start.py
) else (
    echo [ERRO] Script quick_start.py NAO encontrado
)

echo.
echo ============================================
echo Testando validador
echo ============================================
echo.

if exist "scripts\validar_pre_coleta.py" (
    echo [OK] Script validar_pre_coleta.py encontrado
    echo Executando validador...
    echo.
    .\venv\Scripts\python.exe scripts\validar_pre_coleta.py
) else (
    echo [ERRO] Validador NAO encontrado
)
