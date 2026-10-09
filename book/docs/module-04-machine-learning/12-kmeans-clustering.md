---
id: 12-kmeans-clustering
title: K-Means Clustering
sidebar_position: 12
---

# K-Means Clustering

## Unsupervised Learning
Unsupervised learning discovers structure without a supplied target label.

Examples include customer segmentation and grouping similar documents.

## K-Means Algorithm
```text
Choose K
  ↓
Initialize centroids
  ↓
Assign points to nearest centroid
  ↓
Update centroids
  ↓
Repeat
```

## Example
```python
from sklearn.cluster import KMeans

model = KMeans(
    n_clusters=4,
    random_state=42,
    n_init="auto"
)
labels = model.fit_predict(X)
```

## Choosing K
Try several K values and inspect clustering quality and business interpretability. The elbow method is one common diagnostic.

Do not automatically choose the largest K: clusters should be useful and understandable.

## Customer Segmentation
Useful features may include spending, purchase count, average order value, and recency.

After clustering, calculate summary statistics for each cluster before giving the segments business names.

## Review Questions
1. What is unsupervised learning?
2. What does K represent?
3. What is a centroid?
4. Why should clusters be interpreted after creation?


## Syllabus Focus

Unsupervised learning, centroids, K selection, elbow method, customer segmentation.
