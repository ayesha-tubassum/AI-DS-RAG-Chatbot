"""
Diagnostic script: investigate why "What is a transformer model in deep learning?"
returned supported=false.

Prints:
1. Top-5 retrieved chunks (title, section, path, score, first 300 chars)
2. The raw generation call result (supported, answer, used_chunks)

Run from ./backend:
    python scripts/_diag_transformer.py
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings
from app.prompts.rag_prompt import GENERATION_PROMPT
from app.services.retrieval import retrieve_candidates, retrieve
from google import genai
from google.genai import types

QUESTION = "What is a transformer model in deep learning?"


async def main() -> None:
    settings = get_settings()

    # ── Step 1: retrieve top-5 WITHOUT threshold ─────────────────────────────
    print("=" * 70)
    print(f"QUESTION: {QUESTION}")
    print("=" * 70)
    print()
    print("TOP-5 RETRIEVED CHUNKS (no threshold applied)")
    print("-" * 70)

    candidates = await retrieve_candidates(QUESTION, top_k=5)

    for i, c in enumerate(candidates):
        print(f"Chunk {i}:")
        print(f"  title   : {c['title']}")
        print(f"  section : {c['section']}")
        print(f"  path    : {c['path']}")
        print(f"  score   : {c['score']}")
        snippet = c["text"][:300].replace("\n", " ")
        print(f"  text    : {snippet}")
        print()

    # ── Step 2: run the actual generation call and capture raw JSON ──────────
    print("-" * 70)
    print("GENERATION CALL — RAW OUTPUT")
    print("-" * 70)

    # Re-retrieve with threshold so we get the same kept_hits as rag_service
    retrieval_result = await retrieve(QUESTION)

    print(f"  Chunks passing threshold ({settings.rag_score_threshold}): "
          f"{retrieval_result.kept_count}")
    print()

    if not retrieval_result.has_evidence:
        print("  Gate 1 FAILED — no chunks passed the threshold.")
        print("  Generation was NOT called.")
        return

    # Build the same prompt rag_service would build
    numbered_chunks_parts = []
    for i, (src, passage) in enumerate(
        zip(retrieval_result.sources, retrieval_result.passages)
    ):
        header = f"[{i}] {src.title}"
        if src.section:
            header += f" -- {src.section}"
        numbered_chunks_parts.append(f"{header}\n{passage}")

    numbered_chunks = "\n\n".join(numbered_chunks_parts)
    prompt = GENERATION_PROMPT.format(
        numbered_chunks=numbered_chunks,
        question=QUESTION,
    )

    # Call the generation model directly
    client = genai.Client(api_key=settings.google_api_key)

    # Use raw text output so we can inspect the exact JSON string returned
    response = await client.aio.models.generate_content(
        model=settings.generation_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
            max_output_tokens=1024,
        ),
    )

    raw_text = response.text or ""
    print("Raw JSON from model:")
    print(raw_text)
    print()

    # Parse it
    try:
        parsed = json.loads(raw_text)
        print("Parsed:")
        print(f"  supported   : {parsed.get('supported')}")
        print(f"  used_chunks : {parsed.get('used_chunks')}")
        answer_preview = (parsed.get("answer") or "")[:300]
        print(f"  answer      : {answer_preview}")
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")

    print()
    print("-" * 70)
    print("CHUNKS PASSED TO THE MODEL:")
    print("-" * 70)
    for i, (src, passage) in enumerate(
        zip(retrieval_result.sources, retrieval_result.passages)
    ):
        print(f"  [{i}] score={src.score:.4f}  {src.title} -- {src.section}")
        print(f"       path: {src.path}")
        snippet = passage[:300].replace("\n", " ")
        print(f"       text: {snippet}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
