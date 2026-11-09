@echo off
setlocal enabledelayedexpansion
title MAX - My AI eXecutive Assistant
color 0b

:: Ensure current working directory is the folder where this batch script lives
cd /d "%~dp0"

echo ======================================================================
echo              MAX - My AI eXecutive Assistant
echo ======================================================================
echo.

:: 1. Check Python installation
set "PY_CMD="
where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_CMD=py"
    )
)

if "%PY_CMD%"=="" (
    color 0c
    echo [ERROR] Python was not found on this computer!
    echo.
    echo Please install Python 3.10+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Make sure to check the box "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: 2. Ensure .env exists
if not exist ".env" (
    if exist ".env.example" (
        echo [MAX] Setting up default configuration (.env)...
        copy ".env.example" ".env" >nul
    )
)

:: 3. Setup Virtual Environment if not present
if not exist ".venv\Scripts\python.exe" (
    echo [MAX] First-time setup detected. Creating virtual environment (.venv)...
    %PY_CMD% -m venv .venv
    if not exist ".venv\Scripts\python.exe" (
        color 0c
        echo.
        echo [ERROR] Could not create virtual environment (.venv).
        echo Please ensure Python is properly installed with venv module.
        echo.
        pause
        exit /b 1
    )
    echo [MAX] Installing dependencies (this only happens once)...
    .\.venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
    .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
    if %errorlevel% neq 0 (
        echo.
        echo [WARNING] Some dependencies had warnings during installation. Continuing...
    )
)

:: 4. Launch Desktop Application using verified healthcheck launcher
echo [MAX] Initializing MAX Desktop Assistant...
.\.venv\Scripts\python.exe launch_desktop.py

if %errorlevel% neq 0 (
    echo.
    echo [MAX] Application exited with code %errorlevel%.
    pause
)
