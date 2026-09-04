"""Import profiler — run this to find what's slow in Module 08."""
import sys, os, time

os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = ""
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

results = []

def timed_import(name, from_module=None, import_names=None):
    t0 = time.perf_counter()
    if from_module:
        mod = __import__(from_module, fromlist=import_names or [])
        if import_names:
            for n in import_names:
                getattr(mod, n)
    else:
        __import__(name)
    elapsed = time.perf_counter() - t0
    results.append((elapsed, name if not from_module else f"from {from_module} import {', '.join(import_names or [])}"))
    print(f"  {elapsed:6.2f}s  {results[-1][1]}", flush=True)

print("=" * 55)
print("IMPORT PROFILER — Module 08")
print("=" * 55)

timed_import("torch")
timed_import("transformers", from_module="transformers",
             import_names=["GPT2LMHeadModel", "GPT2TokenizerFast", "TrainingArguments", "Trainer"])
timed_import("datasets", from_module="datasets", import_names=["Dataset"])
timed_import("peft", from_module="peft",
             import_names=["get_peft_model", "LoraConfig", "TaskType"])

print()
print("=" * 55)
print("SUMMARY (sorted slowest first):")
print("=" * 55)
for elapsed, name in sorted(results, reverse=True):
    bar = "█" * int(elapsed * 5)
    print(f"  {elapsed:6.2f}s  {bar}  {name}")
print()
total = sum(e for e, _ in results)
print(f"  Total import time: {total:.2f}s")
