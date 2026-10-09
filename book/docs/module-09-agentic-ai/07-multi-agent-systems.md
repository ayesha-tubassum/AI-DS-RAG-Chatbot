---
id: 07-multi-agent-systems
title: Multi-Agent Systems
sidebar_position: 7
---

## Learning Objectives
Design a collaborative workflow and reduce coordination risks.

## Common Patterns
- **Sequential:** one role passes its result to the next.
- **Parallel:** independent roles work on separate subtasks.
- **Supervisor:** a coordinator assigns work and checks results.
- **Review:** agents propose and critique solutions, followed by validation.

More agents do not automatically produce better results.

## Researcher–Writer–Reviewer Example
1. Researcher returns claims, source references, and uncertainty.
2. Writer drafts from the supplied evidence.
3. Reviewer flags unsupported claims and missing requirements.
4. Coordinator requests a limited revision if needed.
5. Final validation checks the deliverable.

## Structured Handoffs
Use schemas instead of vague messages:
```python
research_result = {
    "question": "Which category had the largest decline?",
    "findings": [
        {"claim": "Category A declined 12%",
         "evidence": "sales.csv, rows 20-45"}
    ],
    "limitations": ["Only two months were available"],
}
```
The values are illustrative. Real claims must be calculated from actual data.

## Coordination Risks
Agents may repeat work, contradict each other, spread errors through handoffs, or loop without improvement. Use step limits, schema validation, independent checks, and human review for consequential outputs. Treat source documents as untrusted input.

## Key Takeaways
- Define communication contracts for roles.
- Verify evidence at each handoff.
- Bound retries and compare with a simpler baseline.

## Review Questions
1. Explain sequential and parallel patterns.
2. What should a structured handoff contain?
3. How can errors spread through a multi-agent workflow?
