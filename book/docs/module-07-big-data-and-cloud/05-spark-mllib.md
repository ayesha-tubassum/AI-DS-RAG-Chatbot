---
id: 05-spark-mllib
title: Spark MLlib
sidebar_position: 5
---

# Spark MLlib

## What Is MLlib?

Spark MLlib is Spark's machine-learning library for scalable machine-learning workflows.

## Typical Workflow

```text
DataFrame → Feature Preparation → Model Training → Prediction → Evaluation
```

## Example Classification Workflow

```python
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression

assembler = VectorAssembler(
    inputCols=["age", "income"],
    outputCol="features"
)

prepared = assembler.transform(df)
train, test = prepared.randomSplit([0.8, 0.2], seed=42)

model = LogisticRegression(
    featuresCol="features",
    labelCol="label"
).fit(train)

predictions = model.transform(test)
predictions.select("label", "prediction").show()
```

Choose evaluation metrics according to the task.

## Exercise

Build a small Spark MLlib classification workflow and compare it with a scikit-learn model on a manageable dataset.
