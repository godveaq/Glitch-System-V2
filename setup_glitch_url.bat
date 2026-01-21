@echo off
echo This script will add an entry to your hosts file to enable access to http://glitch
echo.
echo WARNING: This script needs administrator privileges to modify the hosts file.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrator privileges.
    echo Right-click on this file and select "Run as administrator".
    pause
    exit /b 1
)

set HOSTS_FILE=C:\Windows\System32\drivers\etc\hosts
set NEW_ENTRY=127.0.0.1 glitch

REM Check if the entry already exists
findstr /C:"%NEW_ENTRY%" "%HOSTS_FILE%" >nul
if %errorlevel% equ 0 (
    echo Entry already exists in hosts file.
    echo You can now access Glitcher at http://glitch
    pause
    exit /b 0
)

REM Add the entry to the hosts file
echo.%NEW_ENTRY% >> "%HOSTS_FILE%"
if %errorlevel% equ 0 (
    echo Successfully added entry to hosts file.
    echo You can now access Glitcher at http://glitch
) else (
    echo Failed to add entry to hosts file.
    echo Please check permissions or add the entry manually:
    echo %NEW_ENTRY%
)

pause