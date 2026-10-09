---
id: exception-handling
title: Exception Handling
sidebar_position: 8
---

# Exception Handling

## Learning Objectives

You will learn:

- What exceptions are.
- Why errors need to be handled.
- How `try` and `except` work.
- How `finally` works.
- How exception handling improves applications.

## What Is an Exception?

An exception is an error condition that occurs while a program is executing.

For example:

```python
number = int("hello")
```

This cannot be converted into an integer and causes an exception.

## Handling Exceptions

```python
try:
    number = int(input("Enter a number: "))
    print(number)
except ValueError:
    print("Please enter a valid number.")
```

Instead of terminating unexpectedly, the program can provide a useful message.

## `finally`

The `finally` block executes after the `try`/`except` process:

```python
try:
    print("Processing...")
except Exception:
    print("Something went wrong.")
finally:
    print("Operation finished.")
```

## Why Exception Handling Matters

Real applications interact with unpredictable inputs. Users can enter invalid values, provide missing information, or attempt operations that are not allowed.

Good programs handle these situations gracefully.

## Real-World Example

A banking application should not crash simply because a user enters invalid withdrawal information. Instead, it should report the problem and allow the user to try again.

## Review Questions

1. What is an exception?
2. What does `try` do?
3. What is the purpose of `except`?
4. When is `finally` useful?
5. Why is exception handling important in real applications?
