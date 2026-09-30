Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -File start-network.ps1" -WindowStyle Hidden
Start-Sleep -Seconds 30
try {
    $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/healthz' -UseBasicParsing -TimeoutSec 5
    Write-Output "Gateway: $($r.StatusCode) $($r.Content)"
} catch {
    Write-Output "Gateway not ready: $_"
}
