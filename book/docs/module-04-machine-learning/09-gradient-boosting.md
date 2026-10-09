---
id: 09-gradient-boosting
title: Gradient Boosting — XGBoost and LightGBM
sidebar_position: 9
---

# Gradient Boosting — XGBoost and LightGBM

## What Is Boosting?
Boosting builds models sequentially. Later models focus on reducing errors made by earlier models.

```text
Model 1 → Errors → Model 2 → Errors → Model 3 → Final Ensemble
```

Gradient boosting commonly uses decision trees as weak learners and optimizes a loss function.

## XGBoost Example
```python
from xgboost import XGBClassifier

model = XGBClassifier(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=4,
    random_state=42
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

XGBoost and LightGBM are widely used for structured/tabular ML.

## Important Hyperparameters
- `learning_rate`: contribution of each stage.
- `n_estimators`: number of boosting stages.
- `max_depth`: tree complexity.
- Regularization parameters: control model complexity.

A smaller learning rate often requires more estimators. These choices should be validated rather than guessed.

## Overfitting
Boosting can overfit. Use validation, regularization, depth control, and early stopping where supported.

## Key Takeaways
Boosting improves a model through sequential error correction. XGBoost and LightGBM are powerful tools, but strong scores still require careful validation.

## Review Questions
1. What is boosting?
2. What does learning rate control?
3. Why can boosting overfit?
4. Name two gradient-boosting frameworks.


## Syllabus Focus

Sequential boosting, weak learners, learning rate, estimators, depth, regularization, XGBoost/LightGBM.
