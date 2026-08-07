# =============================================================================
# start-network.ps1 - start all backend services + the frontend
# =============================================================================
# Each backend service is self-configured by its OWN .env
# (Backend/Services/<Name>/.env). This script only reads each service's
# SERVICE_HOST / SERVICE_PORT to know where to bind, then launches it; the
# service itself loads the rest (DB, secrets, CORS, URLs) from that same .env.
# The frontend reads Frontend/.env (via vite.config.js).
#
# Logs stream to .run-logs\*.log; stop everything with stop-network.ps1.
# =============================================================================

$ErrorActionPreference = "Stop"
$root   = $PSScriptRoot
$svcDir = Join-Path $root "Backend\Services"
$feDir  = Join-Path $root "Frontend"
$logDir = Join-Path $root ".run-logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# Read KEY=VALUE pairs from a .env file into a hashtable (skip comments/blanks).
function Read-DotEnv([string]$path) {
    $map = @{}
    if (Test-Path $path) {
        Get-Content $path | ForEach-Object {
            $line = $_.Trim()
            if ($line -and -not $line.StartsWith("#") -and $line.Contains("=")) {
                $k, $v = $line -split "=", 2
                $map[$k.Trim()] = $v.Trim()
            }
        }
    }
    return $map
}

$services = @(
    "LoginServices", "UserServices", "MasterDataServices",
    "HotelServices", "RestaurantServices", "BarServices"
)

$pidFile = Join-Path $logDir "pids.txt"
Remove-Item $pidFile -ErrorAction SilentlyContinue

foreach ($name in $services) {
    $cwd = Join-Path $svcDir $name
    $svcEnv = Read-DotEnv (Join-Path $cwd ".env")
    $bind = $svcEnv["SERVICE_HOST"]; if (-not $bind) { $bind = "127.0.0.1" }
    $port = $svcEnv["SERVICE_PORT"]
    if (-not $port) { Write-Host "skip  $name - no SERVICE_PORT in its .env"; continue }

    $log = Join-Path $logDir ("{0}.log" -f $name)
    $args = @("-m", "uvicorn", "main:app", "--host", $bind, "--port", $port)
    $p = Start-Process -FilePath "python" -ArgumentList $args -WorkingDirectory $cwd `
        -RedirectStandardOutput $log -RedirectStandardError ($log + ".err") `
        -WindowStyle Hidden -PassThru
    "$name=$($p.Id)" | Add-Content $pidFile
    Write-Host ("started {0,-18} pid {1,-6} {2}:{3}" -f $name, $p.Id, $bind, $port)
}

# ---- Frontend (reads Frontend/.env via vite.config.js) ---------------------
$feEnv  = Read-DotEnv (Join-Path $feDir ".env")
$feHost = $feEnv["VITE_DEV_HOST"]; if (-not $feHost) { $feHost = "0.0.0.0" }
$fePort = $feEnv["VITE_DEV_PORT"]; if (-not $fePort) { $fePort = "5173" }
$apiBase = $feEnv["VITE_API_BASE_URL"]

$feLog = Join-Path $logDir "Frontend.log"
$fe = Start-Process -FilePath "npm.cmd" -ArgumentList @("run", "dev") -WorkingDirectory $feDir `
    -RedirectStandardOutput $feLog -RedirectStandardError ($feLog + ".err") `
    -WindowStyle Hidden -PassThru
"Frontend=$($fe.Id)" | Add-Content $pidFile
Write-Host ("started {0,-18} pid {1,-6} {2}:{3}" -f "Frontend", $fe.Id, $feHost, $fePort)

$lanHost = if ($apiBase) { ([uri]$apiBase).Host } else { "localhost" }
Write-Host ""
Write-Host "Frontend : http://$($lanHost):$($fePort)"
Write-Host "Gateway  : $apiBase"
Write-Host "Logs     : $logDir"
