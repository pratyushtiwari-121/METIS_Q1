import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

def get_python_exe():
    subpaths = ["Scripts/python.exe", "Scripts/python", "bin/python", "bin/python.exe"]
    candidate_dirs = [
        ROOT_DIR / ".venv",
        ROOT_DIR / "venv",
        BACKEND_DIR / ".venv",
        BACKEND_DIR / "venv",
    ]
    for d in candidate_dirs:
        for sub in subpaths:
            candidate = d / sub
            if candidate.exists():
                return str(candidate)
    return sys.executable

def main():
    print("=" * 65)
    print("   Starting Mentis-Q Quantum Digital Signature Security System")
    print("=" * 65)

    py_exe = get_python_exe()
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"

    print(f"\n[1/3] Launching FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        [py_exe, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(BACKEND_DIR)
    )

    print("[2/3] Waiting for Backend to initialize...")
    time.sleep(3)

    print("\n[3/3] Launching React Frontend (Vite) on http://localhost:5173 ...")
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(FRONTEND_DIR),
        shell=(os.name == "nt")
    )

    time.sleep(2)
    print("\n" + "=" * 65)
    print("   Both Backend and Frontend are running!")
    print("   UI:       http://localhost:5173")
    print("   API Docs: http://127.0.0.1:8000/docs")
    print("   Press CTRL+C anytime to stop both servers.")
    print("=" * 65 + "\n")

    try:
        webbrowser.open("http://localhost:5173")
    except Exception:
        pass

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("\n[!] Backend process exited unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("\n[!] Frontend process exited unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\nStopping Mentis-Q servers...")
    finally:
        if backend_proc.poll() is None:
            backend_proc.terminate()
        if frontend_proc.poll() is None:
            if os.name == "nt":
                subprocess.call(["taskkill", "/F", "/T", "/PID", str(frontend_proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                frontend_proc.terminate()
        print("Servers stopped cleanly.")

if __name__ == "__main__":
    main()
