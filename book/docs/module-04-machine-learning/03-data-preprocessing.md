---
id: 03-data-preprocessing
title: Data Preprocessing
sidebar_position: 3
---

# Data Preprocessing

## Why Preprocessing?
Real datasets may contain missing values, categories, inconsistent scales, duplicates, and incorrect types. Preprocessing makes data suitable for algorithms.

## 1. Missing Values
Inspect:
```python
print(df.isna().sum())
```

Numerical example:
```python
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy="median")
```

Categorical example:
```python
cat_imputer = SimpleImputer(strategy="most_frequent")
```

The correct strategy depends on the dataset.

## 2. Encoding
```python
from sklearn.preprocessing import OneHotEncoder
encoder = OneHotEncoder(handle_unknown="ignore")
```

## 3. Scaling
```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
```
Scaling is especially important for distance- and margin-based methods such as KNN and SVM.

## 4. ColumnTransformer
Different columns often require different treatment:
```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), numerical_columns),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_columns)
])
```

## 5. Pipelines
```python
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

pipeline = Pipeline([
    ("preprocessing", preprocessor),
    ("model", LogisticRegression(max_iter=1000))
])
pipeline.fit(X_train, y_train)
```

A pipeline keeps transformations consistent and helps prevent accidental leakage.

## Key Takeaways
Preprocessing is part of the model workflow. Fit transformations using training data and apply the learned transformations to validation/test data.

## Review Questions
1. Why are missing values a problem?
2. Why is scaling important for KNN?
3. What does ColumnTransformer do?
4. How does a pipeline reduce preprocessing mistakes?


## Syllabus Focus

Missing values, encoding categorical variables, scaling, ColumnTransformer, pipelines, leakage prevention.
