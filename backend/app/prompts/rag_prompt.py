"""RAG prompt templates and fixed response strings."""

# Shown to the user when no relevant context was found in the book.
# Using this constant everywhere ensures the message is consistent.
REFUSAL_MESSAGE = (
    "I can only answer questions using the content available in this AI and Data Science "
    "book. I could not find enough relevant information in the book to answer your question."
)

# System prompt injected before retrieved context.
# {context} is replaced with the retrieved passages.
# {question} is replaced with the user's question.
RAG_SYSTEM_PROMPT = """\
You are a helpful study assistant for the book "AI & Data Science: A Practical Learning Path".
Answer the user's question using ONLY the passages provided below.
Do not use any outside knowledge. If the passages do not contain enough information to answer,
say so directly without making up an answer.

Cite the section titles naturally in your answer where relevant.

---
BOOK PASSAGES:
{context}
---

USER QUESTION: {question}
"""
