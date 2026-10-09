---
id: handling-missing-values
title: Handling Missing Values
sidebar_position: 4
---

# Handling Missing Values

## Learning Objectives

You will learn how to:

- Identify missing values in Pandas.
- Understand why missing data occurs.
- Distinguish between detection and treatment.
- Remove missing records when appropriate.
- Fill missing values using suitable strategies.
- Validate your final dataset.

## 1. What Are Missing Values?

A missing value means that information expected for a record is unavailable or not recorded.

For example:

| Customer | Age | City |
|---|---:|---|
| Ali | 25 | Lahore |
| Sara | | Karachi |
| Hamza | 31 | |

Missing data can occur because a person skipped a field, a sensor failed, a database was incomplete, or two systems used different schemas.

## 2. Detecting Missing Values

```python
print(df.isna())
print(df.isna().sum())
```

To find rows containing missing values:

```python
missing_rows = df[df.isna().any(axis=1)]
print(missing_rows)
```

## 3. Removing Missing Records

A simple option is:

```python
df_clean = df.dropna()
```

However, removing rows can discard useful information. Therefore, do not use `dropna()` automatically.

## 4. Filling Missing Values

For a numerical column, a common approach is to use a summary statistic.

```python
df["Age"] = df["Age"].fillna(df["Age"].median())
```

For categorical data:

```python
df["City"] = df["City"].fillna("Unknown")
```

The correct strategy depends on the meaning of the variable.

## 5. Forward and Backward Filling

For ordered data, previous or next observations may sometimes be used.

```python
df["value"] = df["value"].ffill()
df["value"] = df["value"].bfill()
```

This should only be used when the ordering and domain make the assumption reasonable.

## 6. Checking the Result

```python
print(df.isna().sum())
```

A cleaning operation should always be followed by validation.

## Practical Example: Weather Data

Suppose a weather dataset has missing temperature readings. If the missing values are few, dropping those records might be acceptable. If the dataset is a time series where continuity matters, an appropriate imputation method may be more useful.

## Important Terminology

- **Missing value:** An unavailable observation.
- **Imputation:** Replacing missing values using a chosen strategy.
- **Median:** Middle value after sorting observations.
- **Forward fill:** Using a previous available value.
- **Backward fill:** Using a following available value.

## Key Takeaways

- Missing values are common in real datasets.
- First detect missingness, then decide how to treat it.
- Dropping data is not always the best solution.
- Filling values requires an understanding of the data.
- Always verify the result after treatment.

## Review Questions

1. How can you count missing values in every column?
2. When might dropping rows be appropriate?
3. Why might the median be useful for filling numerical values?
4. What is imputation?
5. Give one situation where forward filling could make sense.
