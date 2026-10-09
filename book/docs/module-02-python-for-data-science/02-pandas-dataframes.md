---
id: pandas-dataframes
title: Pandas DataFrames
sidebar_position: 2
---

# Pandas DataFrames

## Learning Objectives

You will learn how to:

- Explain the purpose of Pandas.
- Create Series and DataFrames.
- Load tabular data.
- Select rows and columns.
- Inspect and manipulate DataFrames.
- Use labels and indexes effectively.

## 1. What is Pandas?

Pandas is a Python library for working with structured and tabular data. It is especially useful when data is arranged in rows and columns, such as customer records, sales transactions, survey results, or weather observations.

The central structure used in this chapter is the **DataFrame**.

```python
import pandas as pd

data = {
    "Name": ["Ali", "Sara", "Hamza"],
    "Marks": [82, 91, 76]
}

df = pd.DataFrame(data)
print(df)
```

## 2. Series and DataFrame

A **Series** is a one-dimensional labelled structure.

```python
marks = pd.Series([80, 90, 75])
```

A **DataFrame** is a two-dimensional table.

```python
df = pd.DataFrame({
    "Name": ["A", "B"],
    "Marks": [80, 90]
})
```

## 3. Inspecting Data

Useful commands include:

```python
print(df.head())
print(df.tail())
print(df.info())
print(df.describe())
print(df.shape)
```

These commands help you understand a dataset before analysis.

## 4. Selecting Columns

```python
print(df["Name"])
print(df[["Name", "Marks"]])
```

## 5. Selecting Rows

With `loc`, selection is based on labels.

```python
print(df.loc[0])
```

With `iloc`, selection is based on integer positions.

```python
print(df.iloc[0])
```

## 6. Filtering Data

```python
high_scores = df[df["Marks"] >= 80]
print(high_scores)
```

Multiple conditions can be combined carefully:

```python
result = df[(df["Marks"] >= 80) & (df["Name"] != "Ali")]
```

## 7. Creating and Updating Columns

```python
df["Passed"] = df["Marks"] >= 50
print(df)
```

Columns can also be transformed:

```python
df["Bonus"] = df["Marks"] * 0.05
```

## 8. Reading a CSV File

```python
df = pd.read_csv("sales.csv")
print(df.head())
```

When working with real data, always inspect the dataset after loading it.

## Practical Example: Sales Table

```python
sales = pd.DataFrame({
    "Product": ["Laptop", "Phone", "Tablet"],
    "Units": [5, 12, 8],
    "Price": [1000, 600, 400]
})

sales["Revenue"] = sales["Units"] * sales["Price"]
print(sales)
```

## Important Terminology

- **DataFrame:** A labelled two-dimensional table.
- **Series:** A one-dimensional labelled data structure.
- **Index:** Labels used to identify rows.
- **Filtering:** Selecting records that satisfy conditions.
- **Inspection:** Examining structure and values before analysis.

## Key Takeaways

- Pandas is a core tool for tabular data analysis.
- DataFrames represent rows and columns.
- Inspect data before performing analysis.
- `loc` and `iloc` provide different ways to select data.
- Columns can be created from existing values.

## Review Questions

1. What is a DataFrame?
2. What is the difference between `loc` and `iloc`?
3. How can you filter rows where a value is greater than 100?
4. Why should a dataset be inspected before analysis?
5. Create a DataFrame with three products and calculate revenue.
