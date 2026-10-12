"""
Diagnostic: investigate retrieval and Gate 1/Gate 2 behaviour for short queries.
Never prints secrets.
Run from ./backend:  python scripts/_diag_queries.py
"""
import asyncio, json, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings
from app.ingestion.chunker import CHARS_PER_TOKEN
from app.prompts.rag_prompt import GENERATION_PROMPT
from app.services.retrieval import retrieve, retrieve_candidates
from app.services.rag_service import _GenerationResponse
from google import genai
from google.genai import types
from pydantic import ValidationError

QUERIES = [
    "what is float",
    "What are floats in Python?",
    "what is AI",
    "what is a list",
    "what is a loop",
    "what is pandas",
]
THRESHOLD = get_settings().rag_score_threshold


def tok(text: str) -> int:
    return len(text) // CHARS_PER_TOKEN


async def gate2_raw(question: str, retrieval_result) -> dict:
    """Call Gemini exactly as rag_service does and return the raw parsed object."""
    settings = get_settings()
    if not retrieval_result.has_evidence:
        return {"skipped": True}

    parts = []
    for i, (src, passage) in enumerate(
        zip(retrieval_result.sources, retrieval_result.passages)
    ):
        header = f"[{i}] {src.title}" + (f" -- {src.section}" if src.section else "")
        parts.append(f"{header}\n{passage}")

    prompt = GENERATION_PROMPT.format(
        numbered_chunks="\n\n".join(parts),
        question=question,
    )
    client = genai.Client(api_key=settings.google_api_key)
    response = await client.aio.models.generate_content(
        model=settings.generation_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_GenerationResponse,
            temperature=0.0,
            max_output_tokens=512,
        ),
    )
    raw = response.text or ""
    try:
        data = json.loads(raw)
        return {"supported": data.get("supported"), "raw": raw[:200]}
    except Exception as e:
        return {"supported": None, "parse_error": str(e), "raw": raw[:200]}


async def main():
    settings = get_settings()
    print(f"RAG_SCORE_THRESHOLD = {THRESHOLD}\n")
    print("=" * 70)

    for q in QUERIES:
        print(f"\nQUERY: {q!r}")
        print("-" * 60)

        # Top-5 without threshold
        candidates = await retrieve_candidates(q, top_k=5)
        print("  Top-5 chunks (no threshold):")
        for i, c in enumerate(candidates):
            flag = "  PASS" if c["score"] >= THRESHOLD else "  fail"
            print(f"    [{i}] score={c['score']:.4f}{flag}  {c['title']!r}  /  {c['section']!r}")
            print(f"         path={c['path']}")

        if not candidates:
            print("    (no results at all)")
            continue

        top_score = candidates[0]["score"]
        print(f"\n  Top score: {top_score:.4f}  threshold: {THRESHOLD}")

        # Gate 1
        result = await retrieve(q)
        gate1_pass = result.has_evidence
        print(f"  Gate 1: {'PASS' if gate1_pass else 'FAIL'} "
              f"(kept={result.kept_count}/{len(candidates)})")

        if not gate1_pass:
            print(f"  => grounded=False  cause=GATE_1 (score {top_score:.4f} < {THRESHOLD})")
            continue

        # Gate 2
        g2 = await gate2_raw(q, result)
        if g2.get("skipped"):
            print("  Gate 2: skipped (no evidence)")
            continue

        supported = g2.get("supported")
        print(f"  Gate 2: supported={supported}  raw={g2.get('raw', '')!r}")
        if supported:
            print("  => grounded=True")
        else:
            print(f"  => grounded=False  cause=GATE_2 (model said supported=false)")

    # ── Extra: inspect the variables-data-types chunk ─────────────────────────
    print("\n" + "=" * 70)
    print("INSPECTING: variables-data-types chunk")
    print("-" * 60)
    cands = await retrieve_candidates("what is a variable in Python", top_k=5)
    for c in cands:
        if "variables-data-types" in c.get("path", ""):
            tokens = tok(c["text"])
            has_float = "float" in c["text"].lower()
            print(f"  path       : {c['path']}")
            print(f"  title      : {c['title']!r}")
            print(f"  section    : {c['section']!r}")
            print(f"  score      : {c['score']:.4f}")
            print(f"  token size : ~{tokens}")
            print(f"  has 'float': {has_float}")
            if has_float:
                # Show the float context
                idx = c["text"].lower().find("float")
                snippet = c["text"][max(0, idx-80):idx+200].replace("\n", " ")
                print(f"  float ctx  : ...{snippet}...")
            print()
            break
    else:
        print("  variables-data-types chunk not in top-5 for that query")

asyncio.run(main())
