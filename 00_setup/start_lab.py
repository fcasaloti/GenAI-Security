# Developed by Fernando Casaloti
"""
00_setup/start_lab.py — One-command lab launcher.
Starts all dependencies, runs a full connectivity check,
then launches the web server.

Usage:
    cd /path/to/ai-lab
    .venv/bin/python 00_setup/start_lab.py
"""

import sys
import os
import time
import subprocess
import urllib.request
import json as _json
from pathlib import Path

LAB_DIR    = Path(__file__).parent.parent
SETUP_DIR  = LAB_DIR / "00_setup"
sys.path.insert(0, str(SETUP_DIR))
VENV_PY    = LAB_DIR / ".venv" / "bin" / "python"
SERVER_PY  = SETUP_DIR / "server.py"

GREEN  = "\033[32m"
RED    = "\033[31m"
YELLOW = "\033[33m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):   print(f"  {GREEN}✓{RESET} {msg}")
def err(msg):  print(f"  {RED}✗{RESET} {msg}")
def warn(msg): print(f"  {YELLOW}~{RESET} {msg}")
def header(msg): print(f"\n{BOLD}{msg}{RESET}")


print(f"\n{'='*60}")
print(f"{BOLD}  GenAI App Security Lab — Starting Up{RESET}")
print(f"{'='*60}")


# ── 0. Load .env and validate required keys ───────────────────────────────────
header("[0/6] Environment (.env)")
env_file = LAB_DIR / ".env"
LITELLM_MASTER_KEY = ""
PANW_KEY_PRESENT   = False

if not env_file.exists():
    err(".env file not found — create it with LITELLM_MASTER_KEY and PANW_PRISMA_AIRS_API_KEY")
    sys.exit(1)

for line in env_file.read_text().splitlines():
    line = line.strip()
    if line.startswith("#") or "=" not in line:
        continue
    k, _, v = line.partition("=")
    k, v = k.strip(), v.strip().strip('"').strip("'")
    os.environ.setdefault(k, v)
    if k == "LITELLM_MASTER_KEY":
        LITELLM_MASTER_KEY = v
    if k == "PANW_PRISMA_AIRS_API_KEY" and v:
        PANW_KEY_PRESENT = True

if not LITELLM_MASTER_KEY:
    err("LITELLM_MASTER_KEY not set in .env — LiteLLM gateway will reject all requests")
    sys.exit(1)
ok(f"LITELLM_MASTER_KEY loaded")

if PANW_KEY_PRESENT:
    ok("PANW_PRISMA_AIRS_API_KEY loaded — Module 10 secured-llama guardrail ready")
else:
    warn("PANW_PRISMA_AIRS_API_KEY not set — Module 10 secured-llama guardrail will not work")


# ── 1. Python packages ────────────────────────────────────────────────────────
header("[1/6] Python packages")
missing_pkgs = []
for pkg, import_name in [
    ("openai",    "openai"),
    ("chromadb",  "chromadb"),
    ("mcp",       "mcp"),
    ("dotenv",    "dotenv"),
]:
    try:
        __import__(import_name)
        ok(f"{pkg}")
    except ImportError:
        err(f"{pkg} not installed — run: .venv/bin/pip install {pkg}")
        missing_pkgs.append(pkg)

if missing_pkgs:
    print(f"\n  Install missing packages and re-run.")
    sys.exit(1)


# ── 2. Embedding model (nomic-embed-text via LM Studio) ──────────────────────
header("[2/6] Embedding model")
try:
    sys.path.insert(0, str(SETUP_DIR))
    from lab_embeddings import LocalEmbedder
    t = time.time()
    emb = LocalEmbedder()
    vecs = emb.encode(["warmup"])
    ok(f"nomic-embed-text ready in {time.time()-t:.2f}s ({len(vecs[0])} dims)")
except Exception as e:
    err(f"Embedding model failed: {e}")
    print("    → Make sure LM Studio is running with 'text-embedding-nomic-embed-text-v1.5' loaded")
    sys.exit(1)


# ── 3. LM Studio ─────────────────────────────────────────────────────────────
from lab_config import LM_STUDIO
header(f"[3/6] LM Studio ({LM_STUDIO})")
try:
    with urllib.request.urlopen(f"{LM_STUDIO}/v1/models", timeout=4) as r:
        data = _json.loads(r.read())
        models = data.get("data", [])
        if models:
            ok(f"Running — model: {models[0]['id']}")
        else:
            warn("Running but NO model loaded — load a model in LM Studio before running Modules 01-08")
except Exception:
    warn("Not reachable — Modules 04-07 will show a startup error")
    print("    → Open LM Studio, load a model, click 'Start Server'")


# ── 4. Docker / LiteLLM ──────────────────────────────────────────────────────
header("[4/6] LiteLLM AI Gateway (Docker, port 4000)")

def litellm_health() -> bool:
    try:
        req = urllib.request.Request(
            "http://localhost:4000/health",
            headers={"Authorization": f"Bearer {LITELLM_MASTER_KEY}"},
        )
        with urllib.request.urlopen(req, timeout=4) as r:
            data = _json.loads(r.read())
            ok(f"Running — {data.get('healthy_count', 0)} model route(s) healthy")
            return True
    except Exception:
        return False

if not litellm_health():
    print("  Starting LiteLLM via Docker Compose...")
    result = subprocess.run(
        ["docker", "compose", "up", "-d", "litellm"],
        cwd=str(LAB_DIR),
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  Waiting for LiteLLM to be ready...", end="", flush=True)
        for _ in range(15):
            time.sleep(2)
            print(".", end="", flush=True)
            if litellm_health():
                break
        else:
            print()
            warn("LiteLLM started but not yet healthy — Modules 09/10 may not work")
    else:
        err(f"Docker Compose failed: {result.stderr.strip()[:80]}")


# ── 5. Open WebUI ─────────────────────────────────────────────────────────────
header("[5/6] Open WebUI (Docker, port 3000)")
try:
    with urllib.request.urlopen("http://localhost:3000", timeout=4) as r:
        ok(f"Running (HTTP {r.status})")
except Exception:
    print("  Starting Open WebUI via Docker Compose...")
    subprocess.run(
        ["docker", "compose", "up", "-d", "open-webui"],
        cwd=str(LAB_DIR), capture_output=True
    )
    time.sleep(3)
    try:
        with urllib.request.urlopen("http://localhost:3000", timeout=4) as r:
            ok(f"Running (HTTP {r.status})")
    except Exception:
        warn("Open WebUI not reachable — starting anyway")


# ── 6. Launch web server ──────────────────────────────────────────────────────
header("[6/6] Lab Web Server (port 8082)")

# Kill any previous instance
import socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    if s.connect_ex(("localhost", 8082)) == 0:
        print("  Stopping previous server instance...")
        subprocess.run(["pkill", "-f", "00_setup/server.py"], capture_output=True)
        time.sleep(1)

print("  Starting server (loading libraries, may take 30-60s)...")
server_proc = subprocess.Popen(
    [str(VENV_PY), str(SERVER_PY)],
    cwd=str(LAB_DIR),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# Wait up to 90s for server to be ready
for i in range(90):
    time.sleep(1)
    if i % 10 == 9:
        print(f"  Still loading... ({i+1}s)", flush=True)
    else:
        print(".", end="", flush=True)
    try:
        with urllib.request.urlopen("http://localhost:8082", timeout=1) as r:
            print()
            ok(f"Web server ready in {i+1}s — HTTP {r.status}")
            break
    except Exception:
        pass
else:
    print()
    err("Web server did not respond after 90s")
    server_proc.terminate()
    sys.exit(1)


# ── Done ──────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"{BOLD}{GREEN}  ✓ Lab is ready!{RESET}")
print(f"{'='*60}")
print(f"\n  Open in your browser:  {BOLD}http://localhost:8082{RESET}")
print(f"\n  Press Ctrl+C to stop the server.\n")

try:
    server_proc.wait()
except KeyboardInterrupt:
    print("\n  Stopping server...")
    server_proc.terminate()
    print("  Server stopped. Goodbye!\n")
