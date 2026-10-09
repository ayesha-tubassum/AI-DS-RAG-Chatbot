---
id: 08-correlation-study
title: Project — Correlation Study
sidebar_position: 8
---

# Project — Correlation Study

## Project Goal
Study variable relationships using covariance and correlation on a suitable dataset.

## Suggested Questions
Examples:
- Do study hours relate to scores?
- Does advertising relate to sales?
- Does temperature relate to energy use?

## Step 1 — Load
```python
import pandas as pd
df = pd.read_csv("dataset.csv")
```

## Step 2 — Calculate
```python
covariance = df["X"].cov(df["Y"])
correlation = df["X"].corr(df["Y"])

print(covariance)
print(correlation)
```

## Step 3 — Visualize
```python
import seaborn as sns
import matplotlib.pyplot as plt

sns.scatterplot(data=df, x="X", y="Y")
plt.title("Relationship Between X and Y")
plt.show()
```

## Step 4 — Correlation Matrix
```python
corr = df.corr(numeric_only=True)
print(corr)
```

## Step 5 — Interpret
Discuss direction, approximate strength, linearity, outliers, and possible third variables.

Do not conclude that correlation proves causation.

## Report Structure
1. Research question
2. Dataset
3. Variables
4. Covariance
5. Correlation
6. Visualization
7. Interpretation
8. Limitations
9. Conclusion

## Checklist
- [ ] Clear question
- [ ] Covariance calculated
- [ ] Correlation calculated
- [ ] Scatter plot included
- [ ] Causation not incorrectly claimed
