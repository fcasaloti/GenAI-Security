# Developed by Fernando Casaloti
"""
Module 01b — First LLM Call
----------------------------
Your application never talks to the model directly through a GUI.
It sends a structured HTTP request to an API endpoint and receives
a structured response. This is how every real AI product works —
ChatGPT, Copilot, Claude — just with a remote server instead of
a local one.

Run standalone:  python 01_llm_basics/02_first_call.py
"""

import sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "00_setup"))
from lab_config import LM_STUDIO, LM_STUDIO_AUTH, lm_studio_get
from openai import OpenAI

print("=" * 60)
print("MODULE 01b — First LLM API Call")
print("=" * 60)
print("""
  We send a math question to the model using the OpenAI-compatible
  API and stream the response token by token — the same way every
  real AI product works under the hood.
""")

# ── Check LM Studio ───────────────────────────────────────────────────────────
try:
    lm_studio_get("/v1/models", timeout=3)
    print(f"  ✓ LM Studio is running at {LM_STUDIO}")
except Exception:
    print(f"  ✗ ERROR: LM Studio is not running at {LM_STUDIO}.")
    print("    Please open LM Studio, load a model, and click 'Start Server'.")
    sys.exit(1)

client = OpenAI(base_url=f"{LM_STUDIO}/v1", api_key=LM_STUDIO_AUTH)
MODEL = "meta-llama-3.1-8b-instruct"

QUESTION = (
    "If a train leaves Paris at 9am going 200km/h, and another leaves Lyon "
    "at 10am going 150km/h toward Paris, and they are 400km apart, when do they meet?"
)

print(f"\n  Model:    {MODEL}")
print(f"  Endpoint: {LM_STUDIO}/v1")
print(f"  Mode:     streaming (tokens arrive one at a time)")

print(f"\n─" * 60)
print(f"  USER MESSAGE:")
print(f"  {QUESTION}")
print(f"─" * 60)
print(f"\n  MODEL RESPONSE (streaming token by token):\n")

response = client.chat.completions.create(
    model=MODEL,
    messages=[{"role": "user", "content": QUESTION}],
    temperature=0.7,
    stream=True,
)

for chunk in response:
    token = chunk.choices[0].delta.content
    if token is not None:
        print(token, end="", flush=True)

print(f"\n\n{'=' * 60}")
print("  Done. Every AI product — ChatGPT, Copilot, Claude — is")
print("  the same HTTP call. Guardrails and controls wrap this call.")
print("=" * 60)
