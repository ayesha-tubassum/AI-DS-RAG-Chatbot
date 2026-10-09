---
id: library-management-system
title: Home Project — Library Management System
sidebar_position: 13
---

# Home Project — Library Management System

## Project Goal

Build a simple system for managing books and members.

The syllabus includes a Library Management System using file handling.

## Core Entities

### Book

- Book ID
- Title
- Author
- Availability

### Member

- Member ID
- Name
- Contact information

## Suggested Features

```text
1. Add Book
2. View Books
3. Add Member
4. View Members
5. Issue Book
6. Return Book
7. Search Book
8. Exit
```

## Example Book Structure

```python
book = {
    "id": 101,
    "title": "Python Basics",
    "author": "Example Author",
    "available": True
}
```

## Converting the Book to a Class

```python
class Book:
    def __init__(self, book_id, title, author):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.available = True
```

This gives students an opportunity to connect file handling with OOP.

## Suggested Challenge

Add methods for:

- Issuing a book.
- Returning a book.
- Checking availability.
- Displaying book information.

Then save the records so they remain available after the program closes.
