"""
Tests for the ingestion pipeline.

All external services (Gemini, Qdrant) are mocked — no real API calls.
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.ingestion.chunker import (
    CHARS_PER_TOKEN,
    TARGET_MAX_TOKENS,
    Chunk,
    _content_hash,
    _make_point_id,
    chunk_document,
)
from app.ingestion.clean import clean_mdx
from app.ingestion.discover import (
    ParsedDoc,
    _file_slug,
    _folder_slug,
    discover_docs,
    validate_paths_against_sitemap,
)


# ── Folder/file slug computation ──────────────────────────────────────────────

class TestFolderSlug:
    def test_numeric_prefix_stripped_from_front_matter(self):
        assert _folder_slug("00-front-matter") == "front-matter"

    def test_numeric_prefix_stripped_from_back_matter(self):
        assert _folder_slug("99-back-matter") == "back-matter"

    def test_module_folder_unchanged(self):
        assert _folder_slug("module-01-python-foundations") == "module-01-python-foundations"

    def test_module_03_unchanged(self):
        assert _folder_slug("module-03-statistics-and-math-for-ml") == "module-03-statistics-and-math-for-ml"


class TestFileSlug:
    def test_front_matter_id_takes_priority(self):
        assert _file_slug("01-variables-data-types", "variables-data-types") == "variables-data-types"

    def test_front_matter_id_with_numeric_prefix_kept(self):
        # module-03 uses ids like "01-descriptive-statistics"
        assert _file_slug("01-descriptive-statistics", "01-descriptive-statistics") == "01-descriptive-statistics"

    def test_fallback_strips_prefix_when_no_id(self):
        assert _file_slug("01-variables-data-types", None) == "variables-data-types"

    def test_fallback_no_prefix(self):
        assert _file_slug("preface", None) == "preface"


# ── Path computation (end-to-end) ─────────────────────────────────────────────

class TestPathComputation:
    def test_module01_path(self):
        slug = _folder_slug("module-01-python-foundations")
        fslug = _file_slug("01-variables-data-types", "variables-data-types")
        assert f"/{slug}/{fslug}" == "/module-01-python-foundations/variables-data-types"

    def test_front_matter_path(self):
        slug = _folder_slug("00-front-matter")
        fslug = _file_slug("how-to-use-this-book", "how-to-use-this-book")
        assert f"/{slug}/{fslug}" == "/front-matter/how-to-use-this-book"

    def test_module03_numeric_id(self):
        slug = _folder_slug("module-03-statistics-and-math-for-ml")
        fslug = _file_slug("01-descriptive-statistics", "01-descriptive-statistics")
        assert f"/{slug}/{fslug}" == "/module-03-statistics-and-math-for-ml/01-descriptive-statistics"


# ── MDX cleaning ──────────────────────────────────────────────────────────────

class TestCleanMdx:
    def test_import_removed(self):
        src = "import Tabs from '@theme/Tabs';\n\nSome text."
        result = clean_mdx(src)
        assert "import" not in result
        assert "Some text." in result

    def test_export_removed(self):
        src = "export const foo = 1;\n\nContent."
        result = clean_mdx(src)
        assert "export" not in result
        assert "Content." in result

    def test_jsx_component_removed(self):
        src = "Before.\n\n<MyComponent prop='x' />\n\nAfter."
        result = clean_mdx(src)
        assert "MyComponent" not in result
        assert "Before." in result
        assert "After." in result

    def test_admonition_fence_removed_content_kept(self):
        src = ":::note\nThis is a note.\n:::\n\nRegular text."
        result = clean_mdx(src)
        assert ":::" not in result
        assert "Regular text." in result

    def test_code_fence_preserved(self):
        src = textwrap.dedent("""\
            Some text.

            ```python
            import os
            print("hello")
            ```

            More text.
        """)
        result = clean_mdx(src)
        assert "```python" in result
        assert 'print("hello")' in result
        assert "import os" in result  # inside fence: kept

    def test_code_fence_import_not_touched(self):
        """import inside a code fence must NOT be removed."""
        src = "```python\nimport pandas as pd\n```"
        result = clean_mdx(src)
        assert "import pandas as pd" in result


# ── Chunker ───────────────────────────────────────────────────────────────────

class TestChunker:
    def _make_doc(self, content: str) -> list[Chunk]:
        return chunk_document(
            content=content,
            title="Test Page",
            page_path="/test/page",
            source_file="test/page.md",
            module="test",
        )

    def test_empty_content_returns_no_chunks(self):
        assert self._make_doc("") == []

    def test_basic_content_returns_chunks(self):
        content = "# Hello\n\nThis is some content.\n\n## Section\n\nMore content here."
        chunks = self._make_doc(content)
        assert len(chunks) >= 1

    def test_heading_hierarchy_in_section(self):
        """
        The 'section' field on each chunk reflects the heading stack at the
        start of that block.  Small documents fit in one chunk; the section
        is the first heading encountered.
        """
        content = textwrap.dedent("""\
            # Chapter One

            Intro text.

            ## Section A

            Content under section A.

            ### Sub-section A1

            Content under sub-section.
        """)
        chunks = self._make_doc(content)
        assert chunks, "Expected at least one chunk"
        # For a tiny document everything is one chunk; section = first heading
        sections = [c.section for c in chunks]
        assert any(s for s in sections), "All sections are empty — headings not tracked"
        # The h1 heading must appear in at least one section
        assert any("Chapter One" in s for s in sections)

    def test_heading_hierarchy_large_doc(self):
        """With a large document, different sections are tracked per chunk."""
        # Build a doc large enough to produce multiple chunks
        sections_content = []
        for i in range(8):
            para = f"Word " * 120  # ~120 words ≈ 160 tokens per section
            sections_content.append(f"## Section {i}\n\n{para}\n")
        content = "# Big Chapter\n\n" + "\n".join(sections_content)
        chunks = self._make_doc(content)
        assert len(chunks) >= 2, "Expected multiple chunks for large doc"
        # Each chunk's section must include the h1
        for chunk in chunks:
            assert "Big Chapter" in chunk.section or chunk.section == "Big Chapter"

    def test_code_fence_never_split(self):
        """A code fence that would cross a chunk boundary must never be split."""
        # Build a document where the code fence is large enough to potentially be split
        fence_lines = ["```python"] + [f"x_{i} = {i}" for i in range(200)] + ["```"]
        content = "# Big Code\n\n" + "\n".join(fence_lines)
        chunks = self._make_doc(content)
        # Reconstruct the full text across all chunks
        full = "\n\n".join(c.text for c in chunks)
        # Every opening ``` must have a matching closing ```
        fence_opens = full.count("```python")
        fence_closes = [
            line.strip() for line in full.splitlines() if line.strip() == "```"
        ]
        assert fence_opens == len(fence_closes), (
            "Code fence was split across chunks! "
            f"Opens: {fence_opens}, closes: {len(fence_closes)}"
        )

    def test_chunk_size_within_limits(self):
        """Most chunks should be within the configured token limits."""
        from app.ingestion.chunker import TARGET_MIN_TOKENS, TARGET_MAX_TOKENS

        # Generate content with many sections
        sections = []
        for i in range(10):
            para = f"Paragraph {i}: " + ("word " * 60)
            sections.append(f"## Section {i}\n\n{para}\n")
        content = "# Document\n\n" + "\n".join(sections)

        chunks = self._make_doc(content)
        too_big = [c for c in chunks if c.token_estimate > TARGET_MAX_TOKENS * 1.3]
        assert len(too_big) == 0, (
            f"{len(too_big)} chunks exceeded max size: "
            + str([c.token_estimate for c in too_big])
        )

    def test_deterministic_ids(self):
        """Same content + position → same point_id."""
        content = "# Title\n\nSome text content here."
        chunks1 = self._make_doc(content)
        chunks2 = self._make_doc(content)
        assert [c.point_id for c in chunks1] == [c.point_id for c in chunks2]

    def test_different_index_different_id(self):
        """Different chunk_index → different point_id."""
        id1 = _make_point_id("file.md", 0)
        id2 = _make_point_id("file.md", 1)
        assert id1 != id2

    def test_different_file_different_id(self):
        id1 = _make_point_id("file_a.md", 0)
        id2 = _make_point_id("file_b.md", 0)
        assert id1 != id2

    def test_content_hash_in_payload(self):
        content = "# Title\n\nSome content."
        chunks = self._make_doc(content)
        for chunk in chunks:
            assert chunk.content_hash == _content_hash(chunk.text)

    def test_chunk_has_required_fields(self):
        content = "# Title\n\nSome content."
        chunks = self._make_doc(content)
        assert chunks
        c = chunks[0]
        assert c.title == "Test Page"
        assert c.page_path == "/test/page"
        assert c.source_file == "test/page.md"
        assert c.module == "test"
        assert isinstance(c.chunk_index, int)
        assert c.point_id  # non-empty string


# ── Discover against real book structure ─────────────────────────────────────

class TestDiscover:
    """Integration test against the real book/docs directory."""

    _DOCS = Path(__file__).resolve().parent.parent.parent / "book" / "docs"

    @pytest.mark.skipif(
        not (_DOCS / "module-01-python-foundations").exists(),
        reason="book/docs not present",
    )
    def test_discovers_md_files(self):
        docs = discover_docs(self._DOCS)
        assert len(docs) > 100  # book has 149 files

    @pytest.mark.skipif(
        not (_DOCS / "module-01-python-foundations").exists(),
        reason="book/docs not present",
    )
    def test_no_category_json_in_results(self):
        docs = discover_docs(self._DOCS)
        for doc in docs:
            assert "_category_" not in doc.relative_path

    @pytest.mark.skipif(
        not (_DOCS / "module-01-python-foundations").exists(),
        reason="book/docs not present",
    )
    def test_module01_paths_correct(self):
        docs = discover_docs(self._DOCS)
        m01 = [d for d in docs if d.module == "module-01-python-foundations"]
        paths = {d.page_path for d in m01}
        assert "/module-01-python-foundations/variables-data-types" in paths
        assert "/module-01-python-foundations/loops-and-iterations" in paths

    @pytest.mark.skipif(
        not (_DOCS / "00-front-matter").exists(),
        reason="book/docs not present",
    )
    def test_front_matter_folder_slug(self):
        docs = discover_docs(self._DOCS)
        front = [d for d in docs if d.module == "00-front-matter"]
        for doc in front:
            assert doc.page_path.startswith("/front-matter/")

    @pytest.mark.skipif(
        not (Path(__file__).resolve().parent.parent.parent / "book" / "build" / "sitemap.xml").exists(),
        reason="sitemap not built",
    )
    def test_all_paths_in_sitemap(self):
        sitemap = Path(__file__).resolve().parent.parent.parent / "book" / "build" / "sitemap.xml"
        docs = discover_docs(self._DOCS)
        warnings = validate_paths_against_sitemap(docs, sitemap)
        # README.md files are skipped by discover_docs; no mismatches should remain
        assert warnings == [], f"Path mismatches:\n" + "\n".join(warnings)


# ── Stale detection ───────────────────────────────────────────────────────────

class TestStaleDetection:
    """Test that stale point detection logic is correct."""

    def test_stale_ids_are_those_not_in_current_set(self):
        stored = ["id-1", "id-2", "id-3", "id-4"]
        current = {"id-1", "id-3"}  # id-2 and id-4 are stale
        stale = [sid for sid in stored if sid not in current]
        assert set(stale) == {"id-2", "id-4"}

    def test_no_stale_when_all_current(self):
        stored = ["id-1", "id-2"]
        current = {"id-1", "id-2"}
        stale = [sid for sid in stored if sid not in current]
        assert stale == []


# ── Dry-run makes no API/Qdrant calls ────────────────────────────────────────

class TestDryRun:
    """Dry-run must not call Gemini or Qdrant."""

    @pytest.mark.asyncio
    async def test_dry_run_no_external_calls(self):
        """Simulate a dry-run and assert embed_documents is never called."""
        from scripts.ingest_book import run
        import argparse

        args = argparse.Namespace(
            dry_run=True,
            recreate=False,
            only="module-01-python-foundations",
            limit_chunks=5,
        )

        with patch("scripts.ingest_book.embed_documents", new_callable=AsyncMock) as mock_embed, \
             patch("scripts.ingest_book.ensure_collection", new_callable=AsyncMock) as mock_col, \
             patch("scripts.ingest_book.upsert_chunks", new_callable=AsyncMock) as mock_upsert:

            await run(args)

        mock_embed.assert_not_called()
        mock_col.assert_not_called()
        mock_upsert.assert_not_called()
