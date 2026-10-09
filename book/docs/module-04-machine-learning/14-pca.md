---
id: 14-pca
title: Principal Component Analysis (PCA)
sidebar_position: 14
---

# Principal Component Analysis (PCA)

## Why Reduce Dimensions?
Datasets may contain many features. High dimensionality can make visualization, computation, and pattern discovery harder.

PCA creates new variables called principal components.

```text
Original Features → PCA → Principal Components → Reduced Data
```

## Core Idea
The first principal component captures as much variation as possible. Subsequent components capture remaining variation subject to the mathematical constraints of PCA.

## Example
```python
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

X_scaled = StandardScaler().fit_transform(X)

pca = PCA(n_components=2)
X_reduced = pca.fit_transform(X_scaled)

print(pca.explained_variance_ratio_)
```

## Explained Variance
The explained variance ratio tells how much variation each component represents.

If PC1 explains 45% and PC2 25%, the first two components explain 70% in this illustrative example.

## PCA and Scaling
PCA is sensitive to feature scale, so standardization is commonly considered before applying it.

## Limitation
Principal components are combinations of original features and may be less interpretable than the original variables.

## Review Questions
1. Why use dimensionality reduction?
2. What is a principal component?
3. What does explained variance mean?
4. Why is scaling commonly used before PCA?


## Syllabus Focus

Dimensionality reduction, principal components, explained variance, scaling, visualization.
