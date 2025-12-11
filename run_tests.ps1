# Script para executar os testes em PowerShell puro
$proj = 'C:\Users\Trampo\Downloads\ChamaeledePlataformaX\bet_analysis_platform-2'
$py = Join-Path $proj 'venv\Scripts\python.exe'

Write-Output "========================================================================"
Write-Output "TESTE 1: run_one_cycle_test.py (ciclo completo com test_mode=True)"
Write-Output "========================================================================"
& $py (Join-Path $proj 'scripts\run_one_cycle_test.py') 2>&1

Write-Output "`n========================================================================"
Write-Output "TESTE 2: force_send_test_message.py (envio forcado de mensagem)"
Write-Output "========================================================================"
& $py (Join-Path $proj 'scripts\force_send_test_message.py') 2>&1

Write-Output "`n========================================================================"
Write-Output "LOGS RECENTES: bet_analysis.log (tail 100 lines)"
Write-Output "========================================================================"
if (Test-Path (Join-Path $proj 'logs\bet_analysis.log')) {
    Get-Content -Path (Join-Path $proj 'logs\bet_analysis.log') -Tail 100
} else {
    Write-Output "Arquivo bet_analysis.log nao encontrado"
}

Write-Output "`n========================================================================"
Write-Output "LOGS RECENTES: pipeline_stats.json (tail 30 lines)"
Write-Output "========================================================================"
if (Test-Path (Join-Path $proj 'logs\pipeline_stats.json')) {
    Get-Content -Path (Join-Path $proj 'logs\pipeline_stats.json') -Tail 30
} else {
    Write-Output "Arquivo pipeline_stats.json nao encontrado"
}

Write-Output "`n========================================================================"
Write-Output "FIM DOS TESTES"
Write-Output "========================================================================"
