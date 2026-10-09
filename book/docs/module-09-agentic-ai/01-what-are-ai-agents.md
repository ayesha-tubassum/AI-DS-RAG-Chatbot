---
id: 01-what-are-ai-agents
title: What Are AI Agents?
sidebar_position: 1
---

## Learning Objectives
Define an AI agent, identify its main components, and distinguish an agent from a simple chatbot.

## What Is an AI Agent?
An **AI agent** is a software system that observes a task or environment, selects actions, and works toward a goal. It may use a language model for decisions, tools to perform actions, and memory to retain useful context.

A basic chatbot mainly responds to messages. An agent can break a task into steps, call approved tools, inspect results, and continue until it completes the task or reaches a stopping condition.

## Common Components
- **Goal:** the result the user wants.
- **Model:** helps interpret the request and select next steps.
- **Tools:** functions or services the agent can call.
- **State/context:** information needed during the current task.
- **Memory:** selected information retained for future use.
- **Guardrails:** rules and permissions that limit behavior.
- **Evaluator:** checks whether the output meets requirements.

## Example
A data-analysis agent might load an approved CSV, calculate sales changes, create a chart, and draft a report. It should support its conclusions with calculated results rather than inventing explanations.

## A Simple Agent Loop
1. Understand the goal.
2. Choose a next action.
3. Validate and execute the action.
4. Inspect the result.
5. Continue, ask a clarifying question, or stop.
6. Return findings and limitations.

## When to Use Agents
Agents can help with multi-step tasks requiring decisions and tools. For predictable transformations, a normal function or fixed workflow is often simpler, cheaper, and easier to test.

## Key Takeaways
- Agents combine goal-directed decisions with actions.
- Tool access adds capability and risk.
- Reliable agents need permissions, checks, and stopping rules.

## Review Questions
1. What is an AI agent?
2. Name four common components.
3. How is an agent different from a simple chatbot?
4. When might a normal function be a better choice?
