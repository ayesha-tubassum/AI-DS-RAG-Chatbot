---
id: 02-tool-using-agents
title: Tool-Using Agents
sidebar_position: 2
---

## Learning Objectives
Explain tool calling and design tools with validation and permissions.

## What Is a Tool?
A **tool** is a function or external service an agent can invoke, such as a calculator, database query, approved file reader, or search function. The model may propose a call, but the application should validate and execute it.

## Design Principles
A good tool has a clear purpose, documented inputs and outputs, input validation, helpful errors, timeouts, limited permissions, and appropriate logging. Avoid unrestricted shell, filesystem, or account access when a narrow function is sufficient.

## Python Example
```python
def calculate_total(prices):
    if not isinstance(prices, list):
        raise TypeError("prices must be a list")
    if not all(isinstance(x, (int, float)) and x >= 0 for x in prices):
        raise ValueError("prices must be non-negative numbers")
    return sum(prices)

print(calculate_total([12.5, 7, 3.5]))
```

## Tool-Calling Workflow
1. The user makes a request.
2. The model proposes a tool and arguments.
3. The application validates arguments and permissions.
4. The tool executes and returns a result.
5. The model explains the result or selects another step.

Require human confirmation for consequential actions such as sending messages, deleting data, purchases, or production changes. Treat retrieved text and tool output as data, not trusted instructions.

## Key Takeaways
- Tools connect agents to external capabilities.
- Validate every argument and minimize permissions.
- Deciding on an action is different from authorizing it.

## Review Questions
1. What is a tool?
2. Why validate tool arguments?
3. Give two actions that should require confirmation.
