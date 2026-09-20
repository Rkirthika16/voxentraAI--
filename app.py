"""
VoxentraAI Master Root Entrypoint (app.py)
Supports:
1. Streamlit CLI runner: `streamlit run app.py`
2. Direct execution: `python app.py`
3. Package namespace extension: `import app`, `from app.config import settings`
"""
import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
__path__ = [str(BASE_DIR / "app")]

# When invoked by Streamlit or executed as a standalone script
if __name__ == "__main__" or "streamlit" in sys.modules:
    STREAMLIT_MAIN = BASE_DIR / "frontend" / "streamlit_app.py"
    if STREAMLIT_MAIN.exists():
        with open(STREAMLIT_MAIN, "r", encoding="utf-8") as f:
            code = compile(f.read(), str(STREAMLIT_MAIN), "exec")
            exec(code, {"__file__": str(STREAMLIT_MAIN), "__name__": "__main__"})
