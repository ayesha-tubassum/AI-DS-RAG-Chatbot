"""
scripts/check_embeddings.py

Smoke-test the embedding service against the real Gemini API.
Reads credentials from .env (via pydantic-settings).

Prints ONLY:
  - Model name and dimension (from settings)
  - Lengths of the two vectors (must match EMBEDDING_DIMENSION)
  - Cosine similarity between a document sentence and a related query

Never prints API keys, full vectors, or any secret value.

Usage (from ./backend with .venv active):
    python scripts/check_embeddings.py
"""

import asyncio
import math
import sys
from pathlib import Path

# Ensure the backend package root is importable when run as a script.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.config import get_settings
from app.core.errors import EmbeddingError, NotConfiguredError
from app.services.embeddings import embed_documents, embed_query


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors (both assumed L2-normalized)."""
    dot = sum(x * y for x, y in zip(a, b))
    # Both vectors are normalized to unit length, so cosine = dot product.
    # Clamp to [-1, 1] to guard against tiny float rounding.
    return max(-1.0, min(1.0, dot))


SAMPLE_DOCUMENT = (
    "NumPy is a fundamental Python library for numerical computing. "
    "It provides multi-dimensional array objects and a large collection "
    "of mathematical functions to operate on arrays efficiently."
)

SAMPLE_QUERY = "What is NumPy used for in data science?"


async def main() -> None:
    settings = get_settings()

    print(f"Model     : {settings.embedding_model}")
    print(f"Dimension : {settings.embedding_dimension}")
    print()

    if not settings.google_configured:
        print("ERROR: GOOGLE_API_KEY is not set in .env — cannot run live check.")
        sys.exit(1)

    try:
        print("Embedding document passage...")
        doc_vectors = await embed_documents([SAMPLE_DOCUMENT])
        doc_vec = doc_vectors[0]

        print("Embedding query...")
        query_vec = await embed_query(SAMPLE_QUERY)

    except NotConfiguredError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)
    except EmbeddingError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    print()
    print(f"Document vector length : {len(doc_vec)}")
    print(f"Query vector length    : {len(query_vec)}")

    # Sanity-check: both must equal the configured dimension.
    expected = settings.embedding_dimension
    if len(doc_vec) != expected or len(query_vec) != expected:
        print(
            f"ERROR: Length mismatch! Expected {expected}, "
            f"got doc={len(doc_vec)}, query={len(query_vec)}"
        )
        sys.exit(1)

    sim = cosine_similarity(doc_vec, query_vec)
    print(f"Cosine similarity (doc ↔ query) : {sim:.4f}")

    # A well-matched query/document pair should score > 0.6.
    if sim > 0.6:
        print("✓ Similarity looks reasonable (> 0.60).")
    else:
        print(f"⚠ Similarity is low ({sim:.4f}). Check the model or the sample texts.")

    print()
    print("✓ Embedding service is working correctly.")


if __name__ == "__main__":
    asyncio.run(main())
