"""
clean.py — strip MDX/JSX noise from Markdown content.

Keeps:
  - All prose text
  - Code fences (``` ... ```) — NEVER touched
  - Standard Markdown headings, lists, tables, blockquotes

Removes:
  - import/export statements (MDX)
  - JSX tags that are not standard Markdown (e.g. <MyComponent ... />)
  - Docusaurus admonition wrappers (:::note ... :::) but keeps their inner text

Does NOT use a full MDX parser — regex is sufficient and safer for this corpus.
"""

from __future__ import annotations

import re

# ── Patterns ──────────────────────────────────────────────────────────────────

# MDX import / export lines
_MDX_IMPORT = re.compile(r"^(?:import|export)\s+.*$", re.MULTILINE)

# Docusaurus admonition fence lines: :::note, :::tip, :::caution, :::danger, :::info, :::
_ADMONITION_FENCE = re.compile(r"^:::[\w]*\s*$", re.MULTILINE)

# JSX self-closing or open tags that are NOT standard HTML inline elements
# We target capitalised component names to avoid breaking e.g. <strong>
_JSX_COMPONENT = re.compile(
    r"<[A-Z][A-Za-z0-9]*(?:\s[^>]*)?\s*/?>|</[A-Z][A-Za-z0-9]*>",
    re.MULTILINE,
)

# Trailing whitespace on each line
_TRAILING_WS = re.compile(r"[ \t]+$", re.MULTILINE)

# Multiple blank lines → max two
_MULTI_BLANK = re.compile(r"\n{3,}")


def clean_mdx(content: str) -> str:
    """
    Strip MDX/JSX noise while preserving code fences and prose.

    Code fences are extracted, replaced with placeholders, cleaned around,
    then reinserted — so we never touch content inside fences.
    """
    # Step 1: extract code fences into a side-table
    fences: list[str] = []
    placeholder_base = "\x00CODEFENCE_{}\x00"

    def _stash_fence(m: re.Match) -> str:
        idx = len(fences)
        fences.append(m.group(0))
        return placeholder_base.format(idx)

    # Match fenced code blocks (``` or ~~~, with optional language tag)
    code_fence_re = re.compile(
        r"(?m)^(`{3,}|~{3,})[^\n]*\n.*?\n\1[ \t]*$",
        re.DOTALL,
    )
    protected = code_fence_re.sub(_stash_fence, content)

    # Step 2: apply MDX/JSX stripping
    cleaned = _MDX_IMPORT.sub("", protected)
    cleaned = _ADMONITION_FENCE.sub("", cleaned)
    cleaned = _JSX_COMPONENT.sub("", cleaned)

    # Step 3: tidy whitespace
    cleaned = _TRAILING_WS.sub("", cleaned)
    cleaned = _MULTI_BLANK.sub("\n\n", cleaned)

    # Step 4: restore code fences
    for idx, fence in enumerate(fences):
        cleaned = cleaned.replace(placeholder_base.format(idx), fence)

    return cleaned.strip()
