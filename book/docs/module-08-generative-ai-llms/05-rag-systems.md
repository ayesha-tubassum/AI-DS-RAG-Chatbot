---
id: 05-rag-systems
title: Retrieval-Augmented Generation (RAG)
sidebar_position: 5
---

# Retrieval-Augmented Generation (RAG)

## 1. What Is RAG?

**Retrieval-Augmented Generation** combines information retrieval with language generation.

Instead of asking an LLM to answer only from its learned parameters:

```text
Question → LLM → Answer
```

RAG adds relevant external context:

```text
Question
   ↓
Retriever
   ↓
Relevant Documents
   ↓
Prompt + Context
   ↓
LLM
   ↓
Answer
```

## 2. Typical RAG Pipeline

```text
Documents
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Database
   ↓
Similarity Search
   ↓
Retrieved Context
   ↓
LLM
   ↓
Grounded Response
```

## 3. Why Chunking?

Long documents are commonly divided into smaller chunks so retrieval can find relevant sections rather than passing an entire document every time.

Chunk size and overlap should be chosen based on the document type and task.

## 4. RAG Advantages

- Can use external documents
- Useful for private knowledge bases
- Knowledge can be updated without retraining the base model
- Retrieved context can improve grounding

## 5. RAG Limitations

RAG can still fail because:

- Retrieval may return irrelevant chunks.
- The answer may not follow the retrieved context.
- Documents may contain conflicting information.
- Poor chunking can reduce retrieval quality.

## Exercise

Design a RAG system for a university handbook. Identify document ingestion, chunking, embedding, retrieval, prompting, and answer-generation steps.
