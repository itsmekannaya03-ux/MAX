import os
import sys
import time
import subprocess
import webbrowser
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def check_server_health(url="http://127.0.0.1:8000/api/health", timeout=35):
    """Waits until the server is actually responding before opening browser."""
    start_time = time.time()
    print("[MAX] Waiting for intelligence core to boot...", end="", flush=True)
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "MAX-Launcher"})
            with urllib.request.urlopen(req, timeout=1.5) as response:
                if response.status == 200:
                    print(" READY!")
                    return True
        except Exception:
            print(".", end="", flush=True)
            time.sleep(0.6)
    print(" TIMEOUT!")
    return False

def open_desktop_window(url="http://127.0.0.1:8000"):
    """Launches app window in Edge (standalone app frame) or default browser."""
    print(f"[MAX] Launching executive interface at {url} ...")
    try:
        # Try native Edge App Mode (clean frameless window)
        edge_proc = subprocess.Popen(f'start "" msedge --app={url}', shell=True)
    except Exception:
        webbrowser.open(url)

def main():
    print("=" * 65)
    print("        MAX — My AI eXecutive Assistant Desktop Launcher")
    print("=" * 65)
    print()

    # Ensure .env exists
    env_file = BASE_DIR / ".env"
    env_example = BASE_DIR / ".env.example"
    if not env_file.exists() and env_example.exists():
        print("[MAX] Creating .env from .env.example...")
        with open(env_example, "r", encoding="utf-8") as src, open(env_file, "w", encoding="utf-8") as dst:
            dst.write(src.read())

    python_exe = sys.executable

    # Verify frontend dist exists
    dist_html = BASE_DIR / "frontend" / "dist" / "index.html"
    if not dist_html.exists():
        print("[MAX] Notice: frontend/dist not found. Serving API mode or build frontend with npm run build.")

    # Start Uvicorn process
    cmd = [
        python_exe, "-m", "uvicorn", "backend.app.main:app",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--log-level", "info"
    ]
    print("[MAX] Starting FastAPI server process...")
    server_proc = subprocess.Popen(cmd, cwd=str(BASE_DIR))

    # Wait for server to become responsive
    is_live = check_server_health("http://127.0.0.1:8000/api/health", timeout=30)

    if is_live:
        open_desktop_window("http://127.0.0.1:8000")
        print("\n[MAX] MAX is now running successfully!")
        print("[MAX] Leave this terminal window open while using MAX.")
        print("[MAX] Press Ctrl+C to stop MAX.\n")
    else:
        print("\n[ERROR] Server failed to respond in time.")
        print("[ERROR] Please check terminal logs above for any traceback.")

    try:
        server_proc.wait()
    except KeyboardInterrupt:
        print("\n[MAX] Stopping server gracefully...")
        server_proc.terminate()
        try:
            server_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_proc.kill()
        print("[MAX] Shutdown complete.")

if __name__ == "__main__":
    main()

