# AI & Data Science Book — RAG Chat Backend

A FastAPI backend that answers questions about the book using Retrieval-Augmented
Generation (RAG). It embeds questions with Google Gemini, searches a Qdrant vector
database for relevant book passages, and generates grounded answers with Gemini.

## Quick start (Windows PowerShell)

```powershell
# 1. Create and activate virtual environment
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
Copy-Item .env.example .env
# Edit .env and fill in your API keys

# 4. Run the development server
uvicorn app.main:app --reload

# 5. Check health
Invoke-RestMethod http://localhost:8000/health
```

## Running tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest tests/ -v
```

## Architecture

```
POST /api/chat
    │
    ▼
ChatRequest (validated, stripped, 1–1000 chars)
    │
    ▼
rag_service.answer()
    ├─ retrieval.retrieve()
    │   ├─ embeddings.embed_text()   → Gemini embedding model
    │   └─ qdrant_service.search()  → Qdrant Cloud (cosine similarity)
    │
    ├─ score < threshold? → return REFUSAL (no generation call)
    │
    └─ generate with Gemini → ChatResponse(grounded=True)
```

## Configuration reference

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_API_KEY` | — | Google AI Studio API key |
| `EMBEDDING_MODEL` | `gemini-embedding-001` | Gemini embedding model |
| `EMBEDDING_DIMENSION` | `3072` | Vector dimension (768/1536/3072) |
| `GENERATION_MODEL` | `gemini-2.0-flash` | Gemini generation model |
| `QDRANT_URL` | — | Qdrant Cloud cluster URL |
| `QDRANT_API_KEY` | — | Qdrant Cloud API key |
| `QDRANT_COLLECTION` | `ai_ds_book` | Qdrant collection name |
| `RAG_TOP_K` | `5` | Max passages retrieved |
| `RAG_SCORE_THRESHOLD` | `0.5` | Min cosine similarity for evidence |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Comma-separated CORS origins |
| `ENVIRONMENT` | `development` | `development` or `production` |
| `LOG_LEVEL` | `INFO` | Python logging level |

## Model choices

- **`gemini-embedding-001`**: Google's current GA text embedding model (stable, April 2026).
  - Replaces the deprecated `text-embedding-004` (shut down Jan 2026).
  - Text-only input — the right choice for RAG over Markdown book content.
  - Supports `task_type`: `RETRIEVAL_QUERY` for questions, `RETRIEVAL_DOCUMENT` for passages — this asymmetric encoding improves retrieval quality.
  - Supports `output_dimensionality` 128–3072; recommended values: **768, 1536, 3072**.
  - **Normalization**: at 3072 dims the API always returns L2-normalized vectors. At 768 or 1536, `gemini-embedding-001` does NOT auto-normalize (unlike Gemini Embedding 2); the service normalizes manually before storing/comparing. This is required for correct cosine similarity in Qdrant.
  - **Default dimension: 3072** — highest quality per Google's MTEB benchmarks; storage cost is acceptable for a book-sized corpus. Change `EMBEDDING_DIMENSION` to 1536 or 768 to trade quality for storage.

- **`gemini-2.0-flash`**: Current standard fast-generation model. Good balance of speed, cost and quality for a Q&A assistant. Can be changed to `gemini-2.5-pro` for higher quality at higher cost.

## Deployment

### Vercel
The file `api/index.py` re-exports the FastAPI `app` object. Vercel's Python
runtime detects it automatically. Set all environment variables in the Vercel
project dashboard.

### Render / Railway
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
