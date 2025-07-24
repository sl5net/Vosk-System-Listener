:: start this script like: & .\start_dictation_v2.0.bat
:: Version: v2.0
:: Change: Added automatic self-repair. If 'requests' module is missing
::         in venv, it automatically deletes and rebuilds the environment.
:: Purpose: The final, one-click solution. Handles admin rights, setup,
::          self-repair, and launches the application.

@echo off
setlocal
title SL5 Dictation - One-Click Starter

:: --- Step 1: Set correct working directory ---
cd /d "%~dp0"

:: --- Step 2: Ensure Administrator privileges ---
echo [*] Checking for Administrator privileges
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [INFO] Administrative privileges needed. Relaunching
    powershell.exe -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)
echo [SUCCESS] Running with Administrator privileges.
echo.

:: --- Step 3: Check virtual environment health and auto-repair ---
set VENV_HEALTHY=true
if not exist ".\.venv" (
    set VENV_HEALTHY=false
) else (
    :: echo -31-
    :: .venv/Scripts/activate
    echo -33-
    echo [*] Performing venv health check (checking for 'requests' module)
    ".\.venv\scripts\python" -c "import requests" >nul 2>&1
    if %errorLevel% NEQ 0 (
        echo [WARNING] Health check failed. 'requests' module not found in venv.
        set VENV_HEALTHY=false
    ) else (
       echo [SUCCESS] Virtual environment is healthy.
    )
)
echo -40-

if "%VENV_HEALTHY%"=="false" (
    echo [ACTION] Rebuilding the virtual environment. This may take a moment.
    if exist ".\.venv" (
        echo [INFO] Removing outdated virtual environment
        rmdir /s /q .\.venv
    )
    echo [INFO] Running full setup
    powershell.exe -ExecutionPolicy Bypass -File ".\setup\windows11_setup.ps1"

    echo [INFO] Re-validating environment after rebuild
    if not exist ".\.venv\Scripts\python" (
        echo [FATAL] Automated setup failed. Please check setup script.
        pause
        exit /b
    )
    echo [SUCCESS] Virtual environment has been rebuilt successfully.
)
echo.
echo -63-

:: Forcefully terminate any running AutoHotkey process
:: this is very importend! becouse the restart feature of a AutoHotkey-Script is buggy!!
:: never delete the follwong taskkill lines.
echo [*] Ensuring a clean start for watchers by terminating AutoHotkey processes
taskkill /F /IM AutoHotkey.exe >nul 2>&1
taskkill /F /IM AutoHotkey64.exe >nul 2>&1

start "SL5 Type Watcher" type_watcher.ahk
start "SL5 Notification Watcher" scripts\notification_watcher.ahk


echo -72-

echo [INFO] Aktiviere die virtuelle Python-Umgebung...
:: 'call' wird verwendet, damit die Umgebung im selben Fenster aktiv bleibt
call .\.venv\Scripts\activate.bat
if %errorLevel% NEQ 0 (
    echo [FATAL] Konnte die virtuelle Umgebung nicht aktivieren.
    pause
    exit /b
)

echo [INFO] Virtuelle Umgebung ist aktiv.
echo [INFO] Starte den Python STT Backend-Server...

python -u dictation_service.py

:: --- Step 4: Launch all application components ---
:: echo [*] Launching SL5 Dictation components in the background
:: start "SL5 STT Backend" cmd /k "call .\scripts\restart_venv_and_run-server.sh > .\log\restart_venv_and_run-server_pre.log 2>&1"




:: --- Step 4: Trigger the service ---
echo [*] Triggering the service using the vosk_trigger file
echo. >> "c:/tmp/vosk_trigger"
echo -84-

echo [SUCCESS] SL5 Dictation is now running in the background.
echo This window will close automatically.
timeout /t 4 > nul

