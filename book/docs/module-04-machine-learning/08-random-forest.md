---
id: 08-random-forest
title: Random Forest
sidebar_position: 8
---

# Random Forest

## Ensemble Learning
An ensemble combines multiple models.

Random Forest builds many decision trees and combines their predictions.

```text
Data → Tree 1 ┐
      → Tree 2 ├→ Combined Prediction
      → Tree 3 ┤
      → Tree N ┘
```

For classification, trees vote; for regression, predictions can be averaged.

## Training
```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=200, random_state=42
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

Important parameters:
- `n_estimators`
- `max_depth`
- `min_samples_leaf`
- `max_features`

## Feature Importance
```python
importance = model.feature_importances_
```
These are model-based importance estimates, not proof of causality.

## Advantages
Random Forest often provides a strong baseline for tabular data and can capture nonlinear patterns without requiring feature scaling.

## Key Takeaways
Random Forest reduces dependence on one tree by combining many randomized trees.

## Review Questions
1. What is ensemble learning?
2. What does n_estimators control?
3. How does Random Forest differ from one tree?
4. Why should feature importance be interpreted carefully?


## Syllabus Focus

Ensemble learning, multiple trees, voting/averaging, hyperparameters, feature importance.
