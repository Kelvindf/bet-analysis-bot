$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.CommandLine -match 'src\\main.py' }
if ($procs) {
    foreach ($p in $procs) {
        Write-Output ("Stopping PID:{0} - {1}" -f $p.ProcessId, $p.CommandLine)
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Output 'No processes matching src\\main.py found.'
}
