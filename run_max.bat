@echo off
title MAX - My AI eXecutive Assistant
color 0b

REM Set working directory to the folder containing this script
cd /d "%~dp0"

echo ======================================================================
echo              MAX - My AI eXecutive Assistant
echo ======================================================================
echo.

REM 1. Check Python installation
set "PY_CMD="
python -c "import sys" >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=python"
) else (
    py -c "import sys" >nul 2>&1
    if not errorlevel 1 (
        set "PY_CMD=py"
    )
)

if "%PY_CMD%"=="" (
    color 0c
    echo [ERROR] Python was not found on this computer.
    echo.
    echo Please install Python 3.10 or newer from:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Make sure to check "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo [MAX] Found Python: %PY_CMD%

REM 2. Ensure .env exists
if not exist ".env" (
    if exist ".env.example" (
        echo [MAX] Creating initial .env configuration file...
        copy ".env.example" ".env" >nul
    )
)

REM 3. Create virtual environment if missing
if not exist ".venv\Scripts\python.exe" (
    echo [MAX] First-time setup: Creating virtual environment...
    %PY_CMD% -m venv .venv
)

if not exist ".venv\Scripts\python.exe" (
    color 0c
    echo.
    echo [ERROR] Failed to create virtual environment in .venv.
    echo Please verify Python is installed with the venv module.
    echo.
    pause
    exit /b 1
)

REM 4. Install backend dependencies if needed
if not exist ".venv\installed.flag" (
    echo [MAX] Installing backend packages. This only takes a moment on first launch...
    .\.venv\Scripts\python.exe -m pip install --upgrade pip
    .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
    if not errorlevel 1 (
        echo installed > ".venv\installed.flag"
    )
)

REM 5. Launch MAX Desktop Assistant
echo [MAX] Launching MAX Executive Assistant...
.\.venv\Scripts\python.exe launch_desktop.py

if errorlevel 1 (
    echo.
    echo [MAX] Application finished or stopped.
    pause
)
