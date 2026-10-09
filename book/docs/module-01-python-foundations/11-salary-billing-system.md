---
id: salary-billing-system
title: Project — Salary and Billing System
sidebar_position: 11
---

# Project — Salary and Billing System

## Project Goal

Build a simple billing or salary management system using classes.

## Example

```python
class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def calculate_annual_salary(self):
        return self.salary * 12

    def display(self):
        print("Employee:", self.name)
        print("Monthly Salary:", self.salary)
        print("Annual Salary:", self.calculate_annual_salary())


employee = Employee("Ali", 80000)

employee.display()
```

## Extending the Project

A more complete salary system could include:

- Employee ID
- Basic salary
- Allowances
- Deductions
- Tax
- Net salary

For a billing system, similar principles can be used for:

- Product
- Quantity
- Unit price
- Discount
- Total amount

The important lesson is not simply producing the final program. The goal is learning how to identify entities and represent them using classes.

## Practice Challenge

Create a `Product` class with:

- Product name
- Product ID
- Price
- Quantity

Then create a method that calculates the total cost.
