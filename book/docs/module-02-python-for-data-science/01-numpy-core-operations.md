---
id: numpy-core-operations
title: NumPy Core Operations
sidebar_position: 1
---

# NumPy Core Operations

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain why NumPy is useful in data science.
- Create one-dimensional and two-dimensional arrays.
- Understand array shape, dimensions, and data types.
- Perform arithmetic and vectorized operations.
- Use common mathematical functions.
- Understand the difference between Python lists and NumPy arrays.

## 1. What is NumPy?

NumPy (Numerical Python) is a Python library designed for numerical computing. Data science frequently involves numbers arranged in tables, vectors, and matrices. NumPy provides an efficient array structure and operations for working with this kind of data.

A NumPy array can contain many values of the same general data type and allows mathematical operations to be applied to an entire collection without writing a loop for every value.

```python
import numpy as np

scores = np.array([72, 81, 65, 90])
print(scores)
```

## 2. Python Lists vs NumPy Arrays

Python lists are general-purpose containers. NumPy arrays are designed for numerical operations.

```python
numbers = [1, 2, 3, 4]
array = np.array(numbers)

print(array * 2)
```

The NumPy expression multiplies every element by 2. This style of operation is called **vectorization**.

## 3. Creating Arrays

```python
a = np.array([10, 20, 30])

matrix = np.array([
    [1, 2, 3],
    [4, 5, 6]
])

zeros = np.zeros((2, 3))
ones = np.ones((2, 3))
sequence = np.arange(0, 10, 2)
```

## 4. Shape, Dimensions, and Size

```python
data = np.array([
    [10, 20],
    [30, 40],
    [50, 60]
])

print(data.shape)
print(data.ndim)
print(data.size)
```

- `shape` describes the dimensions.
- `ndim` gives the number of dimensions.
- `size` gives the total number of elements.

## 5. Indexing and Slicing

```python
values = np.array([10, 20, 30, 40, 50])

print(values[0])
print(values[1:4])
```

For two-dimensional data:

```python
matrix = np.array([
    [10, 20, 30],
    [40, 50, 60]
])

print(matrix[0, 1])
print(matrix[:, 1])
```

## 6. Vectorized Arithmetic

```python
prices = np.array([100, 200, 300])
discounted = prices * 0.90

print(discounted)
```

Common operations include:

```python
x = np.array([1, 4, 9])

print(x + 2)
print(x * 3)
print(x ** 2)
print(x / 2)
```

## 7. Mathematical Functions

NumPy provides many mathematical functions.

```python
values = np.array([1, 4, 9, 16])

print(np.sqrt(values))
print(np.mean(values))
print(np.max(values))
print(np.min(values))
print(np.sum(values))
```

## 8. Practical Example: Student Scores

```python
scores = np.array([75, 82, 68, 91, 88])

print("Average:", np.mean(scores))
print("Highest:", np.max(scores))
print("Lowest:", np.min(scores))
```

This pattern is useful when analysing numerical datasets.

## Important Terminology

- **Array:** NumPy's core numerical data structure.
- **Vectorization:** Performing an operation on many values at once.
- **Dimension:** A level of structure in an array.
- **Shape:** The size of an array along each dimension.
- **Indexing:** Accessing particular elements.
- **Slicing:** Selecting a range or section of an array.

## Key Takeaways

- NumPy is fundamental for numerical work in Python.
- Arrays support efficient mathematical operations.
- `shape`, `ndim`, and `size` help you understand array structure.
- Vectorized operations reduce the need for explicit loops.
- NumPy provides many mathematical functions for analysis.

## Review Questions

1. What problem does NumPy solve in data science?
2. What is vectorization?
3. What is the difference between `shape` and `size`?
4. How would you calculate the average of a NumPy array?
5. Create a 2 × 3 NumPy array and print its second column.
