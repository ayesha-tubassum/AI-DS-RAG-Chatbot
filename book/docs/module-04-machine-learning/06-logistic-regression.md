---
id: 06-logistic-regression
title: Logistic Regression
sidebar_position: 6
---

# Logistic Regression

## Classification
Classification predicts categories such as spam/not spam, fraud/not fraud, or churn/stay.

## Core Idea
Logistic Regression converts a linear score into a probability and then uses a decision threshold to produce a class.

```text
Features → Linear Score → Probability → Class
```

## Training
```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test)
```

## Metrics
Accuracy = correct predictions / total predictions.

Precision asks: among predicted positives, how many are truly positive?

Recall asks: among actual positives, how many were found?

F1 combines precision and recall.

```python
from sklearn.metrics import classification_report
print(classification_report(y_test, predictions))
```

## Why Accuracy Can Mislead
If fraud is 1% of transactions, predicting every transaction as legitimate gives high accuracy but detects no fraud.

Choose metrics according to the real cost of errors.

## Key Takeaways
Logistic Regression is a strong, interpretable classification baseline. Probability thresholds and class imbalance can change how performance should be evaluated.

## Review Questions
1. What is classification?
2. Why is Logistic Regression used for classification?
3. Define precision and recall.
4. Why can accuracy be misleading?


## Syllabus Focus

Binary classification, probabilities, thresholds, accuracy, precision, recall, F1.
