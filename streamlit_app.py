"""
VoxentraAI Master Root Streamlit Entrypoint for Cloud Deployments (Streamlit Community Cloud / HuggingFace).
"""
import os
import sys
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Execute main Streamlit app in frontend/
STREAMLIT_MAIN = BASE_DIR / "frontend" / "streamlit_app.py"

with open(STREAMLIT_MAIN, "r", encoding="utf-8") as f:
    code = compile(f.read(), str(STREAMLIT_MAIN), "exec")
    exec(code, globals())
