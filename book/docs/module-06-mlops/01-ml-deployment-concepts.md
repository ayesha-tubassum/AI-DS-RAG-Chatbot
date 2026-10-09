---
id: 01-ml-deployment-concepts
title: ML Deployment Concepts
sidebar_position: 1
---

# ML Deployment Concepts

## 1. What Is ML Deployment?

Machine learning development does not end when a model gets a good score in a notebook. **Deployment** means making the trained model available in an environment where an application or user can send data and receive predictions.

A simple flow is:

```text
Training Data
    ↓
Data Preparation
    ↓
Model Training
    ↓
Model Evaluation
    ↓
Save Model
    ↓
Deploy Model
    ↓
Prediction Requests
    ↓
Monitoring & Improvement
```

## 2. Why Production Is Different

A notebook can run on your computer because all dependencies, files, and variables are available locally. A production service must be repeatable, reliable, and accessible.

Typical concerns include:

- How will the model receive input?
- How will predictions be returned?
- Which Python and package versions are required?
- Where will the model file live?
- How will errors be recorded?
- How will the service be monitored?
- How can a new model version be released safely?

## 3. Batch vs Real-Time Prediction

### Batch Prediction

Predictions are generated for many records at scheduled intervals.

Examples:

- Daily customer churn predictions
- Weekly sales scoring
- Monthly risk reports

### Real-Time Prediction

A client sends a request and expects a prediction immediately.

Examples:

- Fraud screening during checkout
- Loan application scoring
- Image classification API

## 4. Saving a Model

With scikit-learn, `joblib` is commonly used for model persistence:

```python
import joblib

joblib.dump(model, "model.joblib")
loaded_model = joblib.load("model.joblib")
```

Always make sure the preprocessing steps used during training are also available during inference.

## 5. Deployment Checklist

Before deployment, verify:

- Input schema is defined.
- Preprocessing is reproducible.
- Model artifact can be loaded.
- Prediction output is documented.
- Errors are handled.
- Logs are available.
- Dependencies are pinned.
- A health check exists.
- Monitoring requirements are identified.

## Key Takeaway

Deployment turns a trained model into a usable software service. MLOps adds the processes needed to keep that service reliable throughout its lifecycle.
