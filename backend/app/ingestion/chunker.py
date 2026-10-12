"""
chunker.py — Markdown-aware chunker with heading-hierarchy tracking.

Design goals (from spec):
  - Target ~400–800 tokens per chunk; overlap 50–100 tokens.
  - Never split inside a code fence.
  - Keep a heading with at least its first paragraph.
  - Merge tiny chunks (< MIN_TOKENS) into the previous chunk.
  - Split oversized sections at paragraph boundaries.
  - Preserve heading hierarchy as "section" string: "h1 > h2 > h3".
  - All size constants configurable.

Token estimate: 1 token ≈ 4 characters (simple, fast, documented).
  4 chars/token is a well-known rule of thumb for English text and code.
  At 400 tokens → 1600 chars; 800 tokens → 3200 chars.
"""

from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

# ── Configurable constants ────────────────────────────────────────────────────

CHARS_PER_TOKEN: int = 4          # 1 token ≈ 4 characters

TARGET_MIN_TOKENS: int = 400      # target minimum chunk size
TARGET_MAX_TOKENS: int = 800      # target maximum chunk size
OVERLAP_TOKENS: int = 75          # overlap between adjacent chunks

MIN_CHUNK_TOKENS: int = 80        # chunks smaller than this are merged into previous

# Derived char limits (used internally)
_MIN_CHARS = TARGET_MIN_TOKENS * CHARS_PER_TOKEN
_MAX_CHARS = TARGET_MAX_TOKENS * CHARS_PER_TOKEN
_OVERLAP_CHARS = OVERLAP_TOKENS * CHARS_PER_TOKEN
_MIN_CHUNK_CHARS = MIN_CHUNK_TOKENS * CHARS_PER_TOKEN


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class Chunk:
    """One text chunk ready for embedding and indexing."""
    text: str
    section: str           # heading breadcrumb e.g. "Variables > Lists"
    chunk_index: int
    title: str             # page title (from front matter)
    page_path: str         # Docusaurus URL path
    source_file: str       # relative path to source .md file
    module: str            # folder name
    content_hash: str      # sha256 of text (for dedup / resume cache)
    point_id: str          # deterministic UUID5

    @property
    def token_estimate(self) -> int:
        return len(self.text) // CHARS_PER_TOKEN


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _make_point_id(source_file: str, chunk_index: int) -> str:
    """
    Deterministic UUID5 from source_file + chunk_index.
    Re-running ingestion on unchanged files produces the same IDs.
    """
    namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # URL namespace
    name = f"{source_file}::{chunk_index}"
    return str(uuid.uuid5(namespace, name))


# ── Heading regex ─────────────────────────────────────────────────────────────

_HEADING = re.compile(r"^(#{1,3})\s+(.+)$")
_CODE_FENCE_START = re.compile(r"^(`{3,}|~{3,})")


# ── Internal: split lines into "blocks" ──────────────────────────────────────

@dataclass
class _Block:
    """A contiguous block of lines with the same heading level context."""
    lines: list[str] = field(default_factory=list)
    heading_stack: tuple[str, ...] = ()   # (h1_text, h2_text?, h3_text?)

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    @property
    def char_count(self) -> int:
        return sum(len(l) for l in self.lines)


def _parse_blocks(content: str) -> list[_Block]:
    """
    Split Markdown content into blocks, one per heading section.
    Code fences are never split.
    """
    blocks: list[_Block] = []
    current_lines: list[str] = []
    heading_stack: list[str] = ["", "", ""]  # indices 0=h1, 1=h2, 2=h3
    in_fence = False
    fence_marker = ""

    def _flush(lines: list[str], stack: list[str]) -> None:
        text = "\n".join(lines).strip()
        if text:
            blocks.append(_Block(
                lines=lines[:],
                heading_stack=tuple(stack),
            ))

    for line in content.splitlines():
        # Track code fences
        if not in_fence:
            m = _CODE_FENCE_START.match(line)
            if m:
                in_fence = True
                fence_marker = m.group(1)[0] * len(m.group(1))
                current_lines.append(line)
                continue
        else:
            current_lines.append(line)
            stripped = line.strip()
            if stripped.startswith(fence_marker) and len(stripped) >= len(fence_marker):
                in_fence = False
            continue

        # Detect headings (only outside fences)
        hm = _HEADING.match(line)
        if hm:
            level = len(hm.group(1))  # 1, 2, or 3
            text = hm.group(2).strip()

            # Flush current accumulator
            _flush(current_lines, heading_stack)
            current_lines = [line]

            # Update stack
            if level == 1:
                heading_stack = [text, "", ""]
            elif level == 2:
                heading_stack = [heading_stack[0], text, ""]
            else:
                heading_stack = [heading_stack[0], heading_stack[1], text]
        else:
            current_lines.append(line)

    _flush(current_lines, heading_stack)
    return blocks


def _section_label(stack: tuple[str, ...]) -> str:
    """Build breadcrumb from heading stack, skipping empty levels."""
    parts = [s for s in stack if s]
    return " > ".join(parts) if parts else ""


def _split_at_paragraphs(text: str, max_chars: int) -> list[str]:
    """
    Split text at blank lines to stay under max_chars.
    Never splits inside a code fence.
    """
    paragraphs: list[str] = []
    current: list[str] = []
    in_fence = False
    fence_marker = ""

    for line in text.splitlines():
        if not in_fence:
            m = _CODE_FENCE_START.match(line)
            if m:
                in_fence = True
                fence_marker = m.group(1)[0] * len(m.group(1))
                current.append(line)
                continue
        else:
            current.append(line)
            stripped = line.strip()
            if stripped.startswith(fence_marker) and len(stripped) >= len(fence_marker):
                in_fence = False
            continue

        if line.strip() == "" and not in_fence:
            if current:
                paragraphs.append("\n".join(current))
                current = []
        else:
            current.append(line)

    if current:
        paragraphs.append("\n".join(current))

    # Combine paragraphs into chunks ≤ max_chars
    result: list[str] = []
    buf: list[str] = []
    buf_len = 0

    for para in paragraphs:
        para_len = len(para)
        if buf_len + para_len > max_chars and buf:
            result.append("\n\n".join(buf))
            buf = []
            buf_len = 0
        buf.append(para)
        buf_len += para_len

    if buf:
        result.append("\n\n".join(buf))

    return result or [text]


# ── Public API ────────────────────────────────────────────────────────────────

def chunk_document(
    content: str,
    title: str,
    page_path: str,
    source_file: str,
    module: str,
) -> list[Chunk]:
    """
    Chunk a cleaned Markdown document into Chunk objects.

    Args:
        content:     Cleaned Markdown text (front matter already stripped).
        title:       Page title from front matter.
        page_path:   Docusaurus URL path.
        source_file: Relative path to source file (for ID and payload).
        module:      Module folder name.

    Returns:
        List of Chunk objects, each with deterministic IDs and content hashes.
    """
    blocks = _parse_blocks(content)
    if not blocks:
        return []

    # Merge or split blocks to hit the target token range
    raw_chunks: list[tuple[str, tuple[str, ...]]] = []  # (text, heading_stack)

    accumulator = ""
    acc_stack: tuple[str, ...] = ()

    for block in blocks:
        block_text = block.text
        block_len = len(block_text)

        # If adding this block stays under max, accumulate
        if len(accumulator) + block_len <= _MAX_CHARS:
            if accumulator:
                accumulator += "\n\n" + block_text
            else:
                accumulator = block_text
                acc_stack = block.heading_stack
        else:
            # Flush accumulator
            if accumulator:
                raw_chunks.append((accumulator, acc_stack))
            # If this block alone is too big, split at paragraphs
            if block_len > _MAX_CHARS:
                for part in _split_at_paragraphs(block_text, _MAX_CHARS):
                    raw_chunks.append((part, block.heading_stack))
                accumulator = ""
                acc_stack = ()
            else:
                accumulator = block_text
                acc_stack = block.heading_stack

    if accumulator:
        raw_chunks.append((accumulator, acc_stack))

    # Add overlap: prepend tail of previous chunk
    overlapped: list[tuple[str, tuple[str, ...]]] = []
    for i, (text, stack) in enumerate(raw_chunks):
        if i > 0 and _OVERLAP_CHARS > 0:
            prev_text = raw_chunks[i - 1][0]
            tail = prev_text[-_OVERLAP_CHARS:]
            # Only add overlap if it doesn't make this chunk too large
            if len(text) + len(tail) <= _MAX_CHARS * 1.2:
                text = tail + "\n\n" + text
        overlapped.append((text, stack))

    # Merge tiny chunks
    merged: list[tuple[str, tuple[str, ...]]] = []
    for text, stack in overlapped:
        if len(text) < _MIN_CHUNK_CHARS and merged:
            prev_text, prev_stack = merged[-1]
            merged[-1] = (prev_text + "\n\n" + text, prev_stack)
        else:
            merged.append((text, stack))

    # Build Chunk objects
    chunks: list[Chunk] = []
    for idx, (text, stack) in enumerate(merged):
        h = _content_hash(text)
        chunks.append(Chunk(
            text=text.strip(),
            section=_section_label(stack),
            chunk_index=idx,
            title=title,
            page_path=page_path,
            source_file=source_file,
            module=module,
            content_hash=h,
            point_id=_make_point_id(source_file, idx),
        ))

    return chunks
