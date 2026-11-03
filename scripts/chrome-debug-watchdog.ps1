# Watchdog: checks every 5 minutes that Chrome debug is responsive
# If it crashes, restarts it automatically

param(
    [int]$Port = 9222,
    [int]$CheckInterval = 300,
    [string]$StartScript = (Join-Path $PSScriptRoot "chrome-debug.ps1")
)

Write-Host "Watchdog started. Checking port $Port every ${CheckInterval}s..."

while ($true) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:${Port}/json/version" -TimeoutSec 5 -ErrorAction Stop
        # Chrome is alive
    }
    catch {
        Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Chrome debug not responding, restarting..."

        # Kill zombie Chrome debug processes
        $existing = Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" -ErrorAction SilentlyContinue |
            Where-Object { $_.CommandLine -like '*ChromeDebugProfile*' }
        foreach ($proc in $existing) {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 2

        & $StartScript -Port $Port
        Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Chrome debug restarted"
    }

    Start-Sleep -Seconds $CheckInterval
}
