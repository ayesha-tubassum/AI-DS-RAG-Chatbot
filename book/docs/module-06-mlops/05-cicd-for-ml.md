---
id: 05-cicd-for-ml
title: CI/CD Introduction
sidebar_position: 5
---

# CI/CD Introduction

## 1. What Is CI/CD?

**Continuous Integration (CI)** automatically checks changes to a codebase. **Continuous Deployment/Delivery (CD)** automates the process of releasing tested changes.

A simplified pipeline:

```text
Developer Push
     ↓
Tests
     ↓
Lint / Quality Checks
     ↓
Build
     ↓
Package
     ↓
Deploy
```

## 2. Why CI/CD Helps ML Teams

ML projects contain more than model code. They include:

- Data processing code
- API code
- Tests
- Configuration
- Dependency files
- Docker configuration
- Model artifacts or model-loading logic

Automation reduces the chance that a working local project fails during deployment.

## 3. A Simple GitHub Actions Workflow

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - run: pip install -r requirements.txt
      - run: pytest
```

## 4. Tests for ML Services

Useful tests include:

- API health check
- Input validation
- Prediction output shape
- Model loading
- Preprocessing
- Critical business rules

## 5. Deployment Safety

A professional pipeline should avoid automatically deploying every untested change. Use tests, review, and appropriate approval gates.

## Exercise

Create a CI workflow that installs your project dependencies and runs your automated tests on every push.
