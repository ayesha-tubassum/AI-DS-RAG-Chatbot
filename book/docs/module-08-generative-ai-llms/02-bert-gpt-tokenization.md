---
id: 02-bert-gpt-tokenization
title: BERT, GPT and Tokenization
sidebar_position: 2
---

# BERT, GPT and Tokenization

## 1. BERT

BERT is designed around bidirectional contextual representations. It is commonly associated with understanding text and tasks such as classification and question answering.

## 2. GPT

GPT-style models use a decoder-oriented Transformer architecture and are designed for autoregressive text generation.

A simplified generation process is:

```text
Prompt
 ↓
Predict next token
 ↓
Add token
 ↓
Predict next token
 ↓
...
```

## 3. BERT vs GPT

| Concept | BERT | GPT |
|---|---|---|
| Main orientation | Encoder | Decoder |
| Common use | Text understanding | Text generation |
| Context | Bidirectional representation | Autoregressive generation |

This comparison is conceptual; modern model families can have additional architectural variations.

## 4. Tokenization

Language models generally process tokens rather than raw text.

Example:

```text
"Machine learning is useful"
        ↓
["Machine", " learning", " is", " useful"]
        ↓
Token IDs
```

A tokenizer converts text into a representation the model can process.

## 5. Why Tokenization Matters

Tokenization affects:

- Input length
- Context usage
- Vocabulary coverage
- Computational cost

## Exercise

Take five sentences and manually identify likely word/subword token boundaries. Then explain why tokenization is not always identical to splitting on spaces.
