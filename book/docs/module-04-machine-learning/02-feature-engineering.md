---
id: 02-feature-engineering
title: Feature Engineering
sidebar_position: 2
---

# Feature Engineering

## Learning Objectives
Learn how to create useful inputs, transform variables, select relevant features, and avoid leakage.

## 1. Features and Target
Features are model inputs (`X`). The target is what the model learns to predict (`y`).

For house prices:
`area, bedrooms, bathrooms, age → price`

## 2. Creating Features
A raw dataset may contain `total_rooms` and `total_bedrooms`. A useful derived feature can be:
```python
df["bedrooms_per_room"] = df["total_bedrooms"] / df["total_rooms"]
```

Other examples:
- `total_spend / number_of_orders`
- `loan / income`
- `revenue - cost`
- day/month/year extracted from dates

## 3. Numerical Transformations
Variables may have very different scales. Standardization is common:
```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

For heavily skewed positive variables, a log transformation may sometimes be useful.

## 4. Categorical Features
Text categories need numerical representation. One-hot encoding is common:
```python
from sklearn.preprocessing import OneHotEncoder
encoder = OneHotEncoder(handle_unknown="ignore")
```

## 5. Feature Selection
Irrelevant features can add noise, computation, and overfitting risk. Use domain knowledge and validation rather than blindly keeping every column.

## 6. Data Leakage
A feature must only use information available at prediction time.

Example of leakage: using a customer's future payment status to predict whether they will default.

Leakage often produces excellent validation scores and poor real-world performance.

## Key Takeaways
- Good features can make simple models powerful.
- Derived features should represent meaningful information.
- Encoding and scaling are common transformations.
- Never use future information to construct prediction features.

## Review Questions
1. What is a feature?
2. Give two examples of derived features.
3. Why do categorical values need encoding?
4. What is data leakage?


## Syllabus Focus

Creating, transforming, selecting features; numerical transformations, categorical variables, derived features, leakage.
