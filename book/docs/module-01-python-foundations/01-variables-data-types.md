---
id: variables-data-types
title: Variables and Data Types
sidebar_position: 1
---

# Variables and Data Types

## Learning Objectives

After completing this chapter, you will be able to:

- Understand what a variable is.
- Create and assign variables in Python.
- Identify common Python data types.
- Understand integers, floats, strings, and booleans.
- Check the type of a value.
- Convert values from one type to another.
- Use variables in practical programs.

## Introduction

A program needs a way to store information. For example, a student management system may need to store a student's name, age, marks, and student ID.

Python allows us to store these values using **variables**. A variable can be thought of as a named reference to a value.

```python
name = "Ali"
age = 20
marks = 85
passed = True
```

Here, `name` refers to a string, `age` and `marks` refer to integers, and `passed` refers to a Boolean value.

## Creating Variables

Python does not require a separate declaration statement before assigning a variable.

```python
name = "Ayesha"
age = 21
```

The `=` symbol is the assignment operator.

```python
age = 20
age = 21
```

The second assignment changes the value associated with `age`.

## Common Data Types

### Integer

Integers represent whole numbers.

```python
students = 30
temperature = -5
```

### Float

Floats represent decimal numbers.

```python
price = 499.99
height = 5.7
```

### String

Strings represent text.

```python
name = "Ayesha"
course = "Artificial Intelligence"
```

### Boolean

A Boolean represents a logical value:

```python
True
False
```

Example:

```python
is_logged_in = True
```

## Checking Data Types

Python provides the `type()` function.

```python
age = 20
print(type(age))
```

Output:

```text
<class 'int'>
```

## Type Conversion

Sometimes a program receives data in one type but needs another.

```python
age = "20"
```

Here `age` is a string. We can convert it into an integer:

```python
age = int(age)
```

Other common conversions include:

```python
float("10.5")
str(100)
bool(1)
```

## Real-World Example

An online store can calculate a total price using variables:

```python
product_price = 500
quantity = 3

total = product_price * quantity
print(total)
```

Output:

```text
1500
```

Meaningful variable names make programs easier to understand.

## Common Beginner Mistakes

Incorrect:

```python
student name = "Ali"
```

Correct:

```python
student_name = "Ali"
```

Another common mistake is confusing a string with a number:

```python
age = "20"
```

This is text, not an integer.

## Key Takeaways

- Variables provide named references to values.
- Common Python types include `int`, `float`, `str`, and `bool`.
- `type()` can inspect a value's type.
- Compatible values can be converted from one type to another.

## Review Questions

1. What is a variable?
2. What is the difference between an integer and a float?
3. What data type is `"100"`?
4. What does `type()` do?
5. Why might type conversion be necessary?
