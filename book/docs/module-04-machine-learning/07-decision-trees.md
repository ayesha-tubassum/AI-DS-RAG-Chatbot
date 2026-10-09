---
id: 07-decision-trees
title: Decision Trees
sidebar_position: 7
---

# Decision Trees

## Core Idea
A decision tree repeatedly asks feature-based questions.

```text
Income > 50000?
├── Yes → Loan > 20000?
│        ├── Yes → Review
│        └── No  → Eligible
└── No  → Not Eligible
```

Trees can solve classification and regression.

## Training
```python
from sklearn.tree import DecisionTreeClassifier

model = DecisionTreeClassifier(
    max_depth=5, random_state=42
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

## Controlling Complexity
Useful parameters include:
- `max_depth`
- `min_samples_split`
- `min_samples_leaf`

Very deep trees can memorize training data and overfit.

## Advantages
- Captures nonlinear relationships.
- Easy to visualize conceptually.
- Useful for both classification and regression.

## Limitation
A single tree can be unstable: small changes in data may change its structure significantly.

## Key Takeaways
Trees create predictions through sequential splits. Controlling depth and leaf sizes can improve generalization.

## Review Questions
1. How does a tree make decisions?
2. What does max_depth control?
3. Why can deep trees overfit?
4. Can trees perform regression?


## Syllabus Focus

Tree-based classification and regression, splits, depth, overfitting, hyperparameters.
