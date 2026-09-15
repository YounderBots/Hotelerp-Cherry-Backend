# =============================================================================
# start-network.ps1 - start all backend services + the frontend
# =============================================================================
# Each backend service is self-configured by its OWN .env
# (Backend/Services/<Name>/.env). This script only reads each service's
# SERVICE_HOST / SERVICE_PORT to know where to bind, then launches it; the
# service itself loads the rest (DB, secrets, CORS, URLs) from that same .env.
# The frontend reads Frontend/.env (via vite.config.js).
#
# POSIX parity: run.sh does the same job and carries the same guards. Keep the
# two in step.
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
# Never sourced as script: a .env holds secrets and must not be executed.
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

function Test-PortBusy([int]$port) {
    try {
        $conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction Stop
        return [bool]$conn
    } catch {
        return $false
    }
}

# "started" is not the same as "listening". A service whose .env points at a
# database that is not there starts, throws during the first request, and
# leaves a one-line log -- while a script that only reports the launch says
# six successes. Ask each one whether it is actually answering.
function Wait-ForService([string]$name, [int]$port, [string]$path) {
    for ($i = 0; $i -lt 40; $i++) {
        try {
            $r = Invoke-WebRequest -Uri "http://127.0.0.1:$port$path" -TimeoutSec 2 -UseBasicParsing
            if ($r.StatusCode -eq 200) { return $true }
        } catch { }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

$services = @(
    "LoginServices", "UserServices", "MasterDataServices",
    "HotelServices", "RestaurantServices", "BarServices"
)

$pidFile = Join-Path $logDir "pids.txt"
Remove-Item $pidFile -ErrorAction SilentlyContinue

$started = @()
$failed  = @()

foreach ($name in $services) {
    $cwd = Join-Path $svcDir $name
    $envPath = Join-Path $cwd ".env"
    if (-not (Test-Path $envPath)) {
        Write-Host "skip  $name - no .env (copy from Backend\Services\.env.example)"
        continue
    }
    $svcEnv = Read-DotEnv $envPath
    # Default to loopback, never 0.0.0.0: a service that forgets to declare a
    # bind address must stay private rather than becoming reachable.
    $bind = $svcEnv["SERVICE_HOST"]; if (-not $bind) { $bind = "127.0.0.1" }
    $port = $svcEnv["SERVICE_PORT"]
    if (-not $port) { Write-Host "skip  $name - no SERVICE_PORT in its .env"; continue }

    if (Test-PortBusy ([int]$port)) {
        Write-Host "skip  $name - port $port is already in use (already running?)"
        continue
    }

    $log = Join-Path $logDir ("{0}.log" -f $name)
    $uvicornArgs = @("-m", "uvicorn", "main:app", "--host", $bind, "--port", $port)
    $p = Start-Process -FilePath "python" -ArgumentList $uvicornArgs -WorkingDirectory $cwd `
        -RedirectStandardOutput $log -RedirectStandardError ($log + ".err") `
        -WindowStyle Hidden -PassThru
    "$name=$($p.Id)" | Add-Content $pidFile
    Write-Host ("starting {0,-18} pid {1,-6} {2}:{3}" -f $name, $p.Id, $bind, $port)
    $started += , @($name, [int]$port, "/healthz")
}

# ---- Frontend (reads Frontend/.env via vite.config.js) ---------------------
$feEnv  = Read-DotEnv (Join-Path $feDir ".env")
$feHost = $feEnv["VITE_DEV_HOST"]; if (-not $feHost) { $feHost = "0.0.0.0" }
$fePort = $feEnv["VITE_DEV_PORT"]; if (-not $fePort) { $fePort = "5173" }
$apiBase = $feEnv["VITE_API_BASE_URL"]

if (-not (Test-Path (Join-Path $feDir "node_modules"))) {
    Write-Host "skip  Frontend - node_modules missing (run: cd Frontend; npm install)"
} elseif (Test-PortBusy ([int]$fePort)) {
    Write-Host "skip  Frontend - port $fePort is already in use (already running?)"
} else {
    # Vite's entry script is run DIRECTLY, not through `npm run dev`. npm sits
    # in the middle as a parent process, so the pid recorded here would be the
    # wrapper's: stop-network.ps1 kills it, node keeps running, and the dev
    # server carries on holding the port while claiming to be stopped. run.sh
    # makes the same choice for the same reason.
    $viteEntry = Join-Path $feDir "node_modules\vite\bin\vite.js"
    $feLog = Join-Path $logDir "Frontend.log"
    $fe = Start-Process -FilePath "node" `
        -ArgumentList @($viteEntry, "--host", $feHost, "--port", $fePort) `
        -WorkingDirectory $feDir `
        -RedirectStandardOutput $feLog -RedirectStandardError ($feLog + ".err") `
        -WindowStyle Hidden -PassThru
    "Frontend=$($fe.Id)" | Add-Content $pidFile
    Write-Host ("starting {0,-18} pid {1,-6} {2}:{3}" -f "Frontend", $fe.Id, $feHost, $fePort)
    # Vite has no /healthz; any answer on / means it is serving.
    $started += , @("Frontend", [int]$fePort, "/")
}

# ---- Verify ----------------------------------------------------------------
if ($started.Count -gt 0) {
    Write-Host ""
    Write-Host "waiting for services to answer..."
    foreach ($entry in $started) {
        $name = $entry[0]; $port = $entry[1]; $probe = $entry[2]
        if (Wait-ForService $name $port $probe) {
            Write-Host ("  ok    {0,-18} http://127.0.0.1:{1}" -f $name, $port)
        } else {
            $log = Join-Path $logDir ("{0}.log" -f $name)
            Write-Host ("  FAIL  {0,-18} see {1}" -f $name, $log)
            if (Test-Path $log) { Get-Content $log -Tail 3 | ForEach-Object { "          $_" } }
            $failed += $name
        }
    }
}

Write-Host ""
Write-Host "Frontend : http://localhost:$fePort"
Write-Host "Gateway  : $apiBase"
Write-Host "PIDs     : $pidFile"
Write-Host "Logs     : $logDir"

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host ("FAILED: {0}" -f ($failed -join ", "))
    exit 1
}
