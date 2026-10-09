---
id: 17-loan-eligibility-project
title: Class Project — Loan Eligibility Prediction
sidebar_position: 17
---

# Class Project — Loan Eligibility Prediction

## Goal
Predict whether an application belongs to an eligible/non-eligible class.

## Possible Features
Income, loan amount, loan term, credit history, employment status, dependents, and property information.

## Models
Compare:
- Logistic Regression
- Decision Tree
- Random Forest

## Evaluation
Report accuracy, precision, recall, F1-score, and a confusion matrix.

```python
from sklearn.metrics import classification_report, confusion_matrix
print(confusion_matrix(y_test, predictions))
print(classification_report(y_test, predictions))
```

## Questions
- Is the dataset imbalanced?
- Which errors matter most?
- Which model has the strongest recall?
- Which model best fits the project objective?

## Deliverables
Preprocessing pipeline, model comparison, confusion matrix, metrics discussion, and final recommendation.

A classroom model must not be treated as an automatic real-world lending decision.


## Syllabus Focus

Classification project using Logistic Regression, Decision Tree and Random Forest.
