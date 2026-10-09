---
id: 08-class-project-rag-vector-database
title: Class Project — RAG System with Vector Database
sidebar_position: 8
---

# Class Project — RAG System with Vector Database

## Goal

Develop a retrieval-augmented system using vector search.

## Architecture

```text
Documents
   ↓
Chunking
   ↓
Embeddings
   ↓
FAISS / Pinecone
   ↓
Similarity Search
   ↓
Retrieved Context
   ↓
Prompt
   ↓
LLM
   ↓
Answer + Sources
```

## Requirements

1. Collect a small document corpus.
2. Extract and clean text.
3. Split documents into chunks.
4. Generate embeddings.
5. Store vectors.
6. Retrieve relevant chunks.
7. Construct an LLM prompt with retrieved context.
8. Generate an answer.
9. Display source metadata where possible.

## Evaluation

Create at least 10 questions and record:

- Retrieved chunks
- Final answer
- Whether the answer is supported
- Retrieval problems
- Hallucination cases

## Deliverables

- RAG application
- Document corpus description
- Vector-store implementation
- Evaluation table
- README
