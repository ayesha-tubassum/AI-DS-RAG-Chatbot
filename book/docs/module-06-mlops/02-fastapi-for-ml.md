---
id: 02-fastapi-for-ml
title: FastAPI for ML Deployment
sidebar_position: 2
---

# FastAPI for ML Deployment

## 1. What Is FastAPI?

FastAPI is a Python web framework used to build APIs. For machine learning, it can provide an endpoint that accepts feature values and returns a prediction.

```text
Client → HTTP Request → FastAPI → Model → Prediction → HTTP Response
```

## 2. Install

```bash
pip install fastapi uvicorn scikit-learn joblib
```

## 3. A Simple Prediction API

```python
from fastapi import FastAPI
from pydantic import BaseModel
import joblib

app = FastAPI(title="ML Prediction API")

model = joblib.load("model.joblib")

class InputData(BaseModel):
    feature_1: float
    feature_2: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict")
def predict(data: InputData):
    prediction = model.predict([[data.feature_1, data.feature_2]])
    return {"prediction": prediction.tolist()}
```

Run it:

```bash
uvicorn main:app --reload
```

Then open the interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

## 4. Request Validation

Pydantic models make the expected input explicit:

```python
class CustomerInput(BaseModel):
    age: int
    income: float
    tenure: int
```

This is safer than accepting an unstructured dictionary.

## 5. Production Considerations

A production API should also consider:

- Authentication and authorization
- Input validation
- Timeouts
- Error handling
- Logging
- Model versioning
- Rate limiting
- Resource limits

Do not expose sensitive training data or secrets in API responses.

## Exercise

Create a `/predict` endpoint for a model you trained in Module 04 or Module 05. Add `/health` and document the input schema.
