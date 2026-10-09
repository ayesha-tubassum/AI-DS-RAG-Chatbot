---
id: 06-memory-enabled-agents
title: Memory-Enabled Agents
sidebar_position: 6
---

## Learning Objectives
Distinguish short-term context from persistent memory and design a privacy-aware memory policy.

## Types of Memory
- **Conversation context:** messages available in the current interaction.
- **Working state:** temporary variables and intermediate results.
- **Persistent memory:** selected information retained across sessions.
- **External knowledge store:** documents retrieved when needed.

## What Should Be Stored?
Store information only when useful, appropriate, and permitted. Prefer concise, structured facts over complete transcripts. Avoid storing secrets or sensitive personal information without a clear, authorized need and safeguards.

```python
memory = {
    "preferred_report_format": "summary with a table",
    "default_currency": "USD",
}
def recall(key, default=None):
    return memory.get(key, default)
```
This example keeps data only in program memory; it does not persist across restarts.

## Memory Lifecycle
Define what may be stored, how information is confirmed and updated, when it expires, how users can inspect or delete it, and who can access it.

## Memory vs. RAG
Memory often retains user- or task-specific state. Retrieval-augmented generation (RAG) retrieves relevant content from a knowledge collection. They can be combined but should have separate access and deletion rules.

## Key Takeaways
- Memory helps only when information is relevant and reliable.
- Apply data minimization, access controls, and deletion policies.
- Separate personal memory from document retrieval.

## Review Questions
1. How does working state differ from persistent memory?
2. Name three memory lifecycle policies.
3. How does memory differ from RAG?
