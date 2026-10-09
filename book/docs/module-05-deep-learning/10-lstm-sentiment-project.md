---
id: 10-lstm-sentiment-project
title: Class Project — LSTM Movie Review Sentiment Analyzer
sidebar_position: 10
---

# Class Project — LSTM Movie Review Sentiment Analyzer

## Goal
Predict sentiment from movie reviews using an LSTM network, matching the syllabus project.

## Workflow
```text
Reviews
→ Clean Text
→ Tokenize
→ Pad Sequences
→ Embedding
→ LSTM
→ Classification
```

## Starter Structure

```python
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(20000, 128),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dense(1, activation="sigmoid")
])
```

## Evaluation
Report accuracy, precision, recall, F1-score, and a confusion matrix.

## Error Analysis
Read incorrect reviews and look for:
- Sarcasm
- Negation
- Mixed sentiment
- Unusual vocabulary

## Deliverables
Notebook, preprocessing explanation, model architecture, training curves, evaluation, error analysis, and conclusion.

