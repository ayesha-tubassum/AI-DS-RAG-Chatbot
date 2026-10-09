---
id: 16-customer-segmentation-project
title: Class Project — Customer Segmentation (K-Means)
sidebar_position: 16
---

# Class Project — Customer Segmentation (K-Means)

## Goal
Group customers into meaningful segments using purchasing behavior.

## Features
Try total spending, purchase count, average order value, and recency.

## Workflow
```text
Clean → Select Features → Scale → Test K → Fit K-Means
→ Summarize Clusters → Visualize → Interpret
```

## Starter Code
```python
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

features = df[["total_spending", "purchase_count", "recency"]]
X_scaled = StandardScaler().fit_transform(features)

model = KMeans(n_clusters=4, random_state=42, n_init="auto")
df["cluster"] = model.fit_predict(X_scaled)
```

For every cluster calculate size, average spending, purchases, and recency. Then describe each segment from evidence.

## Deliverables
Notebook, cluster summary, K-selection analysis, visualization, and business recommendations.


## Syllabus Focus

Unsupervised segmentation using purchasing behavior.
