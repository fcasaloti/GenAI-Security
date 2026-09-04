# GenAI Security — Attack & Defense Workshop

A hands-on lab environment for learning and demonstrating GenAI security concepts. Covers 10 modules from LLM basics to AI gateway security, with a live web portal and runnable Python demos.

---

## Modules

| # | Topic | Key concept |
|---|-------|-------------|
| 01 | LLM Basics | Tokenization, first API call, system prompt risks |
| 02 | Embeddings | Semantic similarity, intent clustering |
| 03 | Vector Database | ChromaDB, data poisoning attack |
| 04 | RAG Pipeline | End-to-end RAG + data poisoning |
| 05 | Agents | Tool-use loop, indirect prompt injection |
| 06 | Jailbreaks | 8 bypass techniques against a system prompt |
| 07 | Guardrails | 4-layer input/output guardrail pipeline |
| 08 | Fine-tuning | Training data poisoning demo |
| 09 | MCP Security | Real MCP server, indirect prompt injection via tool output |
| 10 | AI Gateway | LiteLLM routing, runtime security layer |
| RW | Real World | How every attack maps to Microsoft 365 Copilot |

---

## Prerequisites

Before running the lab you need the following installed on your machine:

- **Python 3.11+**
- **Docker Desktop** — [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
- **LM Studio** — [lmstudio.ai](https://lmstudio.ai)
- **Git**

---

## Recovery — Setting Up from Scratch

Use these steps if you are on a new machine or recovering from a lost environment.

### 1. Clone the repository

```bash
git clone https://github.com/fcasaloti/GenAI-Security.git
cd GenAI-Security
```

### 2. Create the Python virtual environment

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

### 3. Recreate the `.env` file

Create a file named `.env` in the root of the project (same folder as `docker-compose.yaml`). This file is **not** in the repository — retrieve your keys from your password manager.

```
LITELLM_MASTER_KEY=your_litellm_master_key_here
PANW_PRISMA_AIRS_API_KEY=your_prisma_airs_api_key_here
```

> **Important:** Never commit this file. It is listed in `.gitignore`.

### 4. Set up LM Studio

1. Open LM Studio and download these two models:
   - **Chat model:** `meta-llama-3.1-8b-instruct` (or equivalent ~8B instruction-tuned model)
   - **Embedding model:** `nomic-embed-text-v1.5`
2. Load the **embedding model** first and start the server on port 1234
3. Then load the **chat model** — both must be active at the same time

### 5. Start Docker Desktop

Make sure Docker Desktop is running before the next step. The lab uses it for LiteLLM (AI gateway) and Open WebUI.

### 6. Start the lab

```bash
.venv/bin/python 00_setup/start_lab.py
```

The start script will:
- Validate your `.env` keys
- Check Python packages
- Warm up the embedding model
- Check LM Studio
- Start LiteLLM and Open WebUI via Docker Compose (auto-starts if not running)
- Launch the lab web server on port 8082

### 7. Open the lab

```
http://localhost:8082
```

---

## Accessing from another computer

The lab server listens on all network interfaces. Students on the same network can open the lab in their browser using your machine's local IP address:

```bash
ipconfig getifaddr en0
```

Then share: `http://<your-ip>:8082`

---

## Project structure

```
ai-lab/
├── 00_setup/          # Start script, embedding helper, web server
├── 01_llm_basics/     # Tokenization, first call, system prompt
├── 02_embeddings/     # Similarity demo
├── 03_vector_db/      # ChromaDB + data poisoning
├── 04_rag_basic/      # Full RAG pipeline
├── 05_agents/         # Agent attack and defense
├── 06_jailbreaks/     # Jailbreak techniques
├── 07_guardrails/     # 4-layer guardrail pipeline
├── 08_fine-tuning/    # Training data poisoning
├── 09_mcp_security/   # MCP server + indirect prompt injection
├── 10_ai_gateway/     # LiteLLM gateway demo
├── lab_server/        # Web portal (HTML pages + static assets)
├── docker-compose.yaml
├── litellm-config.yaml
└── requirements.txt
```

---

## What is NOT in this repository

| Item | Where to get it |
|------|----------------|
| `.env` (API keys) | Your password manager |
| `.venv/` (Python packages) | Recreated via `pip install -r requirements.txt` |
| LM Studio models | Downloaded inside LM Studio |
| Docker images | Pulled automatically by Docker Compose |

---

Developed by Fernando Casaloti
