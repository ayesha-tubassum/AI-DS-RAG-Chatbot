---
id: 09-spark-mllib-training-project
title: Class Project — Spark MLlib Model Training
sidebar_position: 9
---

# Class Project — Spark MLlib Model Training

## Goal

Train and evaluate a machine-learning model using Spark MLlib.

## Requirements

1. Load data into a Spark DataFrame.
2. Identify the label column.
3. Prepare feature columns.
4. Build a feature vector.
5. Split the data.
6. Train an MLlib model.
7. Generate predictions.
8. Evaluate the model.
9. Explain the selected metric.

```text
Dataset → Spark DataFrame → Feature Vector → Train/Test Split
        → MLlib Model → Predictions → Evaluation
```

## Deliverables

- Training notebook/script
- Model evaluation
- Results table
- Scalability explanation
- README

Do not assume Spark is faster for every workload; distributed processing has overhead.
