---
id: 05-linear-algebra-basics
title: Linear Algebra Basics for Machine Learning
sidebar_position: 5
---

# Linear Algebra Basics for Machine Learning

## Learning Objectives
- Understand scalars, vectors, and matrices.
- Represent data numerically.
- Perform basic vector and matrix operations.
- Understand dot products and matrix multiplication.
- Connect linear algebra to ML.

## 1. Why Linear Algebra?
Machine learning represents data, parameters, and transformations numerically. A dataset can be represented as a matrix where rows are observations and columns are features.

## 2. Scalars
A scalar is one number:
```text
5
10.5
-3
```

## 3. Vectors
A vector is an ordered collection of numbers.

```python
import numpy as np
x = np.array([2, 4, 6])
print(x)
```

## 4. Matrices
A matrix is a rectangular arrangement of numbers.

```python
A = np.array([[1, 2], [3, 4]])
print(A.shape)
```

## 5. Vector Operations
```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

print(a + b)
print(3 * a)
print(np.dot(a, b))
```

The dot product is:
```text
1×4 + 2×5 + 3×6
```

## 6. Matrix Multiplication
```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

print(A @ B)
```

Matrix dimensions must be compatible for multiplication.

## 7. Linear Algebra in ML
Vectors and matrices appear in feature tables, linear regression, neural networks, embeddings, and dimensionality reduction.

## Real-World Example
A house can be represented by a feature vector such as:
```text
[area, bedrooms, age]
```
Many houses form a feature matrix used by an ML algorithm.

## Important Terminology
Scalar, vector, matrix, shape, dot product, matrix multiplication.

## Key Takeaways
- ML data is commonly represented with vectors and matrices.
- Matrix shape matters for valid operations.
- Linear algebra is a foundation for later ML algorithms.

## Review Questions
1. What is a scalar?
2. What is a vector?
3. What does matrix shape describe?
4. What is a dot product?
5. Why is linear algebra important for ML?
