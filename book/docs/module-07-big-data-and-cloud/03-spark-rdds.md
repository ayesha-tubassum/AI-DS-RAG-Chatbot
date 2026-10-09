---
id: 03-spark-rdds
title: Apache Spark and RDDs
sidebar_position: 3
---

# Apache Spark and RDDs

## What Is Apache Spark?

Apache Spark is a distributed data-processing framework. The syllabus focuses on RDDs, DataFrames, Spark SQL, and Spark MLlib.

## RDD

**Resilient Distributed Dataset (RDD)** is a distributed collection that can be processed across a cluster.

```text
Dataset → Partition → Distributed RDD → Parallel Operations
```

## Transformations and Actions

Transformations include:

```python
rdd.map(...)
rdd.filter(...)
```

Actions include:

```python
rdd.count()
rdd.collect()
```

Transformations describe work; actions trigger computation.

## Example

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("RDDDemo").getOrCreate()
sc = spark.sparkContext

numbers = sc.parallelize([1, 2, 3, 4, 5])
squared = numbers.map(lambda x: x * x)

print(squared.collect())

spark.stop()
```

## Exercise

Create an RDD containing numbers from 1 to 10. Filter even numbers and calculate their squares.
