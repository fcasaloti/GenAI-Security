# Developed by Fernando Casaloti
"""
GenAI App Security Lab — Web Server
-------------------------------------
Serves interactive module pages and streams live Python script output
to the browser via Server-Sent Events (SSE).

Usage:
    cd /path/to/ai-lab
    .venv/bin/python 00_setup/server.py
    Open: http://localhost:8082
"""

import asyncio
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="GenAI App Security Lab")

LAB_DIR  = Path(__file__).parent.parent          # ai-lab/
BASE_DIR = LAB_DIR / "lab_server"                # ai-lab/lab_server/

# ── Module pages ──────────────────────────────────────────────────────────────
PAGES = {
    "01": BASE_DIR / "pages" / "module01_tokenization.html",
    "02": BASE_DIR / "pages" / "module02_embeddings.html",
    "03": BASE_DIR / "pages" / "module03_vectordb.html",
    "04": BASE_DIR / "pages" / "module04_rag.html",
    "05": BASE_DIR / "pages" / "module05_agents.html",
    "06": BASE_DIR / "pages" / "module06_jailbreaks.html",
    "07": BASE_DIR / "pages" / "module07_guardrails.html",
    "08": BASE_DIR / "pages" / "module08_finetune.html",
    "09": BASE_DIR / "pages" / "module09_mcp.html",
    "10": BASE_DIR / "pages" / "module10_gateway.html",
    "11": BASE_DIR / "pages" / "module11_model_supply_chain.html",
    "rw": BASE_DIR / "pages" / "module_realworld.html",
}

# ── Script registry — maps script ID → file path ─────────────────────────────
SCRIPTS = {
    "01":  LAB_DIR / "01_llm_basics"  / "01_tokenization.py",
    "02":  LAB_DIR / "02_embeddings"  / "01_similarity.py",
    "03":  LAB_DIR / "03_vector_db"   / "01_chromadb_basics.py",
    "04":  LAB_DIR / "04_rag_basic"   / "01_rag_basic.py",
    "05a": LAB_DIR / "05_agents"      / "01_agent_basics.py",
    "05b": LAB_DIR / "05_agents"      / "02_agent_defended.py",
    "06":  LAB_DIR / "06_jailbreaks"  / "01_jailbreak_lab.py",
    "07":  LAB_DIR / "07_guardrails"  / "01_guardrails.py",
    "08":  LAB_DIR / "08_fine-tuning" / "01_finetune_demo.py",
    "09":  LAB_DIR / "09_mcp_security"/ "01_mcp_demo.py",
    "10":  LAB_DIR / "10_ai_gateway"  / "01_gateway_demo.py",
}

# ── Static files (shared CSS) ─────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    index = BASE_DIR / "pages" / "index.html"
    if index.exists():
        return HTMLResponse(index.read_text(encoding="utf-8"))
    return RedirectResponse("/module/01")


@app.get("/module/{module_id}", response_class=HTMLResponse)
async def serve_module(module_id: str):
    page = PAGES.get(module_id)
    if not page or not page.exists():
        return HTMLResponse(f"<h1>Module {module_id} not found</h1>", status_code=404)
    return HTMLResponse(page.read_text(encoding="utf-8"))


# ── Interactive tokenization API ──────────────────────────────────────────────
@app.get("/api/tokenize")
async def api_tokenize(text: str = ""):
    if not text.strip():
        return JSONResponse({"tokens": [], "ids": [], "count": 0})
    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    ids = enc.encode(text)
    tokens = [enc.decode([t]) for t in ids]
    return JSONResponse({"tokens": tokens, "ids": ids, "count": len(ids)})


# ── SSE: run a script and stream stdout to browser ────────────────────────────
@app.get("/run/{script_id}")
async def run_script(script_id: str):
    script = SCRIPTS.get(script_id)
    if not script:
        return JSONResponse({"error": f"script '{script_id}' not found"}, status_code=404)
    if not script.exists():
        return JSONResponse({"error": f"file not found: {script}"}, status_code=404)

    async def event_stream():
        import os as _os
        env = {**_os.environ, "LAB_NONINTERACTIVE": "1"}
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-u", str(script),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(LAB_DIR),
            env=env,
        )
        async for line in process.stdout:
            text = line.decode("utf-8", errors="replace").rstrip("\n")
            escaped = text.replace("\n", "\\n")
            yield f"data: {escaped}\n\n"
        await process.wait()
        yield "data: __DONE__\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("GenAI App Security Lab")
    print("Open: http://localhost:8082")
    uvicorn.run(app, host="0.0.0.0", port=8082, log_level="warning")
