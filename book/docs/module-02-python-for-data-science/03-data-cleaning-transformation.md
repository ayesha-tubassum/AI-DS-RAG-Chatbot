---
id: data-cleaning-transformation
title: Data Cleaning and Transformation
sidebar_position: 3
---

# Data Cleaning and Transformation

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain why data cleaning is necessary.
- Identify common data quality problems.
- Rename columns and standardize values.
- Remove duplicate records.
- Convert columns into useful formats.
- Create transformed features for analysis.

## 1. Why Data Cleaning Matters

Real-world datasets are rarely perfectly organized. They may contain inconsistent spelling, duplicate records, incorrect data types, unnecessary spaces, or values stored in inconvenient formats.

Data cleaning prepares the dataset for reliable analysis.

A useful workflow is:

1. Inspect the data.
2. Identify quality problems.
3. Clean or transform values.
4. Validate the result.
5. Continue with analysis.

## 2. Inspecting a Dataset

```python
import pandas as pd

df = pd.read_csv("customers.csv")

print(df.head())
print(df.info())
print(df.describe(include="all"))
```

## 3. Removing Duplicate Rows

```python
df = df.drop_duplicates()
```

You should understand why duplicates exist before automatically removing them.

## 4. Standardizing Text

Suppose customer names contain unnecessary spaces:

```python
df["Name"] = df["Name"].str.strip()
```

Values can also be standardized:

```python
df["City"] = df["City"].str.title()
```

For categories such as gender or status, consistent spelling is important.

## 5. Renaming Columns

```python
df = df.rename(columns={
    "Cust Name": "customer_name",
    "Total Sale": "total_sale"
})
```

Clear column names make analysis easier to understand.

## 6. Data Type Conversion

```python
df["date"] = pd.to_datetime(df["date"])
df["price"] = pd.to_numeric(df["price"], errors="coerce")
```

Data types matter because they determine which operations can be performed safely.

## 7. Creating New Features

Transformation often means creating a new column from existing information.

```python
df["total"] = df["quantity"] * df["unit_price"]
```

This is a basic example of **feature creation**.

## 8. Normalization

Normalization can refer to transforming numerical values to a comparable scale.

A common min-max transformation is:

```python
df["scaled"] = (
    (df["score"] - df["score"].min()) /
    (df["score"].max() - df["score"].min())
)
```

The exact transformation should be selected according to the analysis or modelling requirement.

## 9. Validation After Cleaning

Cleaning is not complete simply because code executed without an error.

Check:

```python
print(df.shape)
print(df.dtypes)
print(df.head())
print(df.isna().sum())
print(df.duplicated().sum())
```

## Real-World Example

Imagine an e-commerce dataset where one customer appears twice, city names use different capitalization, and prices are stored as text. Cleaning converts the raw dataset into a consistent table that can be safely summarized and visualized.

## Important Terminology

- **Data cleaning:** Correcting or managing data quality problems.
- **Transformation:** Changing data into a more useful representation.
- **Duplicate:** A repeated record.
- **Feature:** A variable used to describe an observation.
- **Normalization:** Rescaling numerical values according to a chosen method.

## Key Takeaways

- Cleaning is a necessary stage of data analysis.
- Always inspect data before modifying it.
- Text, duplicates, data types, and inconsistent values are common issues.
- Transformations can create useful analytical features.
- Validate the cleaned dataset before using it.

## Review Questions

1. Why is data cleaning important?
2. How can duplicate rows be detected?
3. Why should data types be checked?
4. What is a transformed feature?
5. Describe a realistic example of a messy dataset.
