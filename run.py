import os
import sys
import subprocess
import argparse
import time

def main():
    parser = argparse.ArgumentParser(description="VoxentraAI Master Launcher")
    parser.add_argument(
        "--mode",
        choices=["all", "api", "frontend", "test"],
        default="all",
        help="Execution mode: 'all' (FastAPI + Streamlit), 'api' (FastAPI only), 'frontend' (Streamlit only), 'test' (run test suite)"
    )
    args = parser.parse_args()

    if args.mode == "test":
        print("Running VoxentraAI Test Suite...")
        subprocess.run([sys.executable, "run_tests.py"])
        return

    if args.mode == "api":
        print("Starting FastAPI Backend on http://127.0.0.1:8000 ...")
        subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"])
        return

    if args.mode == "frontend":
        print("Starting Streamlit Portal on http://localhost:8501 ...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"])
        return

    if args.mode == "all":
        print("=" * 70)
        print("[LAUNCH] STARTING VOXENTRA AI (FastAPI Backend + Streamlit Frontend)")
        print("=" * 70)
        print("1. FastAPI Backend:     http://127.0.0.1:8000")
        print("2. Interactive Docs:    http://127.0.0.1:8000/docs")
        print("3. Streamlit Portal:    http://localhost:8501")
        print("=" * 70)

        # Launch API in background subprocess
        api_proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"])
        time.sleep(2)
        try:
            subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py"])
        finally:
            api_proc.terminate()

if __name__ == "__main__":
    main()
