---
id: file-handling
title: File Handling
sidebar_position: 7
---

# File Handling

## Learning Objectives

You will learn:

- Why files are used.
- How to open files.
- How to read files.
- How to write files.
- How to use context managers.

## Why File Handling?

Variables store information while a program is running. Files allow information to persist after the program ends.

For example, an employee record system may store employee information in a file.

## Reading a File

```python
file = open("students.txt", "r")

content = file.read()

print(content)

file.close()
```

The `"r"` mode means read.

## Writing to a File

```python
file = open("students.txt", "w")

file.write("Ali\n")
file.write("Sara\n")

file.close()
```

The `"w"` mode is used for writing.

## Using `with`

A better approach is:

```python
with open("students.txt", "r") as file:
    content = file.read()

print(content)
```

The context manager helps ensure that the file is properly handled after the block finishes.

## Common File Modes

| Mode | Purpose |
| --- | --- |
| `r` | Read |
| `w` | Write |
| `a` | Append |
| `x` | Create |

## Real-World Example

An employee system might save:

```text
101,Ali,Data Science
102,Sara,Marketing
103,Ahmed,Finance
```

The Python application can later read these records and process them.

## Review Questions

1. Why are files useful?
2. What does `"r"` mean?
3. What happens when a file is opened in `"w"` mode?
4. What is the purpose of `"a"`?
5. Why is `with open(...)` commonly preferred?
