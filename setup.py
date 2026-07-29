"""
Setup helper - Checks prerequisites and helps configure the project.
Usage: python setup.py
"""

import subprocess, sys, urllib.request, json, os

# Fix Windows console encoding
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def check_python():
    v = sys.version_info
    ok = v >= (3, 9)
    status = "[OK]" if ok else "[FAIL]"
    print(f"  {status} Python {v.major}.{v.minor}.{v.micro}")
    return ok


def check_ollama():
    try:
        r = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=10)
        print(f"  [OK] Ollama CLI: {r.stdout.strip()}")
    except FileNotFoundError:
        print("  [FAIL] Ollama NOT installed -> https://ollama.com/download")
        return False
    try:
        req = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5)
        models = [m["name"] for m in json.loads(req.read().decode()).get("models", [])]
        msg = ", ".join(models) if models else "none (run: ollama pull phi3)"
        print(f"  [OK] Server running - Models: {msg}")
    except Exception:
        print("  [WARN] Server not running -> Run: ollama serve")
    return True


def check_deps():
    pkgs = ["langchain", "langchain_ollama", "langchain_core", "langgraph", "streamlit", "dotenv", "rich"]
    missing = []
    for p in pkgs:
        try:
            __import__(p)
            print(f"  [OK] {p}")
        except ImportError:
            print(f"  [FAIL] {p}")
            missing.append(p)
    return missing


if __name__ == "__main__":
    print("=" * 50)
    print("  Basic Agent - Setup Check")
    print("=" * 50)
    print("\n[Python]"); check_python()
    print("\n[Ollama]"); check_ollama()
    print("\n[Dependencies]")
    m = check_deps()
    print()
    if m:
        print(f"Missing packages! Run: pip install -r requirements.txt")
    else:
        print("All good! Run: python agent.py")
