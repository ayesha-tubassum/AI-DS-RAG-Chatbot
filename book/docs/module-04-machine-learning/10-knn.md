---
id: 10-knn
title: K-Nearest Neighbors (KNN)
sidebar_position: 10
---

# K-Nearest Neighbors (KNN)

## Core Idea
KNN predicts a new observation using nearby training observations.

```text
New Point → Find K Nearest → Vote/Average → Prediction
```

For classification, neighbors vote on the class. For regression, their target values can be combined.

## Training
```python
from sklearn.neighbors import KNeighborsClassifier

model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

## Why Scaling Matters
Suppose one feature ranges from 0–1 and another from 0–100,000. Distance can be dominated by the large-scale variable.

Use StandardScaler or another appropriate scaling method.

## Choosing K
Small K can be sensitive to noise. Large K produces smoother predictions and can miss local structure. Use validation to select K.

## Strengths
- Simple concept.
- Useful for nonlinear boundaries.
- Minimal assumptions about functional form.

## Limitations
- Prediction can be expensive for large datasets.
- Sensitive to scaling and irrelevant features.
- Performance depends on K and distance metric.

## Review Questions
1. How does KNN predict?
2. Why is scaling important?
3. What can happen with very small K?
4. What can happen with very large K?


## Syllabus Focus

Instance-based learning, distance, K selection, scaling, strengths and limitations.
