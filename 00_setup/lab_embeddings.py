# Developed by Fernando Casaloti
"""
Shared embedding utility — calls LM Studio's local embedding model.
Uses nomic-embed-text-v1.5 (768 dims) via the OpenAI-compatible API.
No model files to download, no ML libraries to load — just HTTP.
"""

import urllib.request
import json
from typing import List

EMBED_URL   = "http://localhost:1234/v1/embeddings"
EMBED_MODEL = "text-embedding-nomic-embed-text-v1.5"


class LocalEmbedder:
    """
    Calls LM Studio's embedding endpoint.
    Compatible with ChromaDB's embedding_function protocol.
    """

    def encode(self, texts: List[str]) -> List[List[float]]:
        payload = json.dumps({"model": EMBED_MODEL, "input": texts}).encode()
        req = urllib.request.Request(
            EMBED_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        # API returns items sorted by index
        items = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in items]

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.encode(input)

    def embed_query(self, input: List[str]) -> List[List[float]]:
        return self.encode(input)


def get_embedder() -> LocalEmbedder:
    return LocalEmbedder()
