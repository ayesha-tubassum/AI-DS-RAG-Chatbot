---
id: 01-neural-network-fundamentals
title: Neural Network Fundamentals
sidebar_position: 1
---

# Neural Network Fundamentals

## Learning Objectives
By the end of this chapter, you should be able to:
- Explain the idea of an artificial neuron and perceptron.
- Describe forward propagation and backpropagation.
- Understand weights, bias, activation functions, and loss functions.
- Explain how neural networks learn from data.

## 1. What Is a Neural Network?
A neural network is a machine-learning model made from connected computational units called neurons. It learns relationships between inputs and outputs by adjusting numerical parameters called weights.

A simple structure is:

```text
Input Layer → Hidden Layer(s) → Output Layer
```

## 2. The Perceptron
A basic neuron computes a weighted sum:

```text
z = w₁x₁ + w₂x₂ + ... + wₙxₙ + b
```

where `w` represents weights and `b` represents bias.

An activation function then transforms `z`.

## 3. Forward Propagation
During forward propagation, information moves from the input layer toward the output layer.

```text
Input
  ↓
Weighted Sum
  ↓
Activation
  ↓
Hidden Layers
  ↓
Output
```

The model produces a prediction from the current weights and biases.

## 4. Activation Functions
Activation functions introduce non-linearity.

Common examples include:
- ReLU
- Sigmoid
- Tanh
- Softmax

ReLU:

```python
def relu(x):
    return max(0, x)
```

In practical frameworks, use optimized library implementations rather than a hand-written function.

## 5. Loss Functions
A loss function measures how far a prediction is from the expected target.

Examples:
- Mean Squared Error for many regression tasks.
- Binary Cross-Entropy for binary classification.
- Categorical Cross-Entropy for multi-class classification.

## 6. Backpropagation
Backpropagation calculates how model parameters contributed to the loss. Gradients are propagated backward through the network, and an optimizer updates weights.

```text
Prediction
   ↓
Loss
   ↓
Gradients
   ↓
Weight Updates
   ↓
Better Prediction
```

## 7. Optimizers
Common optimizers include:
- SGD
- Adam
- RMSprop

A learning rate controls the size of parameter updates.

## 8. A Small Keras Model

```python
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Dense(64, activation="relu", input_shape=(20,)),
    tf.keras.layers.Dense(32, activation="relu"),
    tf.keras.layers.Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)
```

The architecture and output activation must match the task.

## Key Takeaways
- A neuron combines inputs using weights and bias.
- Forward propagation generates predictions.
- Loss measures prediction error.
- Backpropagation supplies gradients for learning.
- Activation functions allow neural networks to model nonlinear relationships.

## Review Questions
1. What is a perceptron?
2. What is forward propagation?
3. Why do neural networks use activation functions?
4. What does a loss function measure?
5. What happens during backpropagation?

