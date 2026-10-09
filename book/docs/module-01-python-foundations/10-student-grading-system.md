---
id: student-grading-system
title: Project — Student Grading System
sidebar_position: 10
---

# Project — Student Grading System

## Project Goal

Build a student grading system using classes and objects.

This project applies:

- Variables
- Data types
- Functions
- Conditional statements
- Classes
- Objects
- Methods

## Requirements

The system should store:

- Student name
- Student ID
- Marks

It should calculate a grade based on the student's marks.

## Example Implementation

```python
class Student:
    def __init__(self, student_id, name, marks):
        self.student_id = student_id
        self.name = name
        self.marks = marks

    def calculate_grade(self):
        if self.marks >= 80:
            return "A"
        elif self.marks >= 70:
            return "B"
        elif self.marks >= 60:
            return "C"
        elif self.marks >= 50:
            return "D"
        else:
            return "F"

    def display(self):
        print("Student ID:", self.student_id)
        print("Name:", self.name)
        print("Marks:", self.marks)
        print("Grade:", self.calculate_grade())


student = Student(101, "Ayesha", 85)

student.display()
```

## What This Project Teaches

The project demonstrates how raw programming concepts can be combined into a small application.

Instead of storing unrelated variables, we create a `Student` object that keeps related information and behavior together.

## Extension Tasks

Try adding:

1. Multiple students.
2. Subject-wise marks.
3. Average marks.
4. Pass/fail status.
5. A method to update marks.
