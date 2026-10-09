---
id: merging-and-groupby
title: Merging and GroupBy
sidebar_position: 5
---

# Merging and GroupBy

## Learning Objectives

You will learn how to:

- Combine related datasets.
- Understand the purpose of keys in a merge.
- Use common merge types.
- Group records by categories.
- Calculate aggregations.
- Build useful summary tables.

## 1. Why Combine Datasets?

Business and analytical data is often stored in multiple tables.

For example:

**Customers**

| customer_id | name |
|---|---|
| 1 | Ali |
| 2 | Sara |

**Orders**

| customer_id | amount |
|---|---:|
| 1 | 500 |
| 2 | 800 |

The shared `customer_id` can be used to combine the tables.

## 2. Merging DataFrames

```python
import pandas as pd

customers = pd.DataFrame({
    "customer_id": [1, 2],
    "name": ["Ali", "Sara"]
})

orders = pd.DataFrame({
    "customer_id": [1, 2],
    "amount": [500, 800]
})

result = pd.merge(customers, orders, on="customer_id")
print(result)
```

## 3. Common Merge Types

A merge can be conceptually understood as:

- **Inner:** Keep matching keys from both datasets.
- **Left:** Keep all records from the left dataset.
- **Right:** Keep all records from the right dataset.
- **Outer:** Keep records from both sides.

Example:

```python
result = pd.merge(
    customers,
    orders,
    on="customer_id",
    how="left"
)
```

## 4. What is GroupBy?

`groupby()` divides records into groups and lets you calculate summaries for each group.

```python
sales = pd.DataFrame({
    "city": ["Lahore", "Lahore", "Karachi", "Karachi"],
    "sales": [100, 200, 150, 300]
})

summary = sales.groupby("city")["sales"].sum()
print(summary)
```

## 5. Multiple Aggregations

```python
summary = sales.groupby("city")["sales"].agg(
    ["sum", "mean", "count"]
)

print(summary)
```

This can answer questions such as:

- How much was sold in each city?
- What is the average sale?
- How many transactions occurred?

## 6. Grouping by Multiple Columns

```python
result = df.groupby(
    ["city", "product"]
)["sales"].sum()
```

This is useful when analysis requires more detailed categories.

## Real-World Example

An e-commerce company may merge customer information with order transactions and then group orders by city, product, or customer segment. This turns raw transaction records into decision-ready summaries.

## Important Terminology

- **Key:** A field used to relate records between datasets.
- **Merge:** Combining DataFrames using related columns.
- **GroupBy:** Splitting records into groups for analysis.
- **Aggregation:** Summarizing multiple observations.
- **Inner join:** A merge that retains matching records.

## Key Takeaways

- Merging connects related datasets.
- The key column must represent the relationship correctly.
- Different merge types answer different data questions.
- `groupby()` is essential for aggregation and summaries.
- Good grouping design leads to useful analytical insights.

## Review Questions

1. What is a key in a dataset?
2. What is the difference between an inner and left merge?
3. Why is `groupby()` useful?
4. Write code to calculate total sales by city.
5. Give an example where two datasets should be merged.
