---
id: 08-class-project-autonomous-data-analyst
title: Class Project: AI Autonomous Data Analyst
sidebar_position: 8
---

## Project Goal
Build a controlled agent workflow that inspects a dataset, calculates metrics, creates a chart, and writes an evidence-based summary.

## Requirements
- Use a small, non-sensitive CSV dataset.
- Validate columns, types, and missing values.
- Provide limited analysis tools with explicit inputs.
- Produce a report and at least one chart.
- Document limitations and data quality.
- Do not permit arbitrary code execution or unrestricted file access.

## Suggested Architecture
1. **Planner:** creates a short analysis plan.
2. **Data tool:** loads only the selected dataset.
3. **Analysis tools:** compute aggregates using tested functions.
4. **Visualization tool:** creates charts from validated data.
5. **Report writer:** summarizes evidence.
6. **Validator:** checks calculations and unsupported claims.

Implement a fixed Python workflow first. Add model-driven tool selection only after the baseline works.

## Suggested Folder Structure
```text
autonomous-data-analyst/
├── data/
├── src/
│   ├── load_data.py
│   ├── analysis_tools.py
│   ├── charts.py
│   ├── report.py
│   └── app.py
├── tests/
├── outputs/
└── README.md
```

## Milestones
1. Choose a dataset and document its columns.
2. Build deterministic analysis functions.
3. Add chart generation.
4. Connect a model to approved tools.
5. Add output validation and tool-call limits.
6. Test missing or invalid columns.
7. Prepare a demo and report.

## Evaluation Rubric
- Calculation and data validation: 30%
- Tool design and safe limits: 20%
- Charts and report: 20%
- Tests and error handling: 20%
- Documentation and demo: 10%

## Deliverables
Code, dataset or instructions, report, charts, tests, README, and limitations.

## Review Questions
1. Which parts should remain deterministic functions?
2. How will you verify that the report is evidence-based?
3. What should happen when a required column is missing?
