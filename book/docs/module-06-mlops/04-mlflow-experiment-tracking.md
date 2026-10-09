---
id: 04-mlflow-experiment-tracking
title: MLflow for Tracking
sidebar_position: 4
---

# MLflow for Tracking

## 1. Why Experiment Tracking?

Machine learning projects often involve many experiments:

- Different algorithms
- Different hyperparameters
- Different datasets
- Different preprocessing choices

Without tracking, it becomes difficult to know which experiment produced which model.

## 2. What MLflow Provides

MLflow can help track:

- Parameters
- Metrics
- Model artifacts
- Experiment runs
- Model versions and lifecycle information

## 3. Installation

```bash
pip install mlflow
```

## 4. Basic Tracking Example

```python
import mlflow
from sklearn.metrics import accuracy_score

with mlflow.start_run():
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    mlflow.log_param("model_type", "RandomForest")
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("accuracy", accuracy)
```

The exact MLflow setup can vary by version and deployment environment.

## 5. What Should Be Logged?

At minimum, consider:

```text
Dataset/version
↓
Preprocessing choices
↓
Model type
↓
Hyperparameters
↓
Evaluation metrics
↓
Model artifact
```

## 6. Why This Matters

Suppose Experiment A has accuracy 0.91 and Experiment B has accuracy 0.94. Tracking lets the team inspect how B was produced and reproduce it.

## Exercise

Train two versions of the same classifier with different hyperparameters. Log the parameters and evaluation metrics for both runs and compare them.
