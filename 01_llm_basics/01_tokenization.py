# Developed by Fernando Casaloti
"""
Module 01a — Tokenization
--------------------------
LLMs don't read words. They read *tokens* — fragments of text produced by
splitting input according to a frequency table built from training data.

Run standalone:  python 01_llm_basics/01_tokenization.py
"""

import tiktoken

print("=" * 60)
print("MODULE 01a — Tokenization")
print("=" * 60)
print("""
  We tokenize sample sentences to show how words split into
  token fragments, then demonstrate how obfuscated inputs like
  "ign0re" produce different token IDs — bypassing string filters.
""")

enc = tiktoken.get_encoding("cl100k_base")
print(f"Tokenizer loaded: cl100k_base  (~100,000 known tokens)\n")

texts = [
    "Hello",
    "Hello world",
    "Felipe is learning AI security",
    "The capital of France is Paris",
    "2 + 2 = 4",
    "SQL injection is dangerous",
]

print("─" * 60)
print("TOKENIZING SAMPLE SENTENCES")
print("─" * 60)
print("Watch how token count rarely matches word count.\n")

for text in texts:
    token_ids = enc.encode(text)
    tokens = [enc.decode([t]) for t in token_ids]

    print(f"  Input:  '{text}'")
    print(f"  Tokens: {tokens}")
    print(f"  IDs:    {token_ids}")
    print(f"  Count:  {len(token_ids)} token(s)  |  {len(text.split())} word(s)")
    print()

# ── Security demo: token smuggling ────────────────────────────────────────────
print("─" * 60)
print("SECURITY DEMO — Token Smuggling")
print("─" * 60)

examples = [
    ("ignore", "normal spelling"),
    ("ign0re", "digit substitution (0 → o)"),
    ("IGNORE", "uppercase variant"),
    ("i g n o r e", "space-separated letters"),
]

for word, note in examples:
    ids = enc.encode(word)
    frags = [enc.decode([t]) for t in ids]
    print(f"  '{word}'  ({note})")
    print(f"    → tokens: {frags}  |  IDs: {ids}")
    print()

print("=" * 60)
print("  Obfuscated variants shift token IDs — the same attack,")
print("  different bytes, invisible to a naive keyword filter.")
print("=" * 60)
