---
id: 13-hierarchical-clustering
title: Hierarchical Clustering
sidebar_position: 13
---

# Hierarchical Clustering

## Core Idea
Hierarchical clustering builds nested groups.

Agglomerative clustering starts with every observation as its own cluster and repeatedly merges groups.

```text
Individual Points
      ↓
Small Groups
      ↓
Larger Groups
      ↓
Hierarchy
```

## Dendrogram
A dendrogram visualizes the sequence of merges. A cut through the hierarchy can produce a chosen number of clusters.

## Scikit-Learn
```python
from sklearn.cluster import AgglomerativeClustering

model = AgglomerativeClustering(n_clusters=3)
labels = model.fit_predict(X)
```

## K-Means vs Hierarchical
| K-Means | Hierarchical |
|---|---|
| Uses centroids | Builds nested groups |
| Requires K during fitting | Provides a hierarchy |
| Often efficient for large datasets | Can be more computationally expensive |

## Key Takeaways
Hierarchical clustering is useful when understanding relationships at multiple grouping levels is important.

## Review Questions
1. What is agglomerative clustering?
2. What does a dendrogram show?
3. Give one difference from K-Means.


## Syllabus Focus

Agglomerative clustering, hierarchy, dendrograms, comparison with K-Means.
