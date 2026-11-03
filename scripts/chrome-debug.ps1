# Start Chrome with remote debugging on port 9222
# Uses a separate profile so it doesn't interfere with your normal Chrome
# Auto-hides the Chrome window so it runs invisibly in the background

param(
    [int]$Port = 9222,
    [string]$ProfilePath = "$env:USERPROFILE\ChromeDebugProfile",
    [switch]$Show   # keep the window visible (use for first-time login)
)

$chrome = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $chrome) { Write-Host "Chrome not found"; exit 1 }

# Win32 API for hiding windows
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32Hide {
    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    public const int SW_HIDE = 0;
}
"@

# Check if debug Chrome is already running
$existing = Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like "*$ProfilePath*" }

if ($existing) {
    Write-Host "Debug Chrome already running on port $Port"
    exit 0
}

Write-Host "Starting Chrome with remote debugging on port $Port..."

$chromeArgs = @(
    "--remote-debugging-port=$Port"
    "--user-data-dir=$ProfilePath"
    "--no-first-run"
    "--no-default-browser-check"
)
if (-not $Show) { $chromeArgs += "--window-position=-32000,-32000" }
Start-Process $chrome -ArgumentList $chromeArgs -WindowStyle $(if ($Show) { "Normal" } else { "Minimized" })

if ($Show) { Write-Host "Chrome debug started (visible, port $Port)"; exit 0 }

# Auto-hide: retry for up to 30 seconds until Chrome window is found and hidden
$maxAttempts = 30
$hidden = $false

for ($i = 0; $i -lt $maxAttempts; $i++) {
    Start-Sleep -Seconds 1

    $debugProcs = Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*$ProfilePath*" }

    foreach ($proc in $debugProcs) {
        $p = Get-Process -Id $proc.ProcessId -ErrorAction SilentlyContinue
        if ($p -and $p.MainWindowHandle -ne 0) {
            [Win32Hide]::ShowWindow($p.MainWindowHandle, 0) | Out-Null
            $hidden = $true
        }
    }

    if ($hidden) { break }
}

if ($hidden) {
    Write-Host "Chrome debug started and hidden (port $Port)"
} else {
    Write-Host "Chrome debug started but could not hide window (port $Port)"
}

Write-Host "Verify: http://localhost:$Port/json/version"
