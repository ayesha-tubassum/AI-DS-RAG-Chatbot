---
id: 05-crewai-and-autogen
title: CrewAI and AutoGen: Multi-Agent Frameworks
sidebar_position: 5
---

## Learning Objectives
Describe multi-agent orchestration and decide when separate agent roles are useful.

## Multi-Agent Orchestration
A multi-agent system coordinates two or more roles. Frameworks such as CrewAI and Microsoft AutoGen provide ways to coordinate agent interactions; exact capabilities and APIs depend on version.

## Example Roles
For a research report:
- **Researcher:** gathers information from approved sources.
- **Analyst:** compares evidence.
- **Writer:** drafts from findings.
- **Reviewer:** checks claims, citations, and completeness.

Role descriptions alone are not security boundaries. The application must enforce tool permissions.

## Workflow
1. Define the overall goal and deliverables.
2. Specify each role's responsibility and tools.
3. Define handoff formats and ordering.
4. Set maximum interactions.
5. Validate each handoff.
6. Review the final result.

## When Multiple Agents Help
Use multiple roles when work is separable or benefits from independent review. Extra agents can increase cost, latency, coordination complexity, and inconsistency, so compare against a simpler baseline.

## Evaluation
Measure factual accuracy, task completion, time, cost, and human corrections.

## Key Takeaways
- Each role needs a clear responsibility.
- Use structured handoffs and bounded interactions.
- Multi-agent complexity should be justified by measurable improvement.

## Review Questions
1. Name four possible roles in a report system.
2. Why are role prompts not enough for security?
3. What metrics can compare single-agent and multi-agent approaches?
