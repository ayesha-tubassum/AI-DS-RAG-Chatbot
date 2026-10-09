---
id: 04-langchain-agents
title: Building Agents with LangChain
sidebar_position: 4
---

## Learning Objectives
Understand the role of LangChain and outline a safe agent-development workflow.

## What Is LangChain?
LangChain is a framework for connecting language models with prompts, tools, retrievers, and application logic. Its APIs evolve, so check the current version's official documentation before implementation.

## Core Concepts
- **Model:** generates or evaluates responses.
- **Prompt:** instructions and context supplied to the model.
- **Tool:** a callable function with a defined interface.
- **Agent:** logic that selects actions, often including tool calls.
- **Tracing:** records used to inspect execution.

## Recommended Workflow
1. Start with a normal function or fixed workflow.
2. Define tool inputs and outputs.
3. Test tools independently.
4. Connect the model to a limited tool list.
5. Add tool-call limits and error handling.
6. Test ambiguous and adversarial inputs.
7. Add tracing and evaluate before deployment.

```python
def get_order_status(order_id, orders):
    if not isinstance(order_id, str) or not order_id.strip():
        raise ValueError("order_id is required")
    return orders.get(order_id, "Order not found")
```
A framework adapter could expose this function as a tool. Keep business logic testable without a language model.

## Testing
Check tool selection, argument validity, missing information, error recovery, stopping behavior, and accuracy when summarizing tool results.

## Key Takeaways
- Frameworks connect components but do not guarantee correctness.
- Keep business logic independent and testable.
- Verify framework APIs against current documentation.

## Review Questions
1. What components can LangChain connect?
2. Why test tools independently?
3. Name three agent behaviors to test.
