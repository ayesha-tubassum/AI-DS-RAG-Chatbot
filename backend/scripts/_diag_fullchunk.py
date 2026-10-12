"""Print the FULL chunk text that gets passed to the generation model."""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.services.retrieval import retrieve

QUESTION = "What is a transformer model in deep learning?"

async def main():
    r = await retrieve(QUESTION)
    print(f"Kept: {r.kept_count} chunks\n")
    for i, (src, passage) in enumerate(zip(r.sources, r.passages)):
        print(f"=== Chunk {i}: {src.title} (score={src.score}) ===")
        print(passage)
        print()

asyncio.run(main())
