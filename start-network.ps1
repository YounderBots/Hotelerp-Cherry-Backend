# =============================================================================
# start-network.ps1 — bring HotelERP up for LAN access
# =============================================================================
# Binds the gateway (8000) and the Vite frontend (5173) to 0.0.0.0 so other
# devices on the Wi-Fi can reach them. The five downstream services stay on
# 127.0.0.1: only the gateway talks to them, and exposing them would bypass the
# gateway's auth/rate-limit layer.
#
#   Frontend : http://<LAN_HOST>:5173
#   Gateway  : http://<LAN_HOST>:8000
#
# Logs stream to .run-logs\*.log. Stop everything with stop-network.ps1.
# =============================================================================

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$svcDir = Join-Path $root "Backend\Services"
$logDir = Join-Path $root ".run-logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# ---- Load root .env into this process --------------------------------------
$envFile = Join-Path $root ".env"
if (-not (Test-Path $envFile)) { throw ".env not found at $envFile" }
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
        $k, $v = $line -split "=", 2
        Set-Item -Path ("Env:" + $k.Trim()) -Value $v.Trim()
    }
}

$lanHost = $env:LAN_HOST
if (-not $lanHost) { throw "LAN_HOST not set in .env" }
$dbBase = $env:DB_URL_BASE
if (-not $dbBase) { throw "DB_URL_BASE not set in .env" }

# ---- Service table: name, port (loopback), schema --------------------------
# The gateway is bound to 0.0.0.0; the rest to 127.0.0.1.
$services = @(
    @{ Name = "LoginServices";      Port = 8000; Schema = "hotelerp_users";      Bind = "0.0.0.0"   },
    @{ Name = "UserServices";       Port = 8020; Schema = "hotelerp_users";      Bind = "127.0.0.1" },
    @{ Name = "MasterDataServices"; Port = 8030; Schema = "hotelerp_masterdata"; Bind = "127.0.0.1" },
    @{ Name = "HotelServices";      Port = 8040; Schema = "hotelerp_hotel";      Bind = "127.0.0.1" },
    @{ Name = "RestaurantServices"; Port = 8050; Schema = "hotelerp_restaurant"; Bind = "127.0.0.1" },
    @{ Name = "BarServices";        Port = 8060; Schema = "hotelerp_bar";        Bind = "127.0.0.1" }
)

$pidFile = Join-Path $logDir "pids.txt"
Remove-Item $pidFile -ErrorAction SilentlyContinue

foreach ($s in $services) {
    $cwd = Join-Path $svcDir $s.Name
    $dbUri = "$dbBase/$($s.Schema)"
    $log = Join-Path $logDir ("{0}.log" -f $s.Name)

    # Per-service env: DB_URI is the only value that differs; everything else was
    # already exported from .env above and is inherited by the child.
    $env:DB_URI = $dbUri

    $args = @("-m", "uvicorn", "main:app", "--host", $s.Bind, "--port", "$($s.Port)")
    $p = Start-Process -FilePath "python" -ArgumentList $args -WorkingDirectory $cwd `
        -RedirectStandardOutput $log -RedirectStandardError ($log + ".err") `
        -WindowStyle Hidden -PassThru
    "$($s.Name)=$($p.Id)" | Add-Content $pidFile
    Write-Host ("started {0,-18} pid {1,-6} {2}:{3}  db={4}" -f $s.Name, $p.Id, $s.Bind, $s.Port, $s.Schema)
}

# ---- Frontend (Vite) on the LAN --------------------------------------------
$feDir = Join-Path $root "Frontend"
$feLog = Join-Path $logDir "Frontend.log"
$feArgs = @("run", "dev", "--", "--host", "0.0.0.0", "--port", "5173", "--strictPort")
$fe = Start-Process -FilePath "npm.cmd" -ArgumentList $feArgs -WorkingDirectory $feDir `
    -RedirectStandardOutput $feLog -RedirectStandardError ($feLog + ".err") `
    -WindowStyle Hidden -PassThru
"Frontend=$($fe.Id)" | Add-Content $pidFile
Write-Host ("started {0,-18} pid {1,-6} 0.0.0.0:5173" -f "Frontend", $fe.Id)

Write-Host ""
Write-Host "Frontend : http://$lanHost:5173"
Write-Host "Gateway  : http://$lanHost:8000"
Write-Host "Logs     : $logDir"
