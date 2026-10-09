---
id: 04-train-test-cross-validation
title: Train/Test Split and Cross Validation
sidebar_position: 4
---

# Train/Test Split and Cross Validation

## Generalization
A useful model performs well on new examples, not only on training observations.

## Train/Test Split
```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

Training data is used to learn. Test data estimates performance on unseen observations.

## Overfitting
Overfitting occurs when a model learns training-specific details and performs poorly on new data.

```text
Underfitting ← Good Generalization → Overfitting
```

## Cross-Validation
In 5-fold cross-validation, the training data is divided into five folds. Each fold takes a turn as validation data.

```python
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X_train, y_train, cv=5)
print(scores)
print(scores.mean())
```

Cross-validation gives several performance estimates instead of depending on one split.

## Stratified Classification Split
For classification, preserve class proportions when appropriate:
```python
train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
```

## Key Takeaways
- Generalization is the real goal.
- Test data should remain untouched until final evaluation.
- Cross-validation helps compare models more reliably.
- Overfitting is a central ML risk.

## Review Questions
1. What is generalization?
2. Why should test data remain separate?
3. What does 5-fold CV mean?
4. What is overfitting?


## Syllabus Focus

Generalization, train/test split, overfitting, cross-validation, stratification.
