Write-Host "This script will add an entry to your hosts file to enable access to http://glitch" -ForegroundColor Yellow
Write-Host ""
Write-Host "WARNING: This script needs administrator privileges to modify the hosts file." -ForegroundColor Red
Write-Host ""
Write-Host "Press any key to continue or Ctrl+C to cancel..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "This script requires administrator privileges." -ForegroundColor Red
    Write-Host "Right-click on this file and select 'Run as administrator'." -ForegroundColor Red
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

$hostsFile = "C:\Windows\System32\drivers\etc\hosts"
$newEntry = "127.0.0.1 glitch"

# Check if the entry already exists
$hostsContent = Get-Content $hostsFile -Raw
if ($hostsContent -match [regex]::Escape($newEntry)) {
    Write-Host "Entry already exists in hosts file." -ForegroundColor Green
    Write-Host "You can now access Glitcher at http://glitch" -ForegroundColor Green
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 0
}

# Add the entry to the hosts file
try {
    Add-Content -Path $hostsFile -Value "`n$newEntry" -Encoding ASCII
    Write-Host "Successfully added entry to hosts file." -ForegroundColor Green
    Write-Host "You can now access Glitcher at http://glitch" -ForegroundColor Green
}
catch {
    Write-Host "Failed to add entry to hosts file." -ForegroundColor Red
    Write-Host "Please check permissions or add the entry manually:" -ForegroundColor Yellow
    Write-Host $newEntry -ForegroundColor Yellow
}

$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")