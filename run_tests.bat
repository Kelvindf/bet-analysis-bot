@echo off
REM Script para executar os testes
setlocal enabledelayedexpansion

set PROJ=C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2
set PY=!PROJ!\venv\Scripts\python.exe

echo.
echo ========================================================================
echo TESTE 1: run_one_cycle_test.py (ciclo completo com test_mode=True)
echo ========================================================================
"!PY!" "!PROJ!\scripts\run_one_cycle_test.py"

echo.
echo ========================================================================
echo TESTE 2: force_send_test_message.py (envio forcado de mensagem)
echo ========================================================================
"!PY!" "!PROJ!\scripts\force_send_test_message.py"

echo.
echo ========================================================================
echo LOGS RECENTES: bet_analysis.log (tail 100 lines)
echo ========================================================================
powershell -NoProfile -Command "if(Test-Path '!PROJ!\logs\bet_analysis.log'){ Get-Content -Path '!PROJ!\logs\bet_analysis.log' -Tail 100 } else { Write-Output 'Arquivo nao encontrado' }"

echo.
echo ========================================================================
echo LOGS RECENTES: pipeline_stats.json (tail 30 lines)
echo ========================================================================
powershell -NoProfile -Command "if(Test-Path '!PROJ!\logs\pipeline_stats.json'){ Get-Content -Path '!PROJ!\logs\pipeline_stats.json' -Tail 30 } else { Write-Output 'Arquivo nao encontrado' }"

echo.
echo ========================================================================
echo FIM DOS TESTES
echo ========================================================================
