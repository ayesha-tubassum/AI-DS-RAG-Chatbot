---
id: 05-nlp-text-cleaning
title: NLP Text Cleaning
sidebar_position: 5
---

# NLP Text Cleaning

## Learning Objectives
Prepare raw text for deep-learning models.

## 1. Why Clean Text?
Text data can contain:
- HTML or markup
- Unnecessary whitespace
- Inconsistent casing
- URLs
- Punctuation
- Noise specific to the application

The correct cleaning strategy depends on the task. Over-cleaning can remove useful information.

## 2. Basic Example

```python
import re

def clean_text(text):
    text = text.lower().strip()
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text
```

## 3. Tokenization
Tokenization converts text into units that a model can process.

Depending on the architecture, tokens may be words, subwords, or characters.

## 4. Padding
Sequences often need a common length within a batch.

```python
from tensorflow.keras.utils import pad_sequences

padded = pad_sequences(
    sequences,
    maxlen=100,
    padding="post"
)
```

## 5. Important Warning
Do not remove words or symbols simply because they look unimportant. Negation, punctuation, and domain-specific terms can affect meaning.

## Key Takeaways
Text cleaning should be purposeful, reproducible, and appropriate for the downstream model.

## Review Questions
1. Why is text cleaning needed?
2. What is tokenization?
3. Why is padding used?
4. Why can over-cleaning hurt NLP performance?

