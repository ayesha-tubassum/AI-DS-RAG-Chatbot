"""
discover.py — find and parse all book Markdown/MDX files.

Rules (derived from sitemap.xml validation):
  Folder slug:
    - Strip leading numeric prefix + hyphen: "00-front-matter" → "front-matter"
                                              "module-01-python-foundations" → kept (starts with "module-")
    - "00-front-matter"  → "front-matter"
    - "99-back-matter"   → "back-matter"
    - "module-XX-*"      → unchanged
  File slug:
    - Always use the front matter `id` field (it is the exact Docusaurus URL slug).
    - If `id` is absent, fall back to stripping the numeric prefix from the stem.

  Full path: "/{folder_slug}/{file_id}"

  Skip:
    - _category_.json (not a doc)
    - Files under node_modules/, build/, .docusaurus/
    - Hidden files/dirs (start with .)
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import NamedTuple

import frontmatter  # python-frontmatter

logger = logging.getLogger(__name__)

# Matches "00-", "01-", "99-" etc. at the start of a folder or file stem
_NUMERIC_PREFIX = re.compile(r"^\d{2,3}-")

# Folders whose slug keeps the module- prefix intact
_MODULE_FOLDER = re.compile(r"^module-\d+")

# Skip these folders anywhere in the path
_SKIP_DIRS = {"node_modules", "build", ".docusaurus", "__pycache__"}


class ParsedDoc(NamedTuple):
    """A single parsed Markdown document."""
    source_file: Path       # absolute path
    relative_path: str      # e.g. "module-01-python-foundations/01-variables-data-types.md"
    page_path: str          # Docusaurus URL path, e.g. "/module-01-python-foundations/variables-data-types"
    module: str             # folder name, e.g. "module-01-python-foundations"
    title: str              # from front matter or h1 fallback
    raw_content: str        # full file text (with front matter stripped)


def _folder_slug(folder_name: str) -> str:
    """
    Compute the URL segment for a docs folder.

    "00-front-matter"              → "front-matter"
    "99-back-matter"               → "back-matter"
    "module-01-python-foundations" → "module-01-python-foundations"  (unchanged)
    """
    if _MODULE_FOLDER.match(folder_name):
        return folder_name
    # Strip leading "NN-" numeric prefix
    return _NUMERIC_PREFIX.sub("", folder_name)


def _file_slug(stem: str, fm_id: str | None) -> str:
    """
    Compute the URL slug for a file.

    Prefer the front matter `id`; fall back to stripping the numeric prefix.
    """
    if fm_id:
        return fm_id
    return _NUMERIC_PREFIX.sub("", stem)


def _should_skip(path: Path, docs_root: Path) -> bool:
    """Return True if this path is inside a directory we always skip."""
    try:
        rel = path.relative_to(docs_root)
    except ValueError:
        return False
    for part in rel.parts:
        if part in _SKIP_DIRS or part.startswith("."):
            return True
    return False


def discover_docs(docs_root: Path) -> list[ParsedDoc]:
    """
    Walk *docs_root* and return a ParsedDoc for every .md / .mdx file.

    Args:
        docs_root: Absolute path to book/docs/.

    Returns:
        Sorted list of ParsedDoc (by source_file path for determinism).
    """
    results: list[ParsedDoc] = []

    for md_file in sorted(docs_root.rglob("*.md")) + sorted(docs_root.rglob("*.mdx")):
        if _should_skip(md_file, docs_root):
            continue
        if md_file.name.startswith("_"):
            continue
        # Skip README.md files — they are folder-level descriptions, not content pages
        if md_file.name.upper() == "README.MD":
            logger.debug("Skipping README: %s", md_file)
            continue

        folder = md_file.parent.name
        folder_slug = _folder_slug(folder)

        try:
            post = frontmatter.load(str(md_file))
            fm_id = post.metadata.get("id")
            fm_title = post.metadata.get("title")
            content = post.content
        except Exception as exc:
            # Some files have YAML with unquoted colons in title values (e.g. "title: Cloud: S3 …")
            # Fall back to regex extraction of id and title from the raw front matter block.
            logger.debug("python-frontmatter failed on %s (%s); using regex fallback.", md_file.name, exc)
            raw_text = md_file.read_text(encoding="utf-8", errors="replace")
            fm_id, fm_title, content = _parse_frontmatter_regex(raw_text)
        file_slug = _file_slug(md_file.stem, fm_id)

        # Title fallback: first # heading in content
        title = fm_title or _extract_h1(content) or md_file.stem

        page_path = f"/{folder_slug}/{file_slug}"

        rel = md_file.relative_to(docs_root)

        results.append(
            ParsedDoc(
                source_file=md_file,
                relative_path=str(rel).replace("\\", "/"),
                page_path=page_path,
                module=folder,
                title=title,
                raw_content=content,
            )
        )

    return results


def _extract_h1(content: str) -> str | None:
    """Return the text of the first # heading, or None."""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _parse_frontmatter_regex(raw: str) -> tuple[str | None, str | None, str]:
    """
    Fallback front matter parser using regex for files where PyYAML fails
    (e.g. unquoted colons in title values like "title: Cloud: S3 Basics").

    Returns (id, title, body_content).
    """
    # Match the YAML front matter block
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", raw, re.DOTALL)
    if not fm_match:
        return None, None, raw

    fm_block = fm_match.group(1)
    body = raw[fm_match.end():]

    # Extract id: and title: lines with a simple regex that handles colons in values
    id_match = re.search(r"^id:\s*(.+)$", fm_block, re.MULTILINE)
    title_match = re.search(r"^title:\s*(.+)$", fm_block, re.MULTILINE)

    fm_id = id_match.group(1).strip().strip("\"'") if id_match else None
    fm_title = title_match.group(1).strip().strip("\"'") if title_match else None

    return fm_id, fm_title, body


def validate_paths_against_sitemap(
    docs: list[ParsedDoc],
    sitemap_path: Path,
) -> list[str]:
    """
    Compare computed page_paths against the sitemap.

    Returns a list of warning strings for any path not found in the sitemap.
    Ignores the site base URL (strips https://example.com prefix).
    """
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        # Handle sitemap namespace
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = {
            elem.text.split("example.com", 1)[-1].rstrip("/")
            for elem in root.findall(".//sm:loc", ns)
            if elem.text
        }
        # Also try without namespace
        if not locs:
            locs = {
                elem.text.split("example.com", 1)[-1].rstrip("/")
                for elem in root.iter()
                if elem.tag.endswith("loc") and elem.text
            }
    except Exception as exc:
        logger.warning("Could not parse sitemap: %s", exc)
        return []

    warnings: list[str] = []
    for doc in docs:
        path = doc.page_path.rstrip("/")
        if path not in locs:
            warnings.append(
                f"Path not in sitemap: {path!r}  (source: {doc.relative_path})"
            )
    return warnings
