---
id: 01-ml-pipeline
title: Machine Learning Pipeline
sidebar_position: 1
---

# Machine Learning Pipeline

## Learning Objectives
By the end of this chapter you can:
- Explain what machine learning is.
- Describe an end-to-end ML workflow.
- Distinguish training, validation, testing, and deployment.
- Identify why data quality and evaluation matter.

## 1. What Is Machine Learning?
Machine learning learns patterns from data and uses those patterns to make predictions or decisions.

Traditional programming:
`Rules + Data → Output`

Machine learning:
`Data + Examples → Learned Model → Prediction`

Examples include house-price prediction, spam detection, fraud detection, and customer churn.

## 2. End-to-End Workflow
```text
Problem Definition
      ↓
Data Collection
      ↓
Data Understanding
      ↓
Cleaning
      ↓
Feature Engineering
      ↓
Preprocessing
      ↓
Train/Test Split
      ↓
Model Training
      ↓
Validation & Evaluation
      ↓
Model Selection
      ↓
Deployment
      ↓
Monitoring
```

## 3. Define the Problem
Before coding, identify:
- What is the target?
- Is the task regression, classification, or clustering?
- What information is available at prediction time?
- Which metric represents success?

A technically accurate model can still be useless if the problem is poorly defined.

## 4. Inspect Data
```python
import pandas as pd

df = pd.read_csv("data.csv")
print(df.head())
print(df.shape)
print(df.info())
print(df.isna().sum())
print(df.describe())
```

## 5. Train and Evaluate
```python
from sklearn.model_selection import train_test_split

X = df.drop(columns=["target"])
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
```

Train only on training data. Keep test data unseen until final evaluation.

## 6. Deployment
A production workflow may look like:
`User Request → API → Preprocessing → Model → Prediction → Response`

Deployment and monitoring are covered later in the MLOps module.

## Key Takeaways
- ML projects are workflows, not just algorithms.
- Data preparation strongly affects results.
- Evaluation must represent unseen data.
- Business objectives should guide model selection.

## Review Questions
1. What is an ML pipeline?
2. Why must test data remain unseen?
3. What is the difference between a model and an ML system?
4. Why define the problem before choosing an algorithm?


## Syllabus Focus

ML pipeline, problem definition, data collection, cleaning, feature engineering, preprocessing, training, evaluation, deployment.
