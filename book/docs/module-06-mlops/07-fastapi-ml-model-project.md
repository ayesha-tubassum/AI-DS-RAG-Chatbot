---
id: 07-fastapi-ml-model-project
title: Class Project — Build and Deploy an ML Model with FastAPI
sidebar_position: 7
---

# Class Project — Build and Deploy an ML Model with FastAPI

## Goal

Create an API that serves predictions from a trained machine learning model.

## Requirements

1. Select a classification or regression model from previous modules.
2. Save the trained model.
3. Create a FastAPI application.
4. Add a `/health` endpoint.
5. Add a `/predict` endpoint.
6. Validate request data.
7. Return a clear prediction response.
8. Add basic error handling.
9. Test the API using the interactive documentation.
10. Write a README explaining how to run the service.

## Suggested Structure

```text
ml-api/
├── main.py
├── model.joblib
├── requirements.txt
├── README.md
└── tests/
    └── test_api.py
```

## Deliverables

- Source code
- Model artifact or reproducible training script
- Requirements file
- API screenshots
- Test results
- README

## Success Criteria

The service should start successfully, validate input, load the model, and return a prediction without exposing sensitive information.
