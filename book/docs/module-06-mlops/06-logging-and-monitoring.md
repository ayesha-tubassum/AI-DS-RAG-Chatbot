---
id: 06-logging-and-monitoring
title: Logging and Monitoring
sidebar_position: 6
---

# Logging and Monitoring

## 1. Why Monitoring?

A model can perform well during development and still behave poorly in production because the incoming data or environment changes.

Monitoring helps answer:

- Is the API available?
- How long do predictions take?
- How many requests fail?
- Are input distributions changing?
- Is model quality changing when labels become available?

## 2. Logging

Python provides a standard logging library:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Prediction request received")
```

Avoid logging sensitive personal information.

## 3. What to Monitor

### System Metrics

- Request count
- Error rate
- Response latency
- CPU/memory usage

### ML Metrics

- Prediction distribution
- Input feature distribution
- Data drift
- Model accuracy or other quality metrics when ground truth becomes available

## 4. Data Drift

Data drift occurs when production input data changes relative to the data used during training.

Example:

```text
Training customers: average age = 35
Production customers: average age = 52
```

That does not automatically mean the model has failed, but it is a signal worth investigating.

## 5. Monitoring Loop

```text
Production Requests
        ↓
Logs + Metrics
        ↓
Drift / Performance Checks
        ↓
Investigation
        ↓
Retraining or Model Update
```

## 6. Exercise

Design a monitoring checklist for your ML API. Include at least three system metrics and three ML/data metrics.
