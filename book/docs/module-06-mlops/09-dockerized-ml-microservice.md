---
id: 09-dockerized-ml-microservice
title: Home Project — Dockerized ML Microservice
sidebar_position: 9
---

# Home Project — Dockerized ML Microservice

## Goal

Package an ML prediction service as a Docker container.

## Requirements

- A trained model
- FastAPI prediction endpoint
- `requirements.txt`
- `Dockerfile`
- `/health` endpoint
- `/predict` endpoint
- Container build instructions
- Container run instructions

## Suggested Architecture

```text
Client
  ↓
Dockerized FastAPI
  ↓
Preprocessing
  ↓
ML Model
  ↓
Prediction
```

## Stretch Goals

- Add automated tests.
- Add structured logging.
- Add a non-root container user.
- Add a Docker health check.
- Add API versioning such as `/v1/predict`.

## Deliverables

Submit the project repository, Dockerfile, README, and evidence that the container runs successfully.
