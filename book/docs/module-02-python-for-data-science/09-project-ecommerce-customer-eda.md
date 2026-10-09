---
id: project-ecommerce-customer-eda
title: Home Project — E-commerce Customer EDA
sidebar_position: 9
---

# Home Project — E-commerce Customer EDA

## Project Goal

Analyze customer behavior and purchasing patterns using an e-commerce dataset.

This project is designed as a home-based project in the syllabus and should reinforce the complete exploratory data analysis workflow.

## Suggested Questions

Investigate questions such as:

- How many customers are represented?
- What is the average order value?
- Which products or categories are most popular?
- Which customer groups purchase more frequently?
- Are there visible differences between regions or segments?

## Recommended Workflow

### 1. Load the Data

```python
import pandas as pd

df = pd.read_csv("ecommerce.csv")
```

### 2. Inspect

```python
print(df.head())
print(df.info())
print(df.describe(include="all"))
```

### 3. Clean

Check:

```python
print(df.isna().sum())
print(df.duplicated().sum())
```

Apply only cleaning decisions that make sense for the dataset.

### 4. Explore Customer Behavior

For example:

```python
customer_orders = df.groupby("CustomerID").size()
print(customer_orders.describe())
```

### 5. Analyze Purchases

```python
category_sales = (
    df.groupby("Category")["Amount"]
    .sum()
    .sort_values(ascending=False)
)

print(category_sales)
```

### 6. Visualize

Use suitable Matplotlib, Seaborn, or Plotly charts to communicate the patterns you find.

## Final Report

Your report should contain:

- Dataset description.
- Cleaning steps.
- Key statistics.
- At least three visualizations.
- Major findings.
- Limitations of the analysis.
- Suggestions for further investigation.

## Assessment Criteria

A strong submission should demonstrate:

- Correct Pandas usage.
- Logical cleaning decisions.
- Meaningful aggregation.
- Appropriate visualizations.
- Clear written interpretation.

## Extension

Create customer segments using simple rule-based categories such as low, medium, and high spending. Explain the rules you selected.
