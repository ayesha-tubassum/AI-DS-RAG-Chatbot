"""Run one question N times and report grounded counts."""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.services.rag_service import answer

QUESTION = "What is a transformer model in deep learning?"
RUNS = 8
DELAY = 2.0

async def main():
    true_count = 0
    false_count = 0
    print(f"Running {RUNS}x: {QUESTION}\n")
    for i in range(1, RUNS + 1):
        result = await answer(QUESTION)
        label = "grounded=True " if result.grounded else "grounded=False"
        print(f"  Run {i}: {label}  srcs={len(result.sources)}")
        if result.grounded:
            true_count += 1
        else:
            false_count += 1
        if i < RUNS:
            await asyncio.sleep(DELAY)
    print(f"\nResult: grounded=True {true_count}/8   grounded=False {false_count}/8")

asyncio.run(main())
