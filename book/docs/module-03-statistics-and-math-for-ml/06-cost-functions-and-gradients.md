---
id: 06-cost-functions-and-gradients
title: Cost Functions and Gradients
sidebar_position: 6
---

# Cost Functions and Gradients

## Learning Objectives
- Explain prediction error.
- Understand cost and loss functions.
- Explain Mean Squared Error.
- Understand gradients and gradient descent.
- Explain the role of learning rate.

## 1. Why Optimization?
A machine learning model makes predictions. Training attempts to adjust model parameters so predictions improve according to a selected objective.

A **loss** or **cost** function provides a numerical measure of error. Terminology varies by context.

## 2. Mean Squared Error
MSE is a common regression loss:

```text
MSE = Average of (actual - predicted)²
```

```python
from sklearn.metrics import mean_squared_error

actual = [10, 20, 30]
predicted = [12, 18, 25]

print(mean_squared_error(actual, predicted))
```

## 3. Gradient
A gradient describes how an objective changes with respect to its parameters. It contains partial derivatives for a multivariable function.

## 4. Gradient Descent
The basic process is:
1. Start with parameter values.
2. Calculate the objective.
3. Calculate the gradient.
4. Move parameters in a direction that reduces the objective.
5. Repeat.

Conceptually:
```text
new parameter = old parameter - learning rate × gradient
```

## 5. Learning Rate
The learning rate controls update size. A value that is too large can make training unstable; a value that is too small can make optimization slow.

## 6. Simple Example
For:
```text
f(x) = x²
```
the derivative is:
```text
f'(x) = 2x
```
Gradient-based optimization can move x toward the minimum.

## Real-World Example
A house-price model compares predicted prices with actual prices. Its optimization process adjusts parameters to reduce the selected training loss.

## Important Terminology
Loss, cost, gradient, gradient descent, learning rate, parameter.

## Key Takeaways
- Loss functions measure model error.
- MSE is common for regression.
- Gradients describe local change.
- Gradient descent uses gradients to optimize parameters.
- Learning rate controls update size.

## Review Questions
1. Why does an ML model need a loss function?
2. What does MSE measure?
3. What is a gradient?
4. What is gradient descent?
5. What can happen if the learning rate is too large?
