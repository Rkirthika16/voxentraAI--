"""VoxentraAI Streamlit Frontend Entrypoint."""
import os
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STREAMLIT_APP_FILE = Path(__file__).resolve().parent / "streamlit_app.py"

if __name__ == "__main__":
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(STREAMLIT_APP_FILE)])
else:
    # If loaded as a module or by Streamlit runner
    with open(STREAMLIT_APP_FILE, "r", encoding="utf-8") as f:
        code = compile(f.read(), str(STREAMLIT_APP_FILE), "exec")
        exec(code, globals())
