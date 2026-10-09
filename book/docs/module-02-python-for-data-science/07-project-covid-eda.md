---
id: project-covid-eda
title: Project — COVID Dataset Exploratory Data Analysis
sidebar_position: 7
---

# Project — COVID Dataset Exploratory Data Analysis

## Project Goal

The goal of this project is to apply NumPy, Pandas, data cleaning, aggregation, and visualization to a real-world-style COVID dataset.

The syllabus defines this as a class-based project focused on extracting insights and trends from COVID-19 data.

## Skills Practiced

- Dataset loading
- Data inspection
- Data cleaning
- Missing-value analysis
- GroupBy
- Aggregation
- Time-based analysis
- Visualization
- Interpretation of results

## Suggested Dataset Structure

Your dataset may contain fields such as:

- Date
- Country or region
- Confirmed cases
- Deaths
- Recovered cases

The exact columns depend on the dataset selected.

## Step 1: Load the Data

```python
import pandas as pd

df = pd.read_csv("covid_data.csv")
print(df.head())
print(df.info())
```

## Step 2: Inspect Data Quality

```python
print(df.isna().sum())
print(df.duplicated().sum())
```

Decide how missing or duplicate records should be handled based on the dataset.

## Step 3: Clean the Data

Convert dates when appropriate:

```python
df["Date"] = pd.to_datetime(df["Date"])
```

Remove duplicates if they represent repeated records:

```python
df = df.drop_duplicates()
```

## Step 4: Explore Summary Statistics

```python
print(df.describe())
```

Calculate totals where appropriate:

```python
print(df["Confirmed"].sum())
print(df["Deaths"].sum())
```

## Step 5: Group by Country

```python
country_summary = df.groupby("Country")[["Confirmed", "Deaths"]].sum()
print(country_summary)
```

Sort the result:

```python
country_summary = country_summary.sort_values(
    "Confirmed",
    ascending=False
)
```

## Step 6: Visualize Trends

```python
import matplotlib.pyplot as plt

daily = df.groupby("Date")["Confirmed"].sum()

daily.plot(figsize=(10, 5))
plt.title("Confirmed Cases Over Time")
plt.xlabel("Date")
plt.ylabel("Confirmed Cases")
plt.show()
```

## Step 7: Interpret the Results

Do not stop after generating charts. Write observations in complete sentences.

For example:

- Which regions have the largest totals?
- How did the metric change over time?
- Are there unusual spikes?
- Could reporting practices affect interpretation?

## Deliverables

Students should submit:

1. A cleaned notebook.
2. At least three meaningful visualizations.
3. A short written analysis.
4. A list of important findings.
5. A brief explanation of cleaning decisions.

## Extension Tasks

- Compare two or more countries.
- Create a rolling trend if the dataset supports it.
- Compare confirmed cases and deaths.
- Build an interactive Plotly chart.

## Project Review

Before submission, confirm that:

- The dataset loads correctly.
- Dates have appropriate types.
- Missing values were examined.
- Duplicate records were considered.
- Aggregations are understandable.
- Charts have labels and titles.
- Conclusions are supported by the data.
