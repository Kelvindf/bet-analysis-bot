@echo off
REM Executar Sistema de Sinais
REM
REM Este arquivo executa o sistema usando o Python correto do venv

cd /d "%~dp0"
echo ============================================================
echo   Sistema de Sinais - Iniciando...
echo ============================================================
echo.

venv\Scripts\python.exe src\main.py --scheduled --interval 1

pause
