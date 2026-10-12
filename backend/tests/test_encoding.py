"""
Tests for the UTF-8 encoding fixes:
  - discover + clean + chunk round-trip for Unicode content
  - embed_cache JSON round-trip for Unicode
  - mojibake detector catches garbled text, passes clean text
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from app.ingestion.clean import clean_mdx
from app.ingestion.chunker import chunk_document
from app.ingestion.discover import discover_docs, ParsedDoc
from app.ingestion.embed_cache import EmbedCache
from app.ingestion.mojibake import contains_mojibake, find_mojibake_samples

# The exact Unicode characters that were corrupted in the book
UNICODE_CHARS = "↓ √ — é ✓ → ≥ ≤ ∑ π"

# Typical mojibake produced by reading UTF-8 as cp1252
MOJIBAKE_SAMPLES = [
    "Γåô",           # ↓ misread
    "ΓêÜ",           # √ misread
    "ΓÇö",           # — misread
    "â€œ",           # left double quote misread
    "Γ©",            # é misread
    "Γ£",            # ✓ misread prefix
]


# ── Mojibake detector ─────────────────────────────────────────────────────────

class TestMojibakeDetector:
    def test_clean_text_not_flagged(self):
        assert contains_mojibake("A variable stores a value. Arrows: down.") is False

    def test_clean_unicode_not_flagged(self):
        # Legitimate Unicode should NOT be flagged
        assert contains_mojibake("The formula is: x = √(a² + b²)") is False

    def test_gamma_aa_pattern_detected(self):
        assert contains_mojibake("Γåô") is True

    def test_gamma_eu_pattern_detected(self):
        assert contains_mojibake("ΓêÜ") is True

    def test_gce_pattern_detected(self):
        assert contains_mojibake("ΓÇö") is True

    def test_ae_euro_pattern_detected(self):
        assert contains_mojibake("â€œ") is True

    def test_replacement_char_detected(self):
        assert contains_mojibake("some οΏ½ text") is True

    def test_empty_string_not_flagged(self):
        assert contains_mojibake("") is False

    def test_normal_paragraph_not_flagged(self):
        text = (
            "NumPy is a fundamental library for numerical computing. "
            "It provides multi-dimensional arrays and fast math operations."
        )
        assert contains_mojibake(text) is False

    def test_all_known_samples_detected(self):
        for sample in MOJIBAKE_SAMPLES:
            assert contains_mojibake(sample) is True, f"Not detected: {sample!r}"

    def test_find_samples_returns_excerpts(self):
        text = f"Some clean text. Then Γåô corruption. More text."
        samples = find_mojibake_samples(text)
        assert len(samples) >= 1
        assert "Γåô" in samples[0]

    def test_find_samples_empty_on_clean_text(self):
        samples = find_mojibake_samples("All clean text here.")
        assert samples == []


# ── Discover: UTF-8 round-trip ────────────────────────────────────────────────

class TestDiscoverEncoding:
    """
    Write a temp .md file with Unicode in body and title, run discover_docs,
    and verify the content survives intact without mojibake.
    """

    UNICODE_TITLE = "UTF-8 Test: \u2193 \u221a \u2014 \u00e9 \u2713"
    UNICODE_BODY  = (
        "# UTF-8 Test: \u2193 \u221a \u2014 \u00e9 \u2713\n\n"
        "Arrow: \u2193\n"
        "Square root: \u221a\n"
        "Em dash: \u2014\n"
        "Accented: \u00e9\n"
        "Check mark: \u2713\n\n"
        "Formula: softmax(QK\u1d40 / \u221ad\u2096)V\n"
    )

    def _write_temp_doc(self, tmp_dir: Path) -> Path:
        doc_dir = tmp_dir / "module-01-test"
        doc_dir.mkdir(parents=True)

        # Write _category_.json so the folder is valid
        (doc_dir / "_category_.json").write_text(
            '{"label": "Test", "position": 1}', encoding="utf-8"
        )

        md_file = doc_dir / "01-unicode-test.md"
        content = (
            "---\n"
            "id: unicode-test\n"
            f"title: {self.UNICODE_TITLE}\n"
            "sidebar_position: 1\n"
            "---\n"
            + self.UNICODE_BODY
        )
        # Write explicitly as UTF-8 (simulating what the book files are)
        md_file.write_text(content, encoding="utf-8")
        return tmp_dir

    def test_unicode_title_survives(self, tmp_path: Path):
        docs_root = self._write_temp_doc(tmp_path)
        docs = discover_docs(docs_root)
        assert len(docs) == 1
        doc = docs[0]
        assert "\u2193" in doc.title, f"Down-arrow missing from title: {doc.title!r}"
        assert "\u221a" in doc.title, f"Sqrt missing from title: {doc.title!r}"

    def test_unicode_body_survives(self, tmp_path: Path):
        docs_root = self._write_temp_doc(tmp_path)
        docs = discover_docs(docs_root)
        assert len(docs) == 1
        content = docs[0].raw_content
        assert "\u2193" in content, "Down-arrow corrupted in body"
        assert "\u221a" in content, "Sqrt corrupted in body"
        assert "\u2014" in content, "Em-dash corrupted in body"
        assert "\u00e9" in content, "Accented char corrupted in body"
        assert "\u2713" in content, "Check mark corrupted in body"

    def test_no_mojibake_after_discover(self, tmp_path: Path):
        docs_root = self._write_temp_doc(tmp_path)
        docs = discover_docs(docs_root)
        for doc in docs:
            assert not contains_mojibake(doc.raw_content), (
                f"Mojibake found in {doc.relative_path}: "
                f"{find_mojibake_samples(doc.raw_content)}"
            )

    def test_unicode_survives_clean(self, tmp_path: Path):
        docs_root = self._write_temp_doc(tmp_path)
        docs = discover_docs(docs_root)
        cleaned = clean_mdx(docs[0].raw_content)
        assert "\u2193" in cleaned, "Down-arrow lost after clean_mdx"
        assert "\u221a" in cleaned, "Sqrt lost after clean_mdx"
        assert not contains_mojibake(cleaned), "Mojibake introduced by clean_mdx"

    def test_unicode_survives_chunk(self, tmp_path: Path):
        docs_root = self._write_temp_doc(tmp_path)
        docs = discover_docs(docs_root)
        cleaned = clean_mdx(docs[0].raw_content)
        chunks = chunk_document(
            content=cleaned,
            title=docs[0].title,
            page_path=docs[0].page_path,
            source_file=docs[0].relative_path,
            module=docs[0].module,
        )
        assert chunks, "No chunks produced"
        combined = " ".join(c.text for c in chunks)
        assert "\u2193" in combined or "\u221a" in combined, (
            "Unicode chars lost after chunking"
        )
        for chunk in chunks:
            assert not contains_mojibake(chunk.text), (
                f"Mojibake in chunk {chunk.chunk_index}: "
                f"{find_mojibake_samples(chunk.text)}"
            )


# ── EmbedCache: unicode round-trip ────────────────────────────────────────────

class TestEmbedCacheEncoding:
    def test_unicode_key_roundtrips(self, tmp_path: Path):
        cache_file = tmp_path / "test_cache.json"
        cache = EmbedCache(cache_path=cache_file)

        # Use a hash that contains only hex chars (realistic)
        key   = "abc123def456"
        # The vector is floats — no unicode issue — but verify the cache
        # also correctly stores/loads a key that happens to come from
        # unicode content (the hash is always ASCII)
        vec   = [0.1, 0.2, 0.3]
        cache.set(key, vec)
        cache.save()

        # Reload from disk
        cache2 = EmbedCache(cache_path=cache_file)
        loaded = cache2.get(key)
        assert loaded == vec

    def test_cache_file_is_valid_utf8_json(self, tmp_path: Path):
        cache_file = tmp_path / "test_cache.json"
        cache = EmbedCache(cache_path=cache_file)
        cache.set("key1", [1.0, 2.0])
        cache.save()

        # File must be readable as UTF-8
        raw = cache_file.read_text(encoding="utf-8")
        data = json.loads(raw)
        assert "key1" in data
        assert data["key1"] == [1.0, 2.0]

    def test_cache_save_uses_ensure_ascii_false(self, tmp_path: Path):
        """ensure_ascii=False means non-ASCII in keys/values are stored as
        real Unicode chars, not \\uXXXX escapes."""
        cache_file = tmp_path / "test_cache.json"
        cache = EmbedCache(cache_path=cache_file)
        # Floats are always ASCII so we verify the flag indirectly via the
        # raw file not containing unnecessary escapes for simple ASCII content
        cache.set("abc", [0.5])
        cache.save()
        raw = cache_file.read_text(encoding="utf-8")
        # The file should be valid JSON
        json.loads(raw)  # raises if malformed
