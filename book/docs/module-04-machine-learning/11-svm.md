---
id: 11-svm
title: Support Vector Machine (SVM)
sidebar_position: 11
---

# Support Vector Machine (SVM)

## Core Idea
SVM seeks a decision boundary that separates classes while maximizing the margin between them.

The observations closest to the boundary are support vectors.

## Nonlinear Classification
Kernels can create nonlinear decision boundaries. Common choices include:
- Linear
- Polynomial
- RBF

## Example
```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

model = make_pipeline(
    StandardScaler(),
    SVC(kernel="rbf")
)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

## Why Scaling?
SVM optimization is sensitive to feature magnitudes, so scaling is commonly used.

## Strengths
- Effective for some high-dimensional problems.
- Can model nonlinear boundaries with kernels.

## Limitations
- Parameter tuning can be important.
- Training can become expensive on large datasets.
- Feature scaling is often necessary.

## Review Questions
1. What is the margin?
2. What are support vectors?
3. What is a kernel?
4. Why is scaling commonly used with SVM?


## Syllabus Focus

Margins, support vectors, kernels, scaling, SVC.
