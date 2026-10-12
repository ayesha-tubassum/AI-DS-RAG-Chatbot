"""
vector_store.py — Qdrant collection management and upsert/delete operations.

Verified API (qdrant-client 1.19.1):
  create_collection(collection_name, vectors_config=VectorParams(size, distance))
  collection_exists(collection_name) → bool
  get_collection(collection_name) → CollectionInfo
  delete_collection(collection_name) → bool
  upsert(collection_name, points=[PointStruct(id, vector, payload)]) → UpdateResult
  scroll(collection_name, scroll_filter, limit, offset, with_payload, with_vectors)
    → (list[Record], next_offset)
  delete(collection_name, points_selector=list[id]) → UpdateResult
  create_payload_index(collection_name, field_name, field_schema) → UpdateResult
"""

from __future__ import annotations

import logging
from typing import Sequence

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
    PointStruct,
    VectorParams,
)

from app.config import get_settings
from app.core.errors import NotConfiguredError, RetrievalError

logger = logging.getLogger(__name__)

# Batch size for Qdrant upsert operations
UPSERT_BATCH_SIZE = 100


def _get_client() -> AsyncQdrantClient:
    settings = get_settings()
    if not settings.qdrant_configured:
        raise NotConfiguredError("Qdrant vector store", ["QDRANT_URL", "QDRANT_API_KEY"])
    return AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)


async def ensure_collection(recreate: bool = False) -> None:
    """
    Create the Qdrant collection if it does not exist.

    If ``recreate`` is True the collection is deleted first (caller must
    already have obtained explicit user confirmation).

    Raises:
        NotConfiguredError: Qdrant is not configured.
        RetrievalError:     Vector size mismatch or API error.
    """
    settings = get_settings()
    client = _get_client()
    collection = settings.qdrant_collection
    dim = settings.embedding_dimension

    try:
        if recreate:
            exists = await client.collection_exists(collection)
            if exists:
                await client.delete_collection(collection)
                logger.info("Deleted collection '%s' for recreation.", collection)

        exists = await client.collection_exists(collection)
        if exists:
            # Verify vector size matches
            info = await client.get_collection(collection)
            stored_dim = info.config.params.vectors.size  # type: ignore[union-attr]
            if stored_dim != dim:
                raise RetrievalError(
                    f"Collection '{collection}' exists with vector size {stored_dim}, "
                    f"but EMBEDDING_DIMENSION={dim}. "
                    "Use --recreate to rebuild, or update EMBEDDING_DIMENSION."
                )
            logger.info(
                "Collection '%s' already exists (size=%d). Reusing.",
                collection, stored_dim,
            )
        else:
            await client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )
            logger.info("Created collection '%s' (size=%d, COSINE).", collection, dim)

            # Create payload indexes for efficient filtering
            await client.create_payload_index(
                collection_name=collection,
                field_name="module",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            await client.create_payload_index(
                collection_name=collection,
                field_name="path",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            logger.info("Created payload indexes for 'module' and 'path'.")

    except (NotConfiguredError, RetrievalError):
        raise
    except Exception as exc:
        raise RetrievalError(f"Collection setup failed: {exc}") from exc
    finally:
        await client.close()


async def upsert_chunks(
    point_ids: list[str],
    vectors: list[list[float]],
    payloads: list[dict],
) -> int:
    """
    Upsert points in batches.

    Args:
        point_ids: UUID strings (one per chunk).
        vectors:   Embedding vectors (same order as point_ids).
        payloads:  Payload dicts (same order).

    Returns:
        Number of points upserted.
    """
    settings = get_settings()
    client = _get_client()
    total = 0

    try:
        for i in range(0, len(point_ids), UPSERT_BATCH_SIZE):
            batch_ids = point_ids[i: i + UPSERT_BATCH_SIZE]
            batch_vecs = vectors[i: i + UPSERT_BATCH_SIZE]
            batch_payloads = payloads[i: i + UPSERT_BATCH_SIZE]

            points = [
                PointStruct(id=pid, vector=vec, payload=payload)
                for pid, vec, payload in zip(batch_ids, batch_vecs, batch_payloads)
            ]
            await client.upsert(collection_name=settings.qdrant_collection, points=points)
            total += len(points)
            logger.debug("Upserted batch of %d points (total so far: %d).", len(points), total)
    except Exception as exc:
        raise RetrievalError(f"Upsert failed: {exc}") from exc
    finally:
        await client.close()

    return total


async def get_all_point_ids_for_source(source_file: str) -> list[str]:
    """
    Scroll through the collection and return all point IDs whose payload
    source_file equals the given value.

    Used for stale-chunk detection: compare stored IDs against current chunks.
    """
    settings = get_settings()
    client = _get_client()
    ids: list[str] = []

    try:
        scroll_filter = Filter(
            must=[
                FieldCondition(key="source_file", match=MatchValue(value=source_file))
            ]
        )
        offset = None
        while True:
            records, next_offset = await client.scroll(
                collection_name=settings.qdrant_collection,
                scroll_filter=scroll_filter,
                limit=250,
                offset=offset,
                with_payload=False,
                with_vectors=False,
            )
            for rec in records:
                ids.append(str(rec.id))
            if next_offset is None:
                break
            offset = next_offset
    except Exception as exc:
        logger.warning("scroll failed for source_file=%s: %s", source_file, exc)
    finally:
        await client.close()

    return ids


async def delete_points(point_ids: Sequence[str]) -> int:
    """Delete points by ID. Returns number deleted."""
    if not point_ids:
        return 0

    settings = get_settings()
    client = _get_client()

    try:
        await client.delete(
            collection_name=settings.qdrant_collection,
            points_selector=list(point_ids),
        )
    except Exception as exc:
        raise RetrievalError(f"Delete failed: {exc}") from exc
    finally:
        await client.close()

    return len(point_ids)


async def get_collection_count() -> int:
    """Return the total number of points in the collection."""
    settings = get_settings()
    client = _get_client()
    try:
        info = await client.get_collection(settings.qdrant_collection)
        return info.points_count or 0
    except Exception:
        return -1
    finally:
        await client.close()
