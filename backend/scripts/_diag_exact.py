"""
Replicate the EXACT rag_service call (including Pydantic response_schema)
and print the raw response text plus .parsed value.
"""
import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings
from app.prompts.rag_prompt import GENERATION_PROMPT
from app.services.retrieval import retrieve
from app.services.rag_service import _GenerationResponse
from google import genai
from google.genai import types
from pydantic import ValidationError

QUESTION = "What is a transformer model in deep learning?"

async def main():
    settings = get_settings()
    retrieval_result = await retrieve(QUESTION)
    print(f"Kept chunks: {retrieval_result.kept_count}")

    numbered_chunks_parts = []
    for i, (src, passage) in enumerate(
        zip(retrieval_result.sources, retrieval_result.passages)
    ):
        header = f"[{i}] {src.title}"
        if src.section:
            header += f" -- {src.section}"
        numbered_chunks_parts.append(f"{header}\n{passage}")

    numbered_chunks = "\n\n".join(numbered_chunks_parts)
    prompt = GENERATION_PROMPT.format(numbered_chunks=numbered_chunks, question=QUESTION)

    print("\n--- PROMPT SENT TO MODEL (first 800 chars) ---")
    print(prompt[:800])
    print("...\n")

    client = genai.Client(api_key=settings.google_api_key)

    # Exact same config as rag_service (temperature=0.0 + Pydantic schema)
    response = await client.aio.models.generate_content(
        model=settings.generation_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=_GenerationResponse,
            temperature=0.0,
            max_output_tokens=1024,
        ),
    )

    print(f"response.text  : {response.text!r}")
    print(f"response.parsed: {response.parsed!r}")

    # Manual parse fallback
    raw = response.text or ""
    try:
        data = json.loads(raw)
        validated = _GenerationResponse.model_validate(data)
        print(f"\nManual parse  : supported={validated.supported}  used_chunks={validated.used_chunks}")
        print(f"Answer preview: {validated.answer[:200]}")
    except (json.JSONDecodeError, ValidationError) as e:
        print(f"Parse error: {e}")

asyncio.run(main())
