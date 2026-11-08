import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def main():
    print("=" * 65)
    print("        MAX — My AI eXecutive Assistant Desktop Launcher")
    print("=" * 65)

    python_exe = BASE_DIR / ".venv" / "Scripts" / "python.exe"
    if not python_exe.exists():
        python_exe = sys.executable

    # Build frontend if dist doesn't exist
    dist_index = BASE_DIR / "frontend" / "dist" / "index.html"
    if not dist_index.exists():
        print("[MAX] Building frontend assets...")
        subprocess.run(["npm", "run", "build"], cwd=str(BASE_DIR / "frontend"), shell=True)

    print("[MAX] Starting server at http://127.0.0.1:8000 ...")
    
    # Open desktop app window
    time.sleep(1)
    app_url = "http://127.0.0.1:8000"
    try:
        # Launch in native app mode using Edge
        subprocess.Popen(f'start "" msedge --app={app_url}', shell=True)
    except Exception:
        webbrowser.open(app_url)

    # Launch uvicorn
    cmd = [str(python_exe), "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000"]
    subprocess.run(cmd, cwd=str(BASE_DIR))

if __name__ == "__main__":
    main()

