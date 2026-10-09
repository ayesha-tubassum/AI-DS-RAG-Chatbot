---
id: 01-descriptive-statistics
title: Descriptive Statistics
sidebar_position: 1
---

# Descriptive Statistics

## Learning Objectives
- Explain descriptive statistics and why they are useful.
- Calculate mean, median, mode, variance, and standard deviation.
- Distinguish measures of central tendency from measures of spread.
- Summarize data with Python.

## 1. What Are Descriptive Statistics?
Descriptive statistics summarize observed data so that its main characteristics can be understood without examining every observation individually. They are a foundation for data analysis and machine learning.

A **population** is the complete group being studied, while a **sample** is a subset of that population.

## 2. Measures of Central Tendency

### Mean
The mean is the arithmetic average:

```text
Mean = Sum of values / Number of values
```

```python
import numpy as np

scores = np.array([60, 70, 80, 90, 100])
print(np.mean(scores))
```

### Median
The median is the middle value after sorting the observations.

```python
print(np.median(scores))
```

It is often less affected by extreme values than the mean.

### Mode
The mode is the most frequently occurring value.

```python
from statistics import mode
print(mode([10, 20, 20, 30, 40]))
```

## 3. Measures of Spread

### Range
```text
Range = Maximum - Minimum
```

```python
print(np.max(scores) - np.min(scores))
```

### Variance
Variance measures average squared deviation from the mean.

```python
print(np.var(scores))
```

For sample data, statistical software may use a sample-variance formula with a different denominator.

### Standard Deviation
Standard deviation is the square root of variance.

```python
print(np.std(scores))
```

It is expressed in the same units as the original variable.

## 4. Pandas Summary

```python
import pandas as pd

df = pd.DataFrame({"sales": [100, 120, 150, 180, 200]})
print(df["sales"].describe())
```

## Real-World Example
Two sales teams can have the same average revenue but different standard deviations. One may be consistent while the other has large swings. Therefore, the average alone is not enough.

## Important Terminology
- Mean: arithmetic average.
- Median: middle ordered value.
- Mode: most frequent value.
- Variance: squared measure of spread.
- Standard deviation: square root of variance.
- Population: complete group.
- Sample: subset of a population.

## Key Takeaways
- Central tendency describes the center of data.
- Variance and standard deviation describe spread.
- Extreme values can strongly affect the mean.
- Statistical summaries must be interpreted in context.

## Review Questions
1. What is descriptive statistics?
2. When can median be more useful than mean?
3. What does standard deviation measure?
4. What is the difference between population and sample?
5. Why should mean not be used alone?
