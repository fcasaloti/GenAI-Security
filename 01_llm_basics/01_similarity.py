# Developed by Fernando Casaloti
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "00_setup"))

print("=" * 60)
print("MODULE 01d — Word Similarity via Embeddings")
print("=" * 60)
print("""
WHAT ARE WE DOING HERE?
  Before we dive into security, we need to understand how
  language models represent meaning mathematically.

  Every piece of text gets converted into a vector — a list of
  numbers (768 of them in our model) that represents WHERE that
  text sits in "meaning space". Texts with similar meanings
  end up at similar coordinates.

  Cosine similarity measures the angle between two vectors:
    1.0  = identical meaning
    0.7+ = closely related
    0.4  = loosely related
    ~0   = completely unrelated

  This lab shows that similarity is about MEANING, not spelling.
  "Transfer money" and "Send funds" are different words — but
  they mean the same thing, so they land close together.
""")

print("Loading embedding model (nomic-embed-text via LM Studio)...", flush=True)
from lab_embeddings import LocalEmbedder
import numpy as np

embedder = LocalEmbedder()
print("Model ready.\n", flush=True)

sentences = [
    "I need to transfer money to my account",   # 0
    "Send funds to my bank",                     # 1
    "The weather is nice today",                 # 2
    "I love pizza",                              # 3
    "king",                                      # 4
    "queen",                                     # 5
    "man",                                       # 6
    "woman",                                     # 7
]

print("Generating embeddings for all sentences...")
print("(Each sentence → 768-dimensional vector via nomic-embed-text)\n")
embeddings = embedder.encode(sentences)
print(f"  ✓ Done. Each embedding: {len(embeddings[0])} numbers\n")


def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


print("─" * 60)
print("SIMILARITY SCORES  (1.0 = identical meaning, 0.0 = unrelated)")
print("─" * 60)

pairs = [
    (0, 1, "Financial synonyms — same intent, different words",
           "Expect HIGH similarity. Both describe moving money."),
    (0, 2, "Finance vs weather — unrelated domains",
           "Expect LOW similarity. Nothing in common semantically."),
    (2, 3, "Weather vs food — both casual, still unrelated",
           "Expect LOW similarity. Different everyday topics."),
    (4, 5, "king vs queen — related by role and royalty",
           "Expect HIGH similarity. Same semantic cluster."),
    (4, 6, "king vs man — gender relationship",
           "Moderate similarity — both masculine, different contexts."),
    (5, 7, "queen vs woman — gender relationship",
           "Moderate similarity — both feminine, different contexts."),
]

for i, j, label, explanation in pairs:
    score = cosine_similarity(embeddings[i], embeddings[j])
    bar = "█" * int(score * 20) if score > 0 else ""
    print(f"\n  {label}")
    print(f"  Why: {explanation}")
    print(f"    A: '{sentences[i]}'")
    print(f"    B: '{sentences[j]}'")
    print(f"    Score: {score:.3f}  |{bar:<20}|")

print(f"\n{'=' * 60}")
print("KEY LESSON:")
print("  Embeddings capture MEANING, not spelling.")
print("  'Transfer money' and 'Send funds' are the same intent")
print("  to the model — even though they share no words.")
print("  This is the foundation of semantic search, RAG, and")
print("  embedding-based security classifiers.")
print("=" * 60)
