---
id: 01-transformers
title: Transformers
sidebar_position: 1
---

# Transformers

## Learning Goal

Understand the core architecture behind modern language models.

## 1. Why Transformers?

Traditional sequence models process tokens step by step. Transformers introduced a powerful mechanism called **attention**, allowing the model to consider relationships between tokens more effectively.

## 2. High-Level Architecture

```text
Text
 ↓
Tokenization
 ↓
Token Embeddings
 ↓
Positional Information
 ↓
Transformer Layers
 ↓
Output Representations
 ↓
Prediction
```

## 3. Self-Attention

Self-attention allows a token to assign importance to other tokens in the sequence.

For example:

> "The animal did not cross the road because it was tired."

A language model needs to understand what "it" refers to. Attention helps the model use contextual relationships.

## 4. Query, Key and Value

At a conceptual level, attention creates:

- **Query:** what the current token is looking for
- **Key:** information used to match relevance
- **Value:** information passed forward

The attention calculation is commonly represented as:

```text
Attention(Q, K, V) =
softmax(QKᵀ / √dₖ)V
```

You do not need to memorize the equation initially. Focus on understanding that attention computes relevance between tokens.

## 5. Encoder and Decoder

Transformer architectures can use:

- Encoder components
- Decoder components
- Encoder-decoder combinations

BERT is primarily encoder-based, while GPT-style models are decoder-based.

## Exercise

Explain self-attention in your own words and draw a simple Transformer pipeline.
