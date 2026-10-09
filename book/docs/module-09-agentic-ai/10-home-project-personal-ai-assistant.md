---
id: 10-home-project-personal-ai-assistant
title: Home Project: Personal AI Assistant with Tools
sidebar_position: 10
---

## Project Goal
Build a personal assistant that answers questions and calls a few safe tools, such as a calculator, sample task-list lookup, or read-only notes search.

## Scope
Start with two or three tools. Avoid account access, purchases, deleting files, or sending real messages in the first version. Use mock data for demos.

## Suggested Tools
- Calculator for arithmetic.
- Search within approved notes.
- Read-only task-list lookup.
- Draft creator that prepares a message without sending it.

## Development Steps
1. Write user stories and define forbidden actions.
2. Implement tools as independent functions.
3. Validate inputs and return structured errors.
4. Connect the model to the approved tool list.
5. Require confirmation for consequential actions.
6. Log tool names and outcomes without unnecessary private content.
7. Test ambiguous requests and failures.

## Acceptance Criteria
- Uses a tool when appropriate.
- Rejects invalid input safely.
- Does not claim success when a tool fails.
- Asks for missing required information.
- Never acts outside its permission list.
- Lets users inspect and clear saved task state.

## Optional Extensions
Add a simple interface, task history, or retrieval over approved notes. Keep each extension independently testable.

## Review Questions
1. Why start with read-only tools?
2. Which actions require confirmation?
3. What should the assistant say if a tool fails?
