---
id: 03-reasoning-and-planning
title: Reasoning and Planning
sidebar_position: 3
---

## Learning Objectives
Break a broad task into subtasks and define completion conditions.

## Why Planning Matters
Complex tasks have dependencies. A report should not be written until the data is loaded and analyzed. Planning makes the order of work explicit.

## Example Plan
For “analyze sales and prepare a summary”:
1. Confirm the period and sales definition.
2. Load and validate the data.
3. Calculate key metrics.
4. Compare periods or categories.
5. Create supporting visualizations.
6. Draft conclusions with evidence.
7. Check the report against the request.

```python
plan = [
    "validate_input", "load_data", "calculate_metrics",
    "create_chart", "write_summary", "verify_output"
]
for step in plan:
    print("Next step:", step)
```
This is a fixed plan, not AI reasoning by itself. Fixed plans are useful when the workflow is known.

## Fixed vs. Dynamic Planning
A fixed workflow follows predefined steps. A dynamic agent may choose later steps based on earlier results. Dynamic planning is flexible, but requires limits on retries, execution time, tool calls, and cost.

## Stop Conditions
Define completion before execution. Examples include all required outputs being present, validation passing, a maximum step count being reached, required input being missing, or an unrecoverable tool error.

## Key Takeaways
- Plans need ordered steps and measurable completion criteria.
- Dynamic planning needs budgets and stop conditions.
- Verify the output instead of assuming the plan succeeded.

## Review Questions
1. Why split a task into subtasks?
2. Give one advantage of a fixed workflow.
3. List three stop conditions.
