---
id: 06-vector-databases-faiss-pinecone
title: Vector Databases: FAISS and Pinecone
sidebar_position: 6
---

# Vector Databases: FAISS and Pinecone

## 1. What Is an Embedding?

An embedding represents content as a numerical vector.

```text
Text
 ↓
Embedding Model
 ↓
[0.12, -0.44, 0.81, ...]
```

Semantically related content can have similar vector representations.

## 2. Similarity Search

A vector database can search for vectors close to a query vector.

Common similarity measures include:

- Cosine similarity
- Euclidean distance
- Dot product

## 3. FAISS

FAISS is a library for efficient similarity search over dense vectors. It is useful for local or application-controlled vector retrieval experiments.

Conceptual flow:

```python
documents
   ↓
embeddings
   ↓
FAISS index
   ↓
query embedding
   ↓
nearest neighbors
```

## 4. Pinecone

Pinecone is a managed vector database service that can be used for vector search applications.

The exact setup depends on the service configuration and SDK version.

## 5. Metadata

Useful metadata can include:

```json
{
  "source": "handbook.pdf",
  "page": 12,
  "section": "Attendance"
}
```

Metadata can help filter and cite retrieved information.

## Exercise

Design a vector-store schema for a collection of university PDF documents. Include vector IDs and useful metadata.
