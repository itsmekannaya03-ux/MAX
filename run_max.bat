@echo off
title MAX - My AI eXecutive Assistant
color 0b

echo ======================================================================
echo              MAX - My AI eXecutive Assistant
echo ======================================================================
echo.

:: Check for virtual environment
if not exist ".venv\Scripts\activate.bat" (
    echo [MAX] Virtual environment not found. Creating .venv...
    python -m venv .venv
    echo [MAX] Installing backend requirements...
    .\.venv\Scripts\pip install -r backend\requirements.txt
)

:: Check for frontend build
if not exist "frontend\dist\index.html" (
    echo [MAX] Building frontend desktop bundle...
    cd frontend
    call npm install
    call npm run build
    cd ..
)

echo [MAX] Starting MAX Intelligence Core on http://127.0.0.1:8000 ...
echo [MAX] Press Ctrl+C in this terminal window to stop MAX.
echo.

:: Launch the Desktop Window (Edge/Chrome App Mode or Default Browser)
start "" msedge --app=http://127.0.0.1:8000 || start http://127.0.0.1:8000

:: Run the FastAPI Uvicorn Server
.\.venv\Scripts\python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
pause

