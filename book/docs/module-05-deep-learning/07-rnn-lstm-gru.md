---
id: 07-rnn-lstm-gru
title: RNN, LSTM and GRU
sidebar_position: 7
---

# RNN, LSTM and GRU

## Learning Objectives
Understand neural networks designed for sequential information.

## 1. Sequential Data
Examples include:
- Text
- Time-series measurements
- Sensor readings
- Ordered events

The order of observations can contain important information.

## 2. Recurrent Neural Networks
An RNN processes a sequence step by step while maintaining a hidden state.

```text
x₁ → RNN → h₁
x₂ → RNN → h₂
x₃ → RNN → h₃
```

The hidden state carries information forward.

## 3. LSTM
Long Short-Term Memory networks introduce gates that help control information flow and preserve useful information over longer sequences.

## 4. GRU
Gated Recurrent Units use a simpler gating structure than LSTM while serving a similar purpose.

## 5. Keras Example

```python
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(10000, 128),
    tf.keras.layers.LSTM(64),
    tf.keras.layers.Dense(1, activation="sigmoid")
])
```

A GRU can be substituted:

```python
tf.keras.layers.GRU(64)
```

## 6. RNN vs LSTM vs GRU

| Model | Main Idea |
|---|---|
| RNN | Basic recurrent hidden state |
| LSTM | Gated memory for longer dependencies |
| GRU | Simplified gated recurrent architecture |

## Key Takeaways
RNNs, LSTMs, and GRUs are designed to process ordered data. LSTM and GRU introduce gating mechanisms to manage information across a sequence.

## Review Questions
1. What makes text sequential?
2. What is a hidden state?
3. Why were LSTMs introduced?
4. How does GRU relate to LSTM?

