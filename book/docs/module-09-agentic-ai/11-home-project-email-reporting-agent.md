---
id: 11-home-project-email-reporting-agent
title: Home Project: Automated Email and Reporting Agent
sidebar_position: 11
---

## Project Goal
Create a workflow that prepares a report and email draft from sample data. The initial version must not send email automatically.

## Workflow
1. Load a sample CSV or spreadsheet.
2. Validate expected columns.
3. Calculate weekly or monthly metrics.
4. Generate a chart and concise report.
5. Draft an email from the report.
6. Check recipients, figures, tone, and attachments.
7. Present the draft for human approval.

## Important Controls
- Use synthetic or approved data.
- Keep recipient addresses in configuration, not model-generated guesses.
- Compute metrics in code; do not let the model invent numbers.
- Validate attachments and file paths.
- Require explicit approval before sending.
- Record whether the draft was created, approved, or sent.
- Avoid silently repeating an action after a failure.

## Example Report Data
```python
report = {
    "period": "Week 1",
    "total_orders": 240,
    "revenue": 12500.00,
    "notes": ["Based on the provided sample dataset."]
}
```
These values are examples, not real business results.

## Test Cases
Empty data, missing columns, invalid dates, unconfigured recipient, mismatched report numbers, and unavailable sending service.

## Deliverables
Code, sample input, report, chart, email draft, validation checklist, tests, and README. Real provider integration should use minimum permissions and retain human approval.

## Review Questions
1. Why should business metrics be calculated in code?
2. What must be checked before sending?
3. How should a failed send be represented?
