---
id: conditional-statements
title: Conditional Statements
sidebar_position: 3
---

# Conditional Statements

## Learning Objectives

You will learn to:

- Make decisions using Python.
- Use `if`, `elif`, and `else`.
- Combine conditions.
- Build simple decision-making programs.

## Why Do Programs Need Decisions?

Real-world programs rarely perform exactly the same action every time.

For example:

- If a student gets 50 or more marks, they pass.
- If a user is logged in, show their dashboard.
- If the temperature is high, display a warning.

Python uses conditional statements for these decisions.

## The `if` Statement

```python
age = 20

if age >= 18:
    print("You are an adult.")
```

The indented code runs only when the condition is true.

## `if` and `else`

```python
marks = 45

if marks >= 50:
    print("Pass")
else:
    print("Fail")
```

## Multiple Conditions

```python
marks = 75

if marks >= 80:
    print("A Grade")
elif marks >= 70:
    print("B Grade")
elif marks >= 60:
    print("C Grade")
else:
    print("Needs Improvement")
```

## Nested Conditions

Conditions can appear inside other conditions:

```python
age = 20
has_id = True

if age >= 18:
    if has_id:
        print("Access granted")
```

Nested conditions should be used carefully because excessive nesting can make programs harder to understand.

## Real-World Example

A simple loan eligibility rule:

```python
income = 100000
credit_score = 750

if income >= 50000 and credit_score >= 700:
    print("Eligible")
else:
    print("Not eligible")
```

## Common Mistake

Python uses indentation to define blocks.

Incorrect:

```python
if age >= 18:
print("Adult")
```

Correct:

```python
if age >= 18:
    print("Adult")
```

## Review Questions

1. What is the purpose of `if`?
2. When is `else` executed?
3. Why do we use `elif`?
4. What is a nested condition?
5. Why is indentation important in Python?
