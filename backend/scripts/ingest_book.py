"""
scripts/ingest_book.py -- ingest book/docs/**/*.md into Qdrant via Gemini embeddings.

Usage (from ./backend with .venv active):

  python scripts/ingest_book.py --dry-run
  python scripts/ingest_book.py --dry-run --only module-01-python-foundations
  python scripts/ingest_book.py
  python scripts/ingest_book.py --recreate
  python scripts/ingest_book.py --only module-01-python-foundations --limit-chunks 20

Flags:
  --dry-run       Parse + chunk only; no API calls, no Qdrant writes.
  --recreate      Delete and recreate the collection (only if this flag is passed).
  --only FOLDER   Ingest only files inside docs/FOLDER.
  --limit-chunks N  Cap total chunks (for test runs).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import textwrap
from collections import defaultdict
from pathlib import Path

# ── Windows console: force UTF-8 output so Unicode chars print correctly ──────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure backend package root is importable when run as a script.
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.config import get_settings
from app.core.logging import configure_logging
from app.ingestion.chunker import Chunk, chunk_document
from app.ingestion.clean import clean_mdx
from app.ingestion.discover import ParsedDoc, discover_docs, validate_paths_against_sitemap
from app.ingestion.embed_cache import EmbedCache
from app.ingestion.mojibake import contains_mojibake, find_mojibake_samples
from app.ingestion.vector_store import (
    delete_points,
    ensure_collection,
    get_all_point_ids_for_source,
    get_collection_count,
    upsert_chunks,
)
from app.services.embeddings import embed_documents

configure_logging()
logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────────

_DOCS_ROOT  = _ROOT.parent / "book" / "docs"
_SITEMAP    = _ROOT.parent / "book" / "build" / "sitemap.xml"

EMBED_BATCH_SIZE  = 20
EMBED_BATCH_DELAY = 1.5


# ── Helpers ────────────────────────────────────────────────────────────────────

def _build_payload(chunk: Chunk) -> dict:
    return {
        "title":        chunk.title,
        "section":      chunk.section,
        "path":         chunk.page_path,
        "source_file":  chunk.source_file,
        "module":       chunk.module,
        "chunk_index":  chunk.chunk_index,
        "text":         chunk.text,
        "content_hash": chunk.content_hash,
    }


def _token_estimate(text: str) -> int:
    from app.ingestion.chunker import CHARS_PER_TOKEN
    return len(text) // CHARS_PER_TOKEN


def _truncate(text: str, max_chars: int = 200) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


# ── Dry-run report ─────────────────────────────────────────────────────────────

def _dry_run_report(
    docs: list[ParsedDoc],
    all_chunks: list[Chunk],
    path_warnings: list[str],
    limit_chunks: int | None,
) -> None:
    # Count mojibake chunks
    mojibake_chunks = [c for c in all_chunks if contains_mojibake(c.text)]

    print()
    print("=" * 70)
    print("DRY-RUN REPORT")
    print("=" * 70)

    print(f"\nFiles found      : {len(docs)}")
    print(f"Chunks created   : {len(all_chunks)}")
    if limit_chunks:
        print(f"(chunk limit     : {limit_chunks} applied)")

    # Mojibake report
    print(f"\nMojibake chunks  : {len(mojibake_chunks)}", end="")
    if len(mojibake_chunks) == 0:
        print("  -- OK: no encoding corruption detected")
    else:
        print(f"  -- WARNING: {len(mojibake_chunks)} chunk(s) contain encoding corruption!")
        for c in mojibake_chunks[:5]:
            samples = find_mojibake_samples(c.text)
            print(f"  ! {c.source_file}  chunk={c.chunk_index}  samples={samples}")

    # Token statistics
    sizes = [_token_estimate(c.text) for c in all_chunks]
    if sizes:
        print(f"\nChunk token sizes:")
        print(f"  min  : {min(sizes)}")
        print(f"  avg  : {sum(sizes) // len(sizes)}")
        print(f"  max  : {max(sizes)}")

    # Chunks per module
    per_module: dict[str, int] = defaultdict(int)
    for c in all_chunks:
        per_module[c.module] += 1
    print("\nChunks per module:")
    for mod, count in sorted(per_module.items()):
        print(f"  {mod:<45} {count:>4}")

    # Path warnings
    if path_warnings:
        print(f"\nPath validation warnings ({len(path_warnings)}):")
        for w in path_warnings:
            print(f"  WARNING: {w}")
    else:
        print("\nOK: All paths validated against sitemap.xml")

    # 3 sample chunks -- always include a module-08 chunk if available
    print()
    print("-" * 70)
    print("3 SAMPLE CHUNKS")
    print("-" * 70)

    m08_chunks = [c for c in all_chunks if "module-08" in c.module]
    samples: list[Chunk] = []
    if m08_chunks:
        samples.append(m08_chunks[0])
    # First and last chunk (skip if already in list)
    for candidate in (all_chunks[0], all_chunks[-1]):
        if not any(id(candidate) == id(s) for s in samples):
            samples.append(candidate)
    # If we don't have 3 yet, add middle
    if len(samples) < 3 and len(all_chunks) > 2:
        mid = all_chunks[len(all_chunks) // 2]
        if not any(id(mid) == id(s) for s in samples):
            samples.append(mid)
    samples = samples[:3]

    for chunk in samples:
        has_moji = contains_mojibake(chunk.text)
        print(f"\n  File    : {chunk.source_file}")
        print(f"  Path    : {chunk.page_path}")
        print(f"  Section : {chunk.section!r}")
        print(f"  Tokens  : ~{_token_estimate(chunk.text)}")
        print(f"  ID      : {chunk.point_id}")
        print(f"  Mojibake: {'YES -- CORRUPTED' if has_moji else 'none'}")
        print(f"  Text    : {_truncate(chunk.text)!r}")

    print()
    print("=" * 70)
    print("Dry run complete. No API calls or Qdrant writes were made.")
    print("=" * 70)
    print()


# ── Core pipeline ──────────────────────────────────────────────────────────────

async def run(args: argparse.Namespace) -> None:
    settings = get_settings()

    # 1. Discover + filter
    logger.info("Discovering docs in %s", _DOCS_ROOT)
    docs = discover_docs(_DOCS_ROOT)

    if args.only:
        docs = [d for d in docs if d.module == args.only]
        if not docs:
            print(f"ERROR: No docs found in folder '{args.only}'.")
            sys.exit(1)
        logger.info("Filtered to %d docs in '%s'", len(docs), args.only)

    # 2. Parse, clean, chunk
    all_chunks: list[Chunk] = []
    for doc in docs:
        cleaned = clean_mdx(doc.raw_content)
        chunks = chunk_document(
            content=cleaned,
            title=doc.title,
            page_path=doc.page_path,
            source_file=doc.relative_path,
            module=doc.module,
        )
        all_chunks.extend(chunks)
        if args.limit_chunks and len(all_chunks) >= args.limit_chunks:
            all_chunks = all_chunks[: args.limit_chunks]
            break

    logger.info("Produced %d chunks from %d files.", len(all_chunks), len(docs))

    # 3. Validate paths
    path_warnings: list[str] = []
    if _SITEMAP.exists():
        path_warnings = validate_paths_against_sitemap(docs, _SITEMAP)
        for w in path_warnings:
            logger.warning("%s", w)
    else:
        logger.info("No sitemap.xml found; skipping path validation.")

    # 4. Dry-run: report and stop
    if args.dry_run:
        _dry_run_report(docs, all_chunks, path_warnings, args.limit_chunks)
        return

    # ── Real ingestion from here ───────────────────────────────────────────────

    # 5. Mojibake guard: refuse to ingest corrupted chunks
    mojibake_chunks = [c for c in all_chunks if contains_mojibake(c.text)]
    if mojibake_chunks:
        print(f"\nERROR: {len(mojibake_chunks)} chunk(s) contain mojibake "
              f"(encoding corruption). Ingestion aborted.")
        print("Run with --dry-run to see which chunks are affected, "
              "then fix the encoding issue and retry.")
        for c in mojibake_chunks[:3]:
            samples = find_mojibake_samples(c.text)
            print(f"  ! {c.source_file}  chunk={c.chunk_index}  {samples}")
        sys.exit(2)

    # 6. Ensure collection
    if args.recreate:
        confirm = input(
            f"\nWARNING: --recreate will DELETE the collection "
            f"'{settings.qdrant_collection}' and all its data.\n"
            f"Type 'yes' to confirm: "
        ).strip()
        if confirm != "yes":
            print("Aborted.")
            sys.exit(0)

    await ensure_collection(recreate=args.recreate)

    # 7. Load embed cache
    cache = EmbedCache()
    logger.info("Embed cache loaded: %d entries.", len(cache))

    # 8. Separate cached from uncached
    to_embed: list[Chunk]         = []
    cached_vectors: dict[str, list[float]] = {}

    for chunk in all_chunks:
        vec = cache.get(chunk.content_hash)
        if vec is not None:
            cached_vectors[chunk.content_hash] = vec
        else:
            to_embed.append(chunk)

    skipped = len(all_chunks) - len(to_embed)
    logger.info("Chunks to embed: %d  |  cached (skip): %d", len(to_embed), skipped)

    # 9. Embed uncached chunks in batches
    new_vectors: dict[str, list[float]] = {}
    failures = 0

    for i in range(0, len(to_embed), EMBED_BATCH_SIZE):
        batch      = to_embed[i : i + EMBED_BATCH_SIZE]
        texts      = [c.text for c in batch]
        batch_num  = i // EMBED_BATCH_SIZE + 1
        total_batches = (len(to_embed) + EMBED_BATCH_SIZE - 1) // EMBED_BATCH_SIZE

        logger.info("Embedding batch %d/%d (%d texts)...", batch_num, total_batches, len(texts))
        try:
            vectors = await embed_documents(texts)
            for chunk, vec in zip(batch, vectors):
                new_vectors[chunk.content_hash] = vec
                cache.set(chunk.content_hash, vec)
        except Exception as exc:
            logger.error("Embedding batch %d failed: %s", batch_num, type(exc).__name__)
            failures += len(batch)
            continue

        cache.save()

        if i + EMBED_BATCH_SIZE < len(to_embed):
            await asyncio.sleep(EMBED_BATCH_DELAY)

    # 10. Merge vectors
    all_vectors = {**cached_vectors, **new_vectors}

    # 11. Stale cleanup
    current_by_source: dict[str, set[str]] = defaultdict(set)
    for chunk in all_chunks:
        current_by_source[chunk.source_file].add(chunk.point_id)

    stale_ids: list[str] = []
    for source_file, current_ids in current_by_source.items():
        stored_ids = await get_all_point_ids_for_source(source_file)
        stale = [sid for sid in stored_ids if sid not in current_ids]
        stale_ids.extend(stale)

    if stale_ids:
        deleted = await delete_points(stale_ids)
        logger.info("Deleted %d stale points.", deleted)

    # 12. Upsert
    upload_ids:      list[str]         = []
    upload_vecs:     list[list[float]] = []
    upload_payloads: list[dict]        = []

    for chunk in all_chunks:
        vec = all_vectors.get(chunk.content_hash)
        if vec is None:
            logger.warning("No vector for chunk %s (skipping).", chunk.point_id)
            failures += 1
            continue
        upload_ids.append(chunk.point_id)
        upload_vecs.append(vec)
        upload_payloads.append(_build_payload(chunk))

    uploaded    = await upsert_chunks(upload_ids, upload_vecs, upload_payloads)
    total_count = await get_collection_count()

    # 13. Final report
    print()
    print("=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)
    print(f"  Files processed      : {len(docs)}")
    print(f"  Chunks created       : {len(all_chunks)}")
    print(f"  Vectors uploaded     : {uploaded}")
    print(f"  Skipped (cached)     : {skipped}")
    print(f"  Stale points deleted : {len(stale_ids)}")
    print(f"  Failures             : {failures}")
    print(f"  Collection size now  : {total_count} points")
    if path_warnings:
        print(f"  Path warnings        : {len(path_warnings)}")
    print("=" * 70)
    print()


# ── Entry point ────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest book/docs into Qdrant via Gemini embeddings.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
          Examples:
            python scripts/ingest_book.py --dry-run
            python scripts/ingest_book.py --dry-run --only module-01-python-foundations
            python scripts/ingest_book.py
            python scripts/ingest_book.py --recreate
            python scripts/ingest_book.py --only module-01-python-foundations --limit-chunks 20
        """),
    )
    parser.add_argument("--dry-run",      action="store_true")
    parser.add_argument("--recreate",     action="store_true")
    parser.add_argument("--only",         metavar="FOLDER")
    parser.add_argument("--limit-chunks", type=int, metavar="N")
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(run(args))
