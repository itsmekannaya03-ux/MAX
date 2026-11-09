import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

if __name__ == "__main__":
    venv_python = BASE_DIR / ".venv" / "Scripts" / "python.exe"
    launcher = BASE_DIR / "launch_desktop.py"

    if venv_python.exists():
        os.execv(str(venv_python), [str(venv_python), str(launcher)])
    else:
        import launch_desktop
        launch_desktop.main()
