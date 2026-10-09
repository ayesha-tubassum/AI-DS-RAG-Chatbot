---
id: operators
title: Operators
sidebar_position: 2
---

# Operators

## Learning Objectives

You will learn how to:

- Perform arithmetic calculations.
- Compare values.
- Combine logical conditions.
- Understand assignment operators.
- Use operators in practical programs.

## Arithmetic Operators

```python
a = 10
b = 3

print(a + b)
print(a - b)
print(a * b)
print(a / b)
```

| Operator | Meaning |
| --- | --- |
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `//` | Floor division |
| `%` | Modulus |
| `**` | Exponentiation |

## Comparison Operators

Comparison operators compare values and normally produce `True` or `False`.

```python
age = 20

print(age > 18)
print(age == 20)
print(age != 15)
```

## Logical Operators

### `and`

Both conditions must be true.

```python
age = 25
has_id = True

print(age >= 18 and has_id)
```

### `or`

At least one condition must be true.

```python
is_student = True
is_employee = False

print(is_student or is_employee)
```

### `not`

Reverses a Boolean condition.

```python
is_logged_in = False
print(not is_logged_in)
```

## Assignment Operators

The normal assignment operator is `=`. Python also supports:

```python
+=
-=
*=
/=
```

Example:

```python
score = 50
score += 10

print(score)
```

Output:

```text
60
```

## Real-World Example

A shopping application may check whether a customer qualifies for free delivery:

```python
order_amount = 2500
membership = True

free_delivery = order_amount >= 2000 or membership
print(free_delivery)
```

## Key Takeaways

Operators allow programs to calculate values, compare information, make logical decisions, and update variables.

## Review Questions

1. What is the difference between `/` and `//`?
2. What does `%` return?
3. What is the purpose of `==`?
4. How does `and` differ from `or`?
5. What does `+=` do?
