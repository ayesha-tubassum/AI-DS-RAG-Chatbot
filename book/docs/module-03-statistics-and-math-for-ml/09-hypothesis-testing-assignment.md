---
id: 09-hypothesis-testing-assignment
title: Home Project — Hypothesis Testing Assignment
sidebar_position: 9
---

# Home Project — Hypothesis Testing Assignment

## Project Goal
Apply hypothesis testing to a real dataset and make an evidence-based conclusion.

## Step 1 — Research Question
Examples:
- Did a new process change average delivery time?
- Is an average different from a reference value?
- Do two groups show evidence of a difference?

## Step 2 — Hypotheses
Write:
```text
H₀:
H₁:
```

Define them before evaluating results.

## Step 3 — Significance Level
```python
alpha = 0.05
```
The selected value should be justified by the context.

## Step 4 — Prepare Data
```python
print(df.info())
print(df.isna().sum())
```

Document cleaning decisions.

## Step 5 — Example Test
```python
from scipy import stats

result = stats.ttest_1samp(
    df["measurement"],
    popmean=50
)

print(result.statistic)
print(result.pvalue)
```

This is an example only; select the test that matches your research design.

## Step 6 — Interpret
Report:
- Test used.
- Test statistic.
- P-value.
- Significance level.
- Statistical decision.
- Practical meaning.

Do not describe a p-value as the probability that H₀ is true.

## Step 7 — Limitations
Discuss sample size, sampling method, assumptions, measurement quality, and generalizability.

## Report Structure
1. Research question
2. Dataset
3. Hypotheses
4. Method
5. Preparation and assumptions
6. Result
7. Interpretation
8. Limitations
9. Conclusion
