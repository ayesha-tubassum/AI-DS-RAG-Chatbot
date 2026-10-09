---
id: 06-text-embeddings
title: Text Embeddings
sidebar_position: 6
---

# Text Embeddings

## 1. What Are Embeddings?
Embeddings represent text as numerical vectors. Similar meanings can be represented by vectors that are useful for downstream tasks.

```text
Text → Tokens → Embedding Vectors
```

## 2. Why Embeddings Matter
Machine-learning models operate on numerical representations. Embeddings allow semantic information to be represented in a continuous vector space.

Applications include:
- Sentiment analysis
- Text classification
- Semantic search
- Recommendation systems

## 3. Keras Embedding Layer

```python
embedding = tf.keras.layers.Embedding(
    input_dim=10000,
    output_dim=128
)
```

The layer learns an embedding vector for each token index during training.

## 4. Pre-trained Representations
Pre-trained language representations can also be reused. Their suitability depends on the task and model architecture.

## 5. Example Concept
Suppose the vocabulary contains 10,000 tokens and each token receives a 128-dimensional vector. The embedding layer learns a `10000 × 128` parameter matrix.

## Key Takeaways
Embeddings convert discrete text tokens into dense numerical representations that neural networks can process.

## Review Questions
1. What is an embedding?
2. Why are embeddings useful?
3. What does embedding dimension mean?
4. Name two applications of text embeddings.

