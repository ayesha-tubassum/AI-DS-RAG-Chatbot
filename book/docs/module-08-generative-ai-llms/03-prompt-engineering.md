---
id: 03-prompt-engineering
title: Prompt Engineering
sidebar_position: 3
---

# Prompt Engineering

## Learning Goal

Craft effective prompts to guide LLM responses.

## 1. What Is a Prompt?

A prompt is the input or instruction supplied to a language model.

A useful prompt usually specifies:

- Task
- Context
- Constraints
- Desired format
- Examples, when useful

## 2. Weak vs Structured Prompt

Weak:

```text
Explain machine learning.
```

More structured:

```text
Explain machine learning to a beginner.

Requirements:
- Use simple language.
- Give one real-world example.
- Explain supervised and unsupervised learning.
- End with three review questions.
```

The second prompt communicates the expected output more clearly.

## 3. Common Prompt Patterns

### Role / Context

```text
You are a Python instructor teaching beginners.
```

### Few-Shot Examples

Provide examples of desired input/output behavior.

### Structured Output

Ask for a specific format such as:

```text
Return:
1. Definition
2. Example
3. Advantages
4. Limitations
```

## 4. Prompt Iteration

Prompt engineering is iterative:

```text
Draft Prompt
   ↓
Test
   ↓
Inspect Output
   ↓
Improve Instructions
   ↓
Test Again
```

## 5. Important Limitation

A better prompt can improve task performance, but prompting does not guarantee factual accuracy. Outputs should be evaluated.

## Exercise

Create prompts for:
1. Summarization
2. Classification
3. Data extraction
4. Educational tutoring
5. Report generation
