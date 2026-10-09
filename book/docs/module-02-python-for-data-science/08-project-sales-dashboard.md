---
id: project-sales-dashboard
title: Project — Sales Dashboard with Pandas and Plotly
sidebar_position: 8
---

# Project — Sales Dashboard with Pandas and Plotly

## Project Goal

Build an interactive sales dashboard using Pandas for data preparation and Plotly for visualization.

The dashboard should help a user understand sales performance without manually reading every transaction.

## Skills Practiced

- CSV loading
- Data cleaning
- Feature creation
- GroupBy
- Aggregation
- Interactive visualization
- Dashboard thinking

## Suggested Dataset

A sales dataset may contain:

- Order date
- Product
- Category
- Region
- Quantity
- Unit price
- Revenue

## Step 1: Load and Inspect

```python
import pandas as pd

df = pd.read_csv("sales.csv")

print(df.head())
print(df.info())
print(df.isna().sum())
```

## Step 2: Create Revenue

If revenue is not already present:

```python
df["Revenue"] = df["Quantity"] * df["Unit Price"]
```

## Step 3: Prepare Summary Tables

Total revenue:

```python
total_revenue = df["Revenue"].sum()
print(total_revenue)
```

Revenue by category:

```python
category_sales = df.groupby("Category")["Revenue"].sum().reset_index()
```

Revenue by region:

```python
region_sales = df.groupby("Region")["Revenue"].sum().reset_index()
```

## Step 4: Create an Interactive Chart

```python
import plotly.express as px

fig = px.bar(
    category_sales,
    x="Category",
    y="Revenue",
    title="Revenue by Category"
)

fig.show()
```

## Step 5: Add a Time Trend

```python
df["Order Date"] = pd.to_datetime(df["Order Date"])

monthly = (
    df.groupby(df["Order Date"].dt.to_period("M"))["Revenue"]
    .sum()
    .reset_index()
)

monthly["Order Date"] = monthly["Order Date"].astype(str)

fig = px.line(
    monthly,
    x="Order Date",
    y="Revenue",
    title="Monthly Revenue"
)

fig.show()
```

## Dashboard Questions

Your dashboard should help answer questions such as:

- What is total revenue?
- Which category performs best?
- Which region generates the most sales?
- How does revenue change over time?
- Which products need attention?

## Deliverables

Submit:

1. A cleaned dataset or notebook.
2. Interactive Plotly visualizations.
3. A dashboard or dashboard-style notebook.
4. Written business insights.

## Quality Checklist

- Data was inspected before analysis.
- Missing values were considered.
- Revenue calculation is correct.
- Charts have meaningful titles.
- Filters or categories are understandable.
- Conclusions are connected to the displayed data.

## Extension Task

Add interactive filtering for region or category and compare the results.
