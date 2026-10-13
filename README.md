# AI & Data Science: Interactive Book with a RAG Chatbot

An interactive, beginner-friendly **AI and Data Science learning platform** built with Docusaurus and powered by a Retrieval-Augmented Generation (RAG) chatbot. The platform combines structured educational content with an AI assistant that answers questions using the book's content and provides clickable chapter sources.

**Core principle: If the book does not provide sufficient evidence, the chatbot should not guess.**

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Book Contents](#book-contents)
- [How the RAG Chatbot Works](#how-the-rag-chatbot-works)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Clone the Repository](#1-clone-the-repository)
  - [Set Up the Backend](#2-set-up-the-backend)
  - [Configure Environment Variables](#3-configure-environment-variables)
  - [Ingest the Book into Qdrant](#4-ingest-the-book-into-qdrant)
  - [Run the Backend](#5-run-the-backend)
  - [Run the Frontend](#6-run-the-frontend)
- [API Endpoints](#api-endpoints)
- [Evaluation and Testing](#evaluation-and-testing)
- [Security](#security)
- [Known Limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Author](#author)
- [License](#license)

---

## Overview

This project consists of two integrated components:

**1. Interactive AI & Data Science Book**

A documentation-based learning website built with Docusaurus. It organizes educational material into structured modules, with navigation, a table of contents, a custom homepage, and a responsive reading experience.

**2. RAG-Powered AI Chatbot**

An AI assistant named **Ask AI** that retrieves relevant passages from the book before generating an answer. Responses are grounded in retrieved book content, with clickable sources that help readers explore the relevant chapters.

Unlike a general-purpose chatbot, Ask AI is intentionally designed to answer questions within the scope of the book.

## Key Features

### Interactive Learning Platform

- Structured learning material organized into modules.
- Book-style navigation with a sidebar and previous/next links.
- Table of contents for easier navigation.
- Light and dark reading modes.
- Custom homepage featuring an animated particle-network background and book-cover design.
- Responsive interface designed for a comfortable reading experience.

### Retrieval-Augmented Generation

- **Context-based answers:** retrieves relevant passages before generating a response.
- **Source attribution:** displays clickable chapter references.
- **Scope-aware refusals:** politely declines questions that are unrelated to the book or unsupported by its content.
- **Retrieval safeguards:** uses relevance-based checks and a strict answering prompt to reduce unsupported responses.
- **Markdown ingestion pipeline:** discovers, cleans, chunks, embeds, and indexes book content.
- **Vector search:** stores and retrieves embedded passages using Qdrant.
- **Evaluation support:** includes evaluation questions and automated tests.

### Frontend and Backend Separation

- The Docusaurus frontend communicates with a FastAPI backend.
- API credentials remain on the backend rather than being exposed in browser code.
- Configuration is managed through environment variables.
- Backend logging, validation, and error handling support more maintainable development.

## Book Contents

The book is organized into nine learning modules, supported by introductory and concluding sections.

| Section | Topics |
|---|---|
| Start Here | Preface, how to use the book, intended audience, learning roadmap, environment setup |
| Module 01 | Python Foundations |
| Module 02 | Python for Data Science |
| Module 03 | Statistics and Math for Machine Learning |
| Module 04 | Machine Learning |
| Module 05 | Deep Learning |
| Module 06 | MLOps |
| Module 07 | Big Data and Cloud |
| Module 08 | Generative AI and Large Language Models |
| Module 09 | Agentic AI |
| Wrapping Up | Conclusion, next steps, glossary, further resources, and information about the book |

## How the RAG Chatbot Works

The chatbot uses a retrieval-first workflow to keep answers grounded in the book.

```text
Book Markdown Files
        |
        v
Content Discovery and Cleaning
        |
        v
Text Chunking
        |
        v
Embedding Generation
        |
        v
Qdrant Vector Database
        |
        |  User submits a question
        v
Question Embedding and Retrieval
        |
        v
Relevance / Evidence Check
        |
        +---- Insufficient evidence
        |          |
        |          v
        |     Safe Refusal
        |
        +---- Relevant evidence found
                   |
                   v
          Strict RAG Answer Prompt
                   |
                   v
          Grounded Answer Generation
                   |
                   v
          Answer with Chapter Sources
```

### Retrieval and Answering Process

1. **Content ingestion:** Markdown files are discovered and cleaned, then divided into smaller chunks.
2. **Embedding generation:** Google Gemini embeddings convert text chunks into numerical vectors.
3. **Vector indexing:** embeddings and their associated content are stored in Qdrant.
4. **Question retrieval:** the user's question is embedded and used to retrieve relevant passages.
5. **Evidence validation:** the system checks whether the retrieved information is sufficiently relevant.
6. **Answer generation:** when adequate evidence is available, the generation model answers using the retrieved context and strict instructions.
7. **Source display:** the response includes links to the relevant book chapters.

If the retrieved evidence is insufficient, the chatbot is designed to refuse rather than invent an answer.

## Technology Stack

| Component | Technology |
|---|---|
| Documentation website | Docusaurus |
| Frontend framework | React |
| Frontend language | TypeScript |
| Book content | Markdown |
| Backend API | Python, FastAPI |
| Data validation and configuration | Pydantic |
| Embedding model | Google Gemini `gemini-embedding-001` |
| Embedding dimensions | 3072 |
| Answer generation | Google Gemini, configurable through `GENERATION_MODEL` |
| Vector database | Qdrant Cloud |
| API server | Uvicorn |
| Automated testing | pytest |
| Version control | Git and GitHub |

## Project Structure

The repository is divided into a frontend book website and a backend RAG service.

```text
AI-DS-RAG-Chatbot/
│
├── book/                              # Docusaurus frontend and book
│   ├── docs/                          # Book content and modules
│   ├── src/
│   │   ├── components/                # Chatbot, book cover, animations, UI
│   │   ├── pages/                     # Homepage and custom pages
│   │   └── theme/
│   │       └── Root.tsx               # Mounts chatbot across the site
│   ├── static/                        # Images, icons, and static assets
│   ├── docusaurus.config.ts            # Docusaurus configuration
│   ├── sidebars.ts                     # Book navigation configuration
│   ├── package.json                   # Frontend dependencies and scripts
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── api/                       # Health and chat API routes
│   │   ├── services/                  # Embeddings, Qdrant, retrieval, RAG
│   │   ├── ingestion/                 # Discovery, cleaning, chunking, caching
│   │   ├── prompts/                   # RAG instructions and refusal messages
│   │   ├── core/                      # Configuration, errors, logging
│   │   └── main.py                    # FastAPI application entry point
│   │
│   ├── scripts/
│   │   ├── ingest_book.py             # Book ingestion command
│   │   └── ...                        # Evaluation and utility scripts
│   │
│   ├── evaluation/
│   │   └── questions.json             # Evaluation questions
│   │
│   ├── tests/                         # pytest test suite
│   ├── requirements.txt               # Python dependencies
│   └── .env.example                   # Environment variable template
│
├── .gitignore                         # Excludes secrets and generated files
└── README.md                          # Project documentation
```

*Note: This tree highlights the main project directories. Additional files may exist in the repository.*

## Getting Started

Follow these steps to run the project locally.

### Prerequisites

Install or prepare the following:

- Python 3.12
- Node.js and npm
- Git
- A Google Gemini API key
- A Qdrant Cloud URL and API key
- A code editor such as Visual Studio Code

You will need access to the configured embedding and generation models, plus a Qdrant collection for storing the book's vectors.

### 1. Clone the Repository

```bash
git clone https://github.com/ayesha-tubassum/AI-DS-RAG-Chatbot.git
cd AI-DS-RAG-Chatbot
```

### 2. Set Up the Backend

The following commands use Windows PowerShell.

```powershell
cd backend

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks virtual environment activation, consult the official Python documentation for your system's execution policy. Avoid changing system-wide security settings unnecessarily.

### 3. Configure Environment Variables

Create a local environment file from the provided template:

```powershell
Copy-Item .env.example .env
```

Open `backend/.env` and supply your own credentials and configuration values.

| Variable | Purpose |
|---|---|
| `GOOGLE_API_KEY` | Authenticates requests to Google Gemini |
| `EMBEDDING_MODEL` | Selects the text embedding model |
| `EMBEDDING_DIMENSION` | Configures the embedding vector dimension |
| `GENERATION_MODEL` | Selects the answer-generation model |
| `QDRANT_URL` | Qdrant Cloud endpoint |
| `QDRANT_API_KEY` | Authenticates access to Qdrant |
| `QDRANT_COLLECTION` | Name of the vector collection |
| `RAG_TOP_K` | Maximum number of retrieved passages to consider |
| `RAG_SCORE_THRESHOLD` | Retrieval relevance threshold |
| `ALLOWED_ORIGINS` | Frontend origins permitted by CORS |
| `ENVIRONMENT` | Runtime environment configuration |
| `LOG_LEVEL` | Backend logging verbosity |

Use values appropriate for your own environment and the project's configuration. The embedding dimension must match the embedding model and the vector collection configuration.

**Security note:** Never commit your actual `.env` file or publish API keys. Only the safe `.env.example` template should be tracked in Git.

### 4. Ingest the Book into Qdrant

Run ingestion commands from the `backend` directory.

First, perform a dry run to inspect parsing and chunking without making embedding API calls or writing to Qdrant:

```powershell
python scripts/ingest_book.py --dry-run
```

Then run the actual ingestion:

```powershell
python scripts/ingest_book.py
```

Additional supported options:

| Option | Purpose |
|---|---|
| `--dry-run` | Parse and chunk content without embedding or Qdrant writes |
| `--only <module-folder>` | Ingest a selected module only |
| `--limit-chunks N` | Limit the number of chunks for a small test run |
| `--recreate` | Rebuild the collection after confirmation; existing collection data may be deleted |

Ingestion may require external API calls and can be affected by provider rate limits. Review the script's help output and configuration before running destructive operations.

### 5. Run the Backend

From the `backend` directory, start the FastAPI development server:

```powershell
uvicorn app.main:app --reload
```

The backend should be available at:

- Health check: http://localhost:8000/health
- API documentation during local development: http://localhost:8000/docs

The health endpoint confirms that the application is responding. It does not necessarily prove that every external dependency is available.

### 6. Run the Frontend

Open a **second terminal** at the repository root:

```powershell
cd book
npm install
npm run start
```

Open the local website:

http://localhost:3000

Navigate through the book and select the **Ask AI** chatbot to ask a question about the book's content.

If the frontend needs to connect to a different backend, configure `BOOK_API_URL` according to the existing frontend configuration. Use the appropriate backend URL for local development or production.

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Checks whether the backend is responding |
| `/api/chat` | As configured by the application | Accepts a question and returns a grounded answer with relevant sources |

The chat endpoint's request and response schema should be checked in the FastAPI application or local API documentation. Do not assume a specific JSON payload without consulting the implemented schema.

## Evaluation and Testing

The repository includes an evaluation dataset and automated tests to support quality checks.

### Run Automated Tests

From the `backend` directory, with the virtual environment activated:

```powershell
pytest
```

### Evaluate RAG Quality

The `backend/evaluation/questions.json` file contains evaluation questions. The backend scripts also include evaluation-related utilities.

Use the evaluation script's help output or its documentation to confirm the exact command before running it.

When evaluating the chatbot, consider:

- Whether relevant passages are retrieved.
- Whether answers are supported by the retrieved context.
- Whether source links point to the correct chapters.
- Whether out-of-scope questions receive a refusal.
- Whether errors are handled without exposing sensitive information.

No evaluation score or test result is claimed here; run the project's tests and evaluation tools to establish actual results.

## Security

Security and reliable behavior are important parts of this project.

- **Secret management:** API keys belong in backend environment variables, never in frontend source code.
- **Git hygiene:** exclude `.env`, `.cache/`, virtual environments, and generated build artifacts from version control as appropriate.
- **CORS:** configure `ALLOWED_ORIGINS` to allow only trusted frontend origins.
- **Input validation:** validate and limit user input.
- **Safe rendering:** render chatbot responses as text rather than trusting arbitrary HTML.
- **Prompt-injection resistance:** treat retrieved document passages as reference data, not as instructions that can override the system's RAG rules.
- **Error handling:** avoid exposing stack traces, credentials, or internal configuration in public responses.
- **Production configuration:** supply secrets through the hosting platform's environment settings and disable development-only API documentation when configured for production.

A refusal strategy and retrieval threshold help reduce unsupported answers, but no RAG system can guarantee that every generated response is correct.

## Known Limitations

- Answers are limited to the information available in the book.
- Google Gemini usage may be subject to API quotas and rate limits.
- Each question is handled independently; the chatbot does not currently retain conversational memory across questions.
- Very short or ambiguous questions may retrieve less relevant passages.
- Retrieval quality depends on content chunking, embedding quality, and threshold configuration.
- The application depends on the availability and configuration of its external model and vector database services.

## Roadmap

Potential future improvements include:

- Improving retrieval for short or ambiguous questions.
- Expanding the evaluation dataset and reporting retrieval and answer-quality metrics.
- Adding broader test coverage for edge cases and out-of-scope queries.
- Improving deployment documentation and production monitoring.
- Exploring conversational memory while preserving the book-only answering policy.
- Expanding the educational content and adding more learning resources.

## Author

**Ayesha Tubassum**

AI & Data Science student interested in building practical AI applications, retrieval-based systems, and interactive learning tools.

- **GitHub:** [ayesha-tubassum](https://github.com/ayesha-tubassum)
- **LinkedIn:** [Ayesha Tubassum](https://www.linkedin.com/in/ayesha-tabassum-59969a392/)

## License

No license has been specified in this README. Until a license file is added to the repository, do not assume that the project is open source or that others have permission to reuse, modify, or distribute its code or content.

---

*Built as a hands-on project exploring AI, Data Science education, and Retrieval-Augmented Generation.*
