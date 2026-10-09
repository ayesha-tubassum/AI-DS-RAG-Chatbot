---
id: python-data-structures
title: Python Data Structures
sidebar_position: 6
---

# Python Data Structures

## Learning Objectives

You will learn:

- What data structures are.
- How to use lists.
- How tuples differ from lists.
- How dictionaries store key-value information.
- How sets store unique values.

## Why Data Structures?

Programs often need to store collections of information, such as student names, product prices, employee records, or course information.

Python provides several built-in data structures.

## Lists

A list stores an ordered collection.

```python
students = ["Ali", "Sara", "Ahmed"]
```

Access an item by index:

```python
print(students[0])
```

Lists are mutable:

```python
students.append("Ayesha")
```

## Tuples

A tuple also stores an ordered collection:

```python
coordinates = (10, 20)
```

Tuples are commonly used when the collection should not be modified.

## Dictionaries

A dictionary stores information using key-value pairs:

```python
student = {
    "name": "Ali",
    "age": 20,
    "marks": 85
}
```

Access a value:

```python
print(student["name"])
```

Dictionaries are useful for structured records.

## Sets

A set stores unique elements:

```python
numbers = {1, 2, 3, 3, 4}

print(numbers)
```

Duplicate values are not retained as separate set elements.

## Choosing the Right Structure

- **List:** ordered, changeable collection.
- **Tuple:** ordered collection that should generally remain fixed.
- **Dictionary:** information naturally represented as keys and values.
- **Set:** uniqueness is important.

## Real-World Example

An employee record can be represented as:

```python
employee = {
    "id": 101,
    "name": "Ayesha",
    "department": "Data Science",
    "salary": 80000
}
```

## Review Questions

1. What is a list?
2. How is a tuple different from a list?
3. What is a dictionary?
4. Why are sets useful?
5. Which data structure would you choose for employee information and why?
