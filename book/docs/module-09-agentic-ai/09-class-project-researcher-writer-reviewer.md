---
id: 09-class-project-researcher-writer-reviewer
title: Class Project: Researcher + Writer + Reviewer
sidebar_position: 9
---

## Project Goal
Create a multi-agent workflow in which a researcher gathers evidence, a writer drafts a response, and a reviewer checks it.

## Roles
**Researcher:** uses approved sources, returns claims with references, and marks uncertainty.
**Writer:** drafts from the evidence, avoids invented citations, and separates evidence from interpretation.
**Reviewer:** checks support for factual claims, flags contradictions, and returns structured issues.

## Workflow
1. User provides question and scope.
2. Researcher returns a structured evidence record.
3. Writer drafts from the record.
4. Reviewer checks the draft against a checklist.
5. Allow a limited number of revisions.
6. Validate citations and required sections.

```python
def run_workflow(question, research_tool, writer, reviewer):
    evidence = research_tool(question)
    draft = writer(question, evidence)
    review = reviewer(question, evidence, draft)
    if review["approved"]:
        return {"draft": draft, "review": review}
    return {"draft": draft, "review": review,
            "status": "needs_human_revision"}
```
The functions must be implemented and tested before use.

## Test Cases
- Sources do not answer the question.
- Sources contradict each other.
- Writer adds a claim absent from the evidence.
- Citation points to the wrong source.
- Reviewer returns an invalid format.

## Quality and Safety
Treat documents as untrusted input. Do not follow instructions embedded in source documents unless authorized by the actual task. Require qualified human review for high-impact decisions.

## Deliverables
Role prompts, tools, workflow code, tests, sample output, review checklist, and README.

## Review Questions
1. What should the researcher provide to the writer?
2. What should the reviewer check?
3. Why limit revision cycles?
