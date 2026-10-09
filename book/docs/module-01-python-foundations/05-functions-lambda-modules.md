---
id: functions-lambda-modules
title: Functions, Lambda Functions and Modules
sidebar_position: 5
---

# Functions, Lambda Functions and Modules

## Learning Objectives

You will learn:

- What functions are.
- Why reusable functions are important.
- How to create parameters and return values.
- What lambda functions are.
- What Python modules are.
- How to import modules.

## What Is a Function?

A function is a reusable block of code designed to perform a particular task.

```python
def greet():
    print("Hello!")
```

Call it using:

```python
greet()
```

## Function Parameters

Functions can receive information:

```python
def greet(name):
    print("Hello", name)

greet("Ayesha")
```

## Return Values

A function can return a result:

```python
def add(a, b):
    return a + b

result = add(10, 20)
print(result)
```

## Why Functions Matter

Functions improve:

- Reusability
- Organization
- Readability
- Testing
- Maintainability

## Lambda Functions

A lambda is a small anonymous function:

```python
square = lambda x: x * x

print(square(5))
```

Lambda functions are useful for short operations, including some uses with `map()`, `filter()`, and sorting.

## Modules

A module is a Python file containing reusable code.

For example:

```python
import math

print(math.sqrt(25))
```

Another example:

```python
import random

number = random.randint(1, 10)
print(number)
```

## Real-World Example

A billing program can use a reusable function:

```python
def calculate_total(price, quantity):
    return price * quantity

total = calculate_total(500, 3)
print(total)
```

The same function can be reused for different products.

## Review Questions

1. What is a function?
2. What is the purpose of a parameter?
3. What does `return` do?
4. What is a lambda function?
5. Why do programmers use modules?
