"""
scripts/eval_chat.py -- end-to-end chat pipeline evaluation.

Runs every question in evaluation/questions.json through the real rag_service
(Gemini generation + Qdrant retrieval) and prints a table plus summary.

Usage (from ./backend with .venv active):
    python scripts/eval_chat.py
    python scripts/eval_chat.py --delay 5

Never prints or logs API keys.  Retries on 429.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from app.core.logging import configure_logging
from app.core.errors import NotConfiguredError, RetrievalError, EmbeddingError, GenerationError
from app.prompts.rag_prompt import REFUSAL_MESSAGE
from app.services.rag_service import answer

configure_logging()

_QUESTIONS_FILE = _ROOT / "evaluation" / "questions.json"
_MAX_RETRIES = 5
_RETRY_BASE = 4.0   # seconds; doubles each attempt


def _trunc(s: str, n: int) -> str:
    """Truncate string to n chars with ASCII ellipsis."""
    return s[:n] + "..." if len(s) > n else s


def _is_rate_limit(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "429" in msg or "quota" in msg or "rate" in msg or "resource_exhausted" in msg


async def _answer_with_retry(question: str, base_delay: float):
    """
    Call rag_service.answer with exponential backoff.
    Retries on both EmbeddingError and GenerationError that look like 429s.
    """
    delay = base_delay
    last_exc: Exception | None = None

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            return await answer(question)
        except (EmbeddingError, GenerationError) as exc:
            if _is_rate_limit(exc) and attempt < _MAX_RETRIES:
                print(f"\n  [rate-limit] {type(exc).__name__} - retrying in {delay:.0f}s "
                      f"(attempt {attempt}/{_MAX_RETRIES})", flush=True)
                await asyncio.sleep(delay)
                delay *= 2
                last_exc = exc
                continue
            raise

    raise last_exc or RuntimeError("All retries exhausted")


async def main(args: argparse.Namespace) -> None:
    questions = json.loads(_QUESTIONS_FILE.read_text(encoding="utf-8"))

    print(f"\nRunning end-to-end eval on {len(questions)} questions")
    print(f"Delay={args.delay}s between questions\n")

    rows = []
    for i, q in enumerate(questions, 1):
        question = q["question"]
        expected = q["expected"]
        topic    = q["topic"]

        print(f"[{i:02d}/{len(questions)}] {_trunc(question, 52)}", end=" ", flush=True)

        try:
            result       = await _answer_with_retry(question, args.delay)
            grounded     = result.grounded
            answer_text  = result.answer
            sources_count = len(result.sources)
            error        = None
        except (NotConfiguredError, RetrievalError, EmbeddingError, GenerationError) as exc:
            grounded      = False
            answer_text   = f"ERROR: {type(exc).__name__}"
            sources_count = 0
            error         = type(exc).__name__
        except Exception as exc:
            grounded      = False
            answer_text   = f"ERROR: {type(exc).__name__}"
            sources_count = 0
            error         = type(exc).__name__

        rows.append({
            "question":      question,
            "expected":      expected,
            "topic":         topic,
            "grounded":      grounded,
            "answer":        answer_text,
            "sources_count": sources_count,
            "error":         error,
        })

        status = "ANSWER" if grounded else "REFUSE"
        print(f"=> {status}  srcs={sources_count}")

        # Delay BEFORE next question (not after last)
        if args.delay > 0 and i < len(questions):
            await asyncio.sleep(args.delay)

    # ---- Table ---------------------------------------------------------------
    print()
    print("=" * 100)
    print("FULL RESULTS TABLE")
    print("=" * 100)

    col_q = 46
    col_e = 7
    col_g = 8
    col_s = 5
    col_a = 28

    header = (
        f"{'Question':<{col_q}}  {'Expect':<{col_e}}  {'Grounded':<{col_g}}"
        f"  {'Srcs':<{col_s}}  {'Answer (shortened)':<{col_a}}"
    )
    sep = "-" * len(header)
    print(sep)
    print(header)
    print(sep)

    for r in rows:
        q_str = _trunc(r["question"], col_q)
        e_str = r["expected"]
        g_str = "true" if r["grounded"] else "false"
        s_str = str(r["sources_count"])
        a_str = _trunc(r["answer"] or "(empty)", col_a)

        correct = (
            (e_str == "answer" and r["grounded"]) or
            (e_str == "refuse" and not r["grounded"])
        )
        flag = "   " if correct else "  X"
        print(
            f"{q_str:<{col_q}}  {e_str:<{col_e}}  {g_str:<{col_g}}"
            f"  {s_str:<{col_s}}  {a_str:<{col_a}}{flag}"
        )

    print(sep)

    # ---- Summary -------------------------------------------------------------
    in_book  = [r for r in rows if r["expected"] == "answer"]
    out_book = [r for r in rows if r["expected"] == "refuse"]

    in_answered  = [r for r in in_book  if r["grounded"] is True]
    in_refused   = [r for r in in_book  if r["grounded"] is False]
    out_refused  = [r for r in out_book if r["grounded"] is False]
    out_answered = [r for r in out_book if r["grounded"] is True]

    answered_no_error = [r for r in in_answered if not r["error"]]
    refused_no_error  = [r for r in out_refused  if not r["error"]]

    print()
    print("=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print(f"  In-book  answer rate  : {len(in_answered)}/{len(in_book)}"
          f"  ({len(in_answered)/max(1,len(in_book)):.0%})")
    print(f"  Out-book refusal rate : {len(out_refused)}/{len(out_book)}"
          f"  ({len(out_refused)/max(1,len(out_book)):.0%})")
    print(f"  Overall accuracy      : "
          f"{(len(in_answered)+len(out_refused))}/{len(rows)}")

    if in_refused:
        print()
        print("  In-book questions REFUSED (false negatives):")
        for r in in_refused:
            mark = " [ERROR]" if r["error"] else ""
            print(f"    X {_trunc(r['question'], 65)}{mark}")
            print(f"      topic: {r['topic']}")

    if out_answered:
        print()
        print("  Out-of-book questions ANSWERED (false positives):")
        for r in out_answered:
            print(f"    X {_trunc(r['question'], 65)}")
            print(f"      answer: {_trunc(r['answer'], 90)}")

    errors = [r for r in rows if r["error"]]
    if errors:
        print()
        print(f"  API errors ({len(errors)} questions hit rate limits or network issues):")
        for r in errors:
            print(f"    ! {r['error']:20s}  {_trunc(r['question'], 55)}")
        print("    (increase --delay or re-run; errors counted as REFUSE for accuracy)")

    print("=" * 100)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="End-to-end chat pipeline evaluation.")
    p.add_argument(
        "--delay", type=float, default=5.0,
        help="Seconds between questions (default 5.0 — respects free-tier limits).",
    )
    return p.parse_args()


if __name__ == "__main__":
    asyncio.run(main(_parse_args()))
