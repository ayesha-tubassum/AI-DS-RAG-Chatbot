---
id: object-oriented-programming
title: Object-Oriented Programming
sidebar_position: 9
---

# Object-Oriented Programming

## Learning Objectives

You will learn:

- What objects and classes are.
- How to create classes.
- What attributes and methods are.
- What encapsulation means.
- What inheritance means.
- How OOP can model real-world systems.

## Introduction to OOP

Object-Oriented Programming (OOP) is a programming approach based around objects.

Consider a real-world student. A student has a name, age, roll number, and marks. A student can also perform actions such as displaying information, calculating a grade, or updating marks.

OOP allows us to model such entities in code.

## Classes

A class is a blueprint for creating objects.

```python
class Student:
    pass
```

## Objects

An object is an instance of a class.

```python
student1 = Student()
student2 = Student()
```

## Attributes

Attributes represent data belonging to an object.

```python
class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks
```

Creating an object:

```python
student = Student("Ali", 85)

print(student.name)
print(student.marks)
```

## Methods

Methods are functions defined inside classes.

```python
class Student:
    def __init__(self, name, marks):
        self.name = name
        self.marks = marks

    def display(self):
        print(self.name, self.marks)
```

## Encapsulation

Encapsulation refers to organizing data and behavior within a class and controlling how an object's internal state is accessed or changed.

The goal is to make objects easier to use safely and maintain.

## Inheritance

Inheritance allows one class to derive from another.

```python
class Person:
    def speak(self):
        print("Hello")


class Student(Person):
    pass
```

Now `Student` can use functionality inherited from `Person`.

## Real-World Example

A university application could have:

```text
Person
 ├── Student
 └── Teacher
```

Common information can belong to `Person`, while specialized behavior can belong to `Student` and `Teacher`.

## Review Questions

1. What is a class?
2. What is an object?
3. What is an attribute?
4. What is a method?
5. What is inheritance?
6. Why is OOP useful for real-world systems?
