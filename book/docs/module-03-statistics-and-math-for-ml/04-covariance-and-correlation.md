---
id: 04-covariance-and-correlation
title: Covariance and Correlation
sidebar_position: 4
---

# Covariance and Correlation

## Learning Objectives
- Explain covariance and correlation.
- Interpret positive and negative relationships.
- Calculate correlation with Python.
- Understand correlation matrices.
- Explain why correlation does not prove causation.

## 1. Studying Relationships
Data science often asks whether two variables move together, such as advertising and sales or study hours and scores.

## 2. Covariance
Covariance describes the direction of joint variation:
- Positive: variables tend to increase together.
- Negative: one tends to increase while the other decreases.
- Near zero: little linear co-movement by this measure.

Its magnitude depends on the variables' units.

## 3. Correlation
Correlation standardizes linear association and commonly ranges from `-1` to `+1`.

```text
+1 → strong positive linear association
 0 → no linear association according to the coefficient
-1 → strong negative linear association
```

```python
import pandas as pd

df = pd.DataFrame({
    "study_hours": [1, 2, 3, 4, 5],
    "score": [55, 60, 68, 78, 85]
})

print(df["study_hours"].corr(df["score"]))
print(df["study_hours"].cov(df["score"]))
```

## 4. Correlation Matrix
```python
print(df.corr(numeric_only=True))
```

A matrix can be visualized:

```python
import seaborn as sns
import matplotlib.pyplot as plt

sns.heatmap(df.corr(numeric_only=True), annot=True)
plt.show()
```

## 5. Correlation Is Not Causation
A correlation does not prove that one variable causes another. A third variable may affect both, or the relationship may be coincidental.

## Real-World Example
Advertising and sales may be positively correlated, but other factors such as seasonality, pricing, and promotions can also affect sales.

## Important Terminology
Covariance, correlation, positive association, negative association, causation, Pearson correlation.

## Key Takeaways
- Covariance shows direction of joint variation.
- Correlation gives a standardized measure of linear association.
- Correlation should be combined with visualization and context.
- Correlation does not prove causation.

## Review Questions
1. What does positive covariance mean?
2. What is the range of Pearson correlation?
3. What does a correlation near -1 indicate?
4. Why does correlation not prove causation?
5. Why should a scatter plot accompany correlation analysis?
