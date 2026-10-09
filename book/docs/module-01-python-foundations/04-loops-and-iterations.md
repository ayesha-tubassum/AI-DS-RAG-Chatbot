---
id: loops-and-iterations
title: Loops and Iterations
sidebar_position: 4
---

# Loops and Iterations

## Learning Objectives

You will learn:

- Why loops are useful.
- How `for` loops work.
- How `while` loops work.
- How to use `break`.
- How to use `continue`.

## Why Use Loops?

Imagine printing the numbers from 1 to 1,000 manually. That would be inefficient.

Loops allow a program to repeat instructions automatically.

## The `for` Loop

```python
for number in range(5):
    print(number)
```

Output:

```text
0
1
2
3
4
```

A starting point can also be specified:

```python
for number in range(1, 6):
    print(number)
```

## Looping Through a List

```python
students = ["Ali", "Sara", "Ahmed"]

for student in students:
    print(student)
```

## The `while` Loop

A `while` loop continues while its condition remains true.

```python
count = 1

while count <= 5:
    print(count)
    count += 1
```

## `break`

`break` stops a loop.

```python
for number in range(10):
    if number == 5:
        break

    print(number)
```

## `continue`

`continue` skips the current iteration.

```python
for number in range(5):
    if number == 2:
        continue

    print(number)
```

## Real-World Example

Find the first failed student:

```python
marks = [80, 75, 65, 40, 90]

for mark in marks:
    if mark < 50:
        print("First failed mark:", mark)
        break
```

## Common Mistake

A `while` loop must eventually change the condition. Otherwise, it may continue indefinitely.

```python
count = 1

while count <= 5:
    print(count)
```

Here `count` never changes.

## Review Questions

1. Why are loops useful?
2. What does `range()` do?
3. What is the difference between `for` and `while`?
4. What does `break` do?
5. What does `continue` do?
