# Developed by Fernando Casaloti
"""
Module 00 — Setup Verification
Run this to confirm your entire lab stack is working before starting Module 01.
"""

import sys
import os
import subprocess
from rich.console import Console
from rich.panel import Panel

console = Console()

def check(label, fn):
    try:
        result = fn()
        console.print(f"  [green]✓[/green] {label}: {result}")
        return True
    except Exception as e:
        console.print(f"  [red]✗[/red] {label}: {e}")
        return False


console.print(Panel("[bold cyan]GenAI App Security Lab — Setup Verification[/bold cyan]", expand=False))

console.print("\n[bold]1. Python Packages[/bold]")
check("Python version",      lambda: sys.version.split()[0])
check("numpy",               lambda: __import__("numpy").__version__)
check("chromadb",            lambda: __import__("chromadb").__version__)
check("openai",              lambda: __import__("openai").__version__)
check("fastapi",             lambda: __import__("fastapi").__version__)
check("tiktoken",            lambda: __import__("tiktoken").__version__)
check("peft",                lambda: __import__("peft").__version__)
check("transformers",        lambda: __import__("transformers").__version__)
# torch import is skipped — it can hang on some Apple Silicon configurations
console.print("  [yellow]~[/yellow] torch: skipped (can hang on M-series — tested at runtime in Module 08)")

console.print("\n[bold]2. Environment Variables (.env)[/bold]")
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
check("LITELLM_MASTER_KEY",
      lambda: "set ✓" if os.getenv("LITELLM_MASTER_KEY") else (_ for _ in ()).throw(Exception("missing — add to .env")))

console.print("\n[bold]3. Local LLM (LM Studio)[/bold]")
import httpx
from lab_config import LM_STUDIO
def check_lmstudio():
    r = httpx.get(f"{LM_STUDIO}/v1/models", timeout=3)
    models = r.json().get("data", [])
    if not models:
        return "running but no model loaded — load a model in LM Studio"
    return f"running, model: {models[0]['id']}"
check(f"LM Studio API ({LM_STUDIO})", check_lmstudio)

console.print("\n[bold]4. Docker Services[/bold]")
def check_litellm():
    r = httpx.get("http://localhost:4000/health",
                  headers={"Authorization": "Bearer sk-runtime-secure-2026"}, timeout=3)
    data = r.json()
    healthy = data.get("healthy_count", "?")
    return f"running — {healthy} model(s) healthy"
def check_openwebui():
    r = httpx.get("http://localhost:3000", timeout=3)
    return f"running (status {r.status_code})"
check("LiteLLM proxy (port 4000)", check_litellm)
check("Open WebUI (port 3000)", check_openwebui)

console.print("\n[bold]5. Embedding Engine[/bold]")
def check_embeddings():
    from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
    ef = DefaultEmbeddingFunction()
    result = ef(["test"])
    return f"ONNX all-MiniLM-L6-v2 — {len(result[0])} dimensions ✓"
check("ChromaDB ONNX embeddings", check_embeddings)

console.print("\n[dim]To start Docker services: cd ~/Documents/Claude/ai-lab && docker compose up -d[/dim]")
console.print("[dim]LM Studio must be running with a model loaded for Modules 04–07.[/dim]\n")
