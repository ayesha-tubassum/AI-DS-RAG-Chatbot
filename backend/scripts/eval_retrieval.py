"""
scripts/eval_retrieval.py — threshold evaluation tool.

For every question in evaluation/questions.json, runs retrieval WITHOUT a
threshold (so we see the raw score distribution) and prints a report showing
where in-book vs out-of-book questions separate.

Usage (from ./backend with .venv active):
    python scripts/eval_retrieval.py
    python scripts/eval_retrieval.py --delay 1.5
    python scripts/eval_retrieval.py --top-k 5

Never prints or logs API keys.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import TypedDict

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.config import get_settings
from app.core.logging import configure_logging
from app.core.errors import EmbeddingError, NotConfiguredError, RetrievalError
from app.services.retrieval import retrieve_candidates

configure_logging()

# ── Constants ──────────────────────────────────────────────────────────────────
_QUESTIONS_FILE = _ROOT / "evaluation" / "questions.json"
_MAX_RETRIES = 4
_RETRY_BASE_DELAY = 2.0       # seconds; doubles each retry


# ── Types ──────────────────────────────────────────────────────────────────────
class Question(TypedDict):
    question: str
    expected: str   # "answer" or "refuse"
    topic: str


class Row(TypedDict):
    question: str
    expected: str
    topic: str
    top1_score: float
    top1_title: str
    top1_section: str
    top1_path: str
    at_threshold: str   # "ANSWER" or "REFUSE"
    hit: bool           # top-K contains the expected chapter (in-book only)


# ── Retry wrapper ──────────────────────────────────────────────────────────────

async def _retrieve_with_retry(
    question: str,
    top_k: int,
    base_delay: float,
) -> list[dict]:
    """Call retrieve_candidates with exponential backoff on 429 / transient errors."""
    delay = base_delay
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            return await retrieve_candidates(question, top_k=top_k)
        except EmbeddingError as exc:
            msg = str(exc)
            # Detect rate-limit signal in the error message
            if "429" in msg or "quota" in msg.lower() or "rate" in msg.lower():
                if attempt < _MAX_RETRIES:
                    print(f"  [rate-limit] retrying in {delay:.0f}s (attempt {attempt}/{_MAX_RETRIES})")
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
            raise
        except Exception:
            raise
    # All retries exhausted — re-raise
    raise EmbeddingError(f"All {_MAX_RETRIES} retries exhausted for question.")


# ── Report printing ────────────────────────────────────────────────────────────

def _trunc(s: str, n: int) -> str:
    return s[:n] + "…" if len(s) > n else s


def _print_table(rows: list[Row], threshold: float) -> None:
    col_q  = 42
    col_e  = 7
    col_sc = 7
    col_t  = 30
    col_a  = 7

    header = (
        f"{'Question':<{col_q}}  {'Expect':<{col_e}}  {'Score':<{col_sc}}"
        f"  {'Top-1 Title':<{col_t}}  {'At thr.':<{col_a}}"
    )
    sep = "-" * len(header)
    print(sep)
    print(header)
    print(sep)
    for r in rows:
        q   = _trunc(r["question"], col_q)
        e   = r["expected"]
        sc  = f"{r['top1_score']:.4f}"
        t   = _trunc(r["top1_title"] or "(none)", col_t)
        act = r["at_threshold"]
        # Mark wrong predictions
        correct = (e == "answer" and act == "ANSWER") or (e == "refuse" and act == "REFUSE")
        flag = "  " if correct else " X"
        print(f"{q:<{col_q}}  {e:<{col_e}}  {sc:<{col_sc}}  {t:<{col_t}}  {act:<{col_a}}{flag}")
    print(sep)


def _print_stats(label: str, scores: list[float]) -> None:
    if not scores:
        print(f"  {label}: no data")
        return
    mn  = min(scores)
    mx  = max(scores)
    avg = sum(scores) / len(scores)
    print(f"  {label}: min={mn:.4f}  avg={avg:.4f}  max={mx:.4f}  n={len(scores)}")


def _suggest_threshold(in_book_scores: list[float], out_scores: list[float]) -> None:
    """Analyse score distributions and print a suggested threshold."""
    print()
    print("=" * 70)
    print("THRESHOLD ANALYSIS")
    print("=" * 70)

    if not in_book_scores or not out_scores:
        print("  Insufficient data for analysis.")
        return

    in_min  = min(in_book_scores)
    out_max = max(out_scores)
    in_avg  = sum(in_book_scores) / len(in_book_scores)
    out_avg = sum(out_scores) / len(out_scores)

    print(f"  In-book  top-1 scores: min={in_min:.4f}  avg={in_avg:.4f}  max={max(in_book_scores):.4f}")
    print(f"  Out-book top-1 scores: min={min(out_scores):.4f}  avg={out_avg:.4f}  max={out_max:.4f}")
    print()

    overlap_lo = max(min(in_book_scores), min(out_scores))
    overlap_hi = min(max(in_book_scores), max(out_scores))

    if overlap_lo <= overlap_hi:
        print(f"  Overlap range : [{overlap_lo:.4f}, {overlap_hi:.4f}]")
        print("  The two groups OVERLAP — any threshold in this range will have some")
        print("  false positives or false negatives.")
    else:
        print(f"  No overlap: groups separate cleanly above {out_max:.4f}.")

    # Suggested threshold: midpoint between the max out-of-book score and the
    # min in-book score (clamped to [0, 1]).  If they overlap, take the midpoint
    # of the overlap to minimise total errors.
    if overlap_lo <= overlap_hi:
        mid = (overlap_lo + overlap_hi) / 2
        suggestion = round(mid, 2)
        strategy = "midpoint of overlap (minimises combined errors)"
    else:
        # Clean gap — set threshold just above the max out-of-book score
        suggestion = round(out_max + 0.01, 2)
        suggestion = min(suggestion, in_min - 0.01)
        suggestion = round(max(suggestion, 0.0), 2)
        strategy = f"just above max out-of-book score ({out_max:.4f})"

    # Also compute what fraction of in-book questions pass at this threshold
    pass_rate = sum(1 for s in in_book_scores if s >= suggestion) / len(in_book_scores)
    fp_rate   = sum(1 for s in out_scores if s >= suggestion) / len(out_scores)

    print()
    print(f"  SUGGESTED THRESHOLD : {suggestion}")
    print(f"  Strategy            : {strategy}")
    print(f"  In-book pass rate   : {pass_rate:.0%}  ({sum(1 for s in in_book_scores if s >= suggestion)}/{len(in_book_scores)} would get an answer)")
    print(f"  Out-of-book leak    : {fp_rate:.0%}  ({sum(1 for s in out_scores if s >= suggestion)}/{len(out_scores)} would wrongly get an answer)")
    print()
    print("  NOTE: This is a recommendation only. To apply it, set")
    print(f"        RAG_SCORE_THRESHOLD={suggestion} in your .env file.")
    print("=" * 70)


# ── Main ───────────────────────────────────────────────────────────────────────

async def main(args: argparse.Namespace) -> None:
    settings = get_settings()
    threshold = settings.rag_score_threshold

    questions: list[Question] = json.loads(_QUESTIONS_FILE.read_text(encoding="utf-8"))

    print(f"\nRunning retrieval eval on {len(questions)} questions")
    print(f"Top-K={args.top_k}  Current threshold={threshold}  Delay={args.delay}s\n")

    rows: list[Row] = []
    in_book_scores: list[float]  = []
    out_scores: list[float]      = []
    in_book_hits: list[bool]     = []

    for i, q in enumerate(questions, 1):
        question  = q["question"]
        expected  = q["expected"]
        topic     = q["topic"]

        print(f"[{i:02d}/{len(questions)}] {_trunc(question, 55)}", end=" ", flush=True)

        try:
            candidates = await _retrieve_with_retry(question, top_k=args.top_k, base_delay=_RETRY_BASE_DELAY)
        except (NotConfiguredError, RetrievalError, EmbeddingError) as exc:
            print(f"\n  ERROR: {type(exc).__name__}")
            rows.append(Row(
                question=question, expected=expected, topic=topic,
                top1_score=0.0, top1_title="ERROR", top1_section="",
                top1_path="", at_threshold="ERROR", hit=False,
            ))
            continue
        except Exception as exc:
            print(f"\n  UNEXPECTED ERROR: {type(exc).__name__}")
            rows.append(Row(
                question=question, expected=expected, topic=topic,
                top1_score=0.0, top1_title="ERROR", top1_section="",
                top1_path="", at_threshold="ERROR", hit=False,
            ))
            continue

        top1_score   = candidates[0]["score"]   if candidates else 0.0
        top1_title   = candidates[0]["title"]   if candidates else ""
        top1_section = candidates[0]["section"] if candidates else ""
        top1_path    = candidates[0]["path"]    if candidates else ""

        at_threshold = "ANSWER" if top1_score >= threshold else "REFUSE"

        # Hit = does top-K include a chunk from the expected module?
        hit = False
        if expected == "answer":
            # Extract the expected module keyword from the topic string
            # e.g. "module-04" from "ML pipeline — module-04"
            topic_lower = topic.lower()
            expected_module = next(
                (part for part in topic_lower.split() if part.startswith("module-")),
                None,
            )
            if expected_module:
                hit = any(
                    expected_module in (c.get("module", "") or "").lower()
                    for c in candidates
                )
            else:
                # Fallback: any result is a "hit" for in-book questions
                hit = bool(candidates)

        row = Row(
            question=question,
            expected=expected,
            topic=topic,
            top1_score=top1_score,
            top1_title=top1_title,
            top1_section=top1_section,
            top1_path=top1_path,
            at_threshold=at_threshold,
            hit=hit,
        )
        rows.append(row)

        if expected == "answer":
            in_book_scores.append(top1_score)
            in_book_hits.append(hit)
        else:
            out_scores.append(top1_score)

        print(f"score={top1_score:.4f}  {at_threshold}")

        if args.delay > 0 and i < len(questions):
            await asyncio.sleep(args.delay)

    # ── Print table ──────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("FULL RESULTS TABLE")
    print("=" * 70)
    _print_table(rows, threshold)

    # ── Group statistics ─────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("SCORE STATISTICS")
    print("=" * 70)
    _print_stats("In-book  questions (expected=answer)", in_book_scores)
    _print_stats("Out-book questions (expected=refuse)", out_scores)

    # ── Hit rate ─────────────────────────────────────────────────────────────
    if in_book_hits:
        hit_rate = sum(in_book_hits) / len(in_book_hits)
        print()
        print("=" * 70)
        print("RETRIEVAL HIT RATE  (top-K contains the expected module)")
        print("=" * 70)
        print(f"  {sum(in_book_hits)}/{len(in_book_hits)} in-book questions returned a chunk from the expected module")
        print(f"  Hit rate: {hit_rate:.0%}")

    # ── Accuracy at current threshold ────────────────────────────────────────
    valid_rows = [r for r in rows if r["at_threshold"] != "ERROR"]
    if valid_rows:
        correct = sum(
            1 for r in valid_rows
            if (r["expected"] == "answer" and r["at_threshold"] == "ANSWER") or
               (r["expected"] == "refuse"  and r["at_threshold"] == "REFUSE")
        )
        print()
        print("=" * 70)
        print(f"ACCURACY AT CURRENT THRESHOLD ({threshold})")
        print("=" * 70)
        print(f"  {correct}/{len(valid_rows)} correct  ({correct/len(valid_rows):.0%})")
        wrong = [r for r in valid_rows if not (
            (r["expected"] == "answer" and r["at_threshold"] == "ANSWER") or
            (r["expected"] == "refuse"  and r["at_threshold"] == "REFUSE")
        )]
        if wrong:
            print("  Incorrect predictions:")
            for r in wrong:
                print(f"    X [{r['expected']:6}] score={r['top1_score']:.4f}  {_trunc(r['question'], 55)}")

    # ── Threshold suggestion ─────────────────────────────────────────────────
    _suggest_threshold(in_book_scores, out_scores)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate retrieval threshold.")
    parser.add_argument(
        "--delay", type=float, default=1.2,
        help="Seconds to sleep between questions (default 1.2 — respects free-tier rate limits).",
    )
    parser.add_argument(
        "--top-k", type=int, default=None,
        help="Override RAG_TOP_K for this run (default: from settings).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    if args.top_k is None:
        from app.config import get_settings as _gs
        args.top_k = _gs().rag_top_k
    asyncio.run(main(args))
