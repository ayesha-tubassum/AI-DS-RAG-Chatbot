"""
mojibake.py -- detect text that was decoded with the wrong codec.

When UTF-8 bytes are read as cp1252 (Windows default) or cp437, multi-byte
sequences produce characteristic replacement-character clusters.  The patterns
below cover the most common ones seen in the book corpus:

  UTF-8 sequence     cp1252 result    cp437 result
  ----------------   -------------    ------------
  U+2193 (DOWN ARROW ↓)  -> "Γ¥ô"  (seen as "Γåô" in earlier diagnostics)
  U+2192 (RIGHT ARROW →) -> "Γ¢â‚¬â€ "
  U+2014 (EM DASH —)     -> "Γ¢â‚¬â€œ" / "ΓÇö"
  U+221A (SQRT √)        -> "Γê√" / "ΓêÜ"
  U+00E9 (e acute é)     -> "Γ©" / "√©"
  U+2713 (CHECK MARK ✓)  -> "Γ£" patterns
  Replacement char U+FFFD-> "οΏ½"

The detector is conservative: it looks for the Gamma (U+0393 / "Γ") prefix that
appears in Latin-1/cp1252 mangling of 3-byte UTF-8 sequences, plus a few other
known patterns.  False positives on legitimate use of "Γ" (Greek capital Gamma
in math text) are possible but rare in an English book.
"""

from __future__ import annotations

import re

# Patterns that appear in cp1252-misread UTF-8 text
# Each is a compiled regex for speed
_PATTERNS: list[re.Pattern[str]] = [
    # 3-byte UTF-8 sequences misread as cp1252 often start with Γ + misc char
    re.compile(r"Γ[åôÅÖ¢£¤¥¦§¨©ªÇÆ]"),   # arrows, box-drawing, misc
    re.compile(r"â€[œ™""]"),               # em dash, curly quotes, trademark
    re.compile(r"Ã[©àèêë¯]"),             # accented Latin chars
    re.compile(r"ΓÇ[öÿû]"),               # em dash family
    re.compile(r"ΓêÜ"),                    # sqrt sign
    re.compile(r"Γåô"),                    # down-arrow
    re.compile(r"οΏ½"),                    # UTF-8 replacement character U+FFFD
    re.compile(r"â‚¬"),                    # euro sign misread
]

# Minimum hit count to flag a text block (avoids false positives on single chars)
_MIN_HITS = 1


def contains_mojibake(text: str) -> bool:
    """
    Return True if *text* contains at least one mojibake pattern.

    Args:
        text: The string to inspect.

    Returns:
        True when likely encoding corruption is detected.
    """
    for pattern in _PATTERNS:
        if pattern.search(text):
            return True
    return False


def find_mojibake_samples(text: str, max_samples: int = 3) -> list[str]:
    """
    Return up to *max_samples* short excerpts around the first mojibake hits.

    Useful for diagnostics: lets you see exactly what the corruption looks like.
    """
    samples: list[str] = []
    for pattern in _PATTERNS:
        for m in pattern.finditer(text):
            start = max(0, m.start() - 20)
            end   = min(len(text), m.end() + 20)
            samples.append(repr(text[start:end]))
            if len(samples) >= max_samples:
                return samples
    return samples
