---
id: 04-spark-dataframes-and-sql
title: Spark DataFrames and Spark SQL
sidebar_position: 4
---

# Spark DataFrames and Spark SQL

## Spark DataFrames

A Spark DataFrame is a distributed structured dataset organized into named columns.

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("DataFrameDemo").getOrCreate()

data = [
    ("Ayesha", 22, 85000),
    ("Sara", 25, 92000),
    ("Ali", 24, 78000),
]

df = spark.createDataFrame(data, ["name", "age", "salary"])
df.show()
df.select("name", "salary").show()
```

## Filtering

```python
df.filter(df.salary > 80000).show()
```

## Grouping

```python
df.groupBy("age").count().show()
```

## Spark SQL

```python
df.createOrReplaceTempView("employees")

result = spark.sql("""
    SELECT age, AVG(salary) AS avg_salary
    FROM employees
    GROUP BY age
""")

result.show()
```

## Exercise

Create a DataFrame containing sales records and use Spark SQL to calculate total sales by product category.
