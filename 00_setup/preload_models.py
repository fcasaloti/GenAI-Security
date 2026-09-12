# Developed by Fernando Casaloti
"""
00_setup/preload_models.py — Run once before the labs.
Downloads and caches the embedding model, then verifies all connectivity.
"""

import sys
import os
import time
from pathlib import Path

LAB_DIR = Path(__file__).parent.parent

print("=" * 60)
print("GenAI App Security Lab — Pre-flight Check")
print("=" * 60)

ok = True

# ── 1. Embedding model ────────────────────────────────────────────────────────
print("\n[1/4] Embedding model (all-MiniLM-L6-v2 ONNX)")
ONNX_DIR = Path.home() / ".cache" / "chroma" / "onnx_models" / "all-MiniLM-L6-v2" / "onnx"

if not ONNX_DIR.exists():
    print("  Downloading model (~79 MB, one-time)...")
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    ef = DefaultEmbeddingFunction()
    ef(["warmup"])
    print("  Download complete.")
else:
    print(f"  Model cache found: {ONNX_DIR}")

# Test it with LocalEmbedder (no network calls)
try:
    sys.path.insert(0, str(LAB_DIR / "00_setup"))
    from lab_embeddings import LocalEmbedder
    t = time.time()
    emb = LocalEmbedder()
    result = emb.encode(["security test sentence"])
    elapsed = time.time() - t
    print(f"  ✓ LocalEmbedder OK — {len(result[0])} dims in {elapsed:.2f}s")
except Exception as e:
    print(f"  ✗ LocalEmbedder failed: {e}")
    ok = False

# ── 2. LM Studio ─────────────────────────────────────────────────────────────
import urllib.request, json as _json
from lab_config import LM_STUDIO
print(f"\n[2/4] LM Studio ({LM_STUDIO})")
try:
    with urllib.request.urlopen(f"{LM_STUDIO}/v1/models", timeout=4) as r:
        data = _json.loads(r.read())
        models = data.get("data", [])
        if models:
            print(f"  ✓ Running — model loaded: {models[0]['id']}")
        else:
            print("  ⚠ Running but NO model loaded — load one in LM Studio")
except Exception as e:
    print(f"  ✗ Not reachable: {e}")
    print("  → Open LM Studio, load a model, click 'Start Server'")
    ok = False

# ── 3. LiteLLM gateway ───────────────────────────────────────────────────────
print("\n[3/4] LiteLLM AI Gateway (port 4000)")
try:
    import urllib.request as _req
    req = urllib.request.Request(
        "http://localhost:4000/health",
        headers={"Authorization": "Bearer sk-runtime-secure-2026"},
    )
    with urllib.request.urlopen(req, timeout=4) as r:
        data = _json.loads(r.read())
        healthy = data.get("healthy_count", 0)
        print(f"  ✓ Running — {healthy} model route(s) healthy")
except Exception as e:
    print(f"  ✗ Not reachable: {e}")
    print(f"  → cd {LAB_DIR} && docker compose up -d litellm")

# ── 4. Open WebUI ─────────────────────────────────────────────────────────────
print("\n[4/4] Open WebUI (port 3000)")
try:
    with urllib.request.urlopen("http://localhost:3000", timeout=4) as r:
        print(f"  ✓ Running (HTTP {r.status})")
except Exception as e:
    print(f"  ✗ Not reachable: {e}")
    print(f"  → cd {LAB_DIR} && docker compose up -d open-webui")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
if ok:
    print("✓ All checks passed — labs are ready to run.")
else:
    print("⚠ Some checks failed — fix the items above before running labs.")
print("=" * 60 + "\n")
