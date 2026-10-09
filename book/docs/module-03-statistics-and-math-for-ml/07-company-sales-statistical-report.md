---
id: 07-company-sales-statistical-report
title: Project — Company Sales Statistical Report
sidebar_position: 7
---

# Project — Company Sales Statistical Report

## Project Goal
Analyze company sales data using descriptive statistics, as specified in the syllabus.

## Skills
- Mean, median, mode
- Variance and standard deviation
- Grouped summaries
- Visualization
- Interpretation

## Suggested Dataset
Possible fields include Date, Product, Region, Quantity, and Revenue. Use the columns available in your selected dataset.

## Step 1 — Load and Inspect
```python
import pandas as pd

df = pd.read_csv("company_sales.csv")
print(df.head())
print(df.info())
print(df.describe())
```

Check data quality:
```python
print(df.isna().sum())
print(df.duplicated().sum())
```

## Step 2 — Statistics
```python
sales = df["Revenue"]

print("Mean:", sales.mean())
print("Median:", sales.median())
print("Std:", sales.std())
print("Variance:", sales.var())
print("Minimum:", sales.min())
print("Maximum:", sales.max())
```

## Step 3 — Compare Regions
```python
summary = df.groupby("Region")["Revenue"].agg(
    ["count", "mean", "median", "std", "sum"]
)
print(summary)
```

## Step 4 — Interpret
Answer:
- What is the typical sale?
- How much does revenue vary?
- Which region has the highest total?
- Which region is more consistent?
- Are there unusual observations?

## Report Structure
1. Introduction
2. Dataset description
3. Data preparation
4. Descriptive statistics
5. Group comparison
6. Visualizations
7. Findings
8. Limitations
9. Conclusion

## Submission Checklist
- [ ] Data quality checked.
- [ ] Mean, median, variance and standard deviation calculated.
- [ ] Groups compared.
- [ ] Visualizations included.
- [ ] Findings explained in words.
