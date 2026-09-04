# Developed by Fernando Casaloti
"""
MCP Server — Sales Assistant Tools
------------------------------------
Exposes two tools to any MCP client:
  read_document(filename)       — reads a file from the docs/ folder
  send_email(to, subject, body) — simulates sending an email (prints, no SMTP)

Transport: stdio (launched as a subprocess by the lab client)
"""

import asyncio
from pathlib import Path
from mcp.server.mcpserver import MCPServer

DOCS_DIR = Path(__file__).parent / "docs"

mcp = MCPServer("sales-assistant")


@mcp.tool()
def read_document(filename: str) -> str:
    """Read a document from the sales documents folder and return its contents."""
    path = DOCS_DIR / filename
    if not path.exists():
        return f"ERROR: file '{filename}' not found in docs folder."
    return path.read_text(encoding="utf-8")


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email to the specified recipient. Returns a delivery confirmation."""
    return f"EMAIL SENT\n  To:      {to}\n  Subject: {subject}\n  Body:\n{body}"


if __name__ == "__main__":
    asyncio.run(mcp.run_stdio_async())
