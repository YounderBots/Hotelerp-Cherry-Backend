# Stops every process started by start-network.ps1 (reads .run-logs\pids.txt).
$pidFile = Join-Path $PSScriptRoot ".run-logs\pids.txt"
if (-not (Test-Path $pidFile)) { Write-Host "no pids.txt - nothing to stop"; return }
Get-Content $pidFile | ForEach-Object {
    $name, $procId = $_ -split "="
    try {
        Stop-Process -Id ([int]$procId) -Force -ErrorAction Stop
        Write-Host "stopped $name (pid $procId)"
    } catch {
        Write-Host "skip $name (pid $procId): already gone"
    }
}
Remove-Item $pidFile -ErrorAction SilentlyContinue
