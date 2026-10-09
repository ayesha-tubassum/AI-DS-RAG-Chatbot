---
id: 03-hypothesis-testing
title: Hypothesis Testing
sidebar_position: 3
---

# Hypothesis Testing

## Learning Objectives
- Explain hypothesis testing.
- Define null and alternative hypotheses.
- Understand significance levels and p-values.
- Interpret statistical results responsibly.
- Apply a simple test with Python.

## 1. Purpose
Hypothesis testing evaluates a claim about a population using sample data. It asks whether observed evidence is sufficiently inconsistent with a baseline assumption.

## 2. Null and Alternative Hypotheses
The **null hypothesis (H₀)** is the baseline assumption. The **alternative hypothesis (H₁/Hₐ)** is the competing claim.

Example:
```text
H₀: A new process does not change average delivery time.
H₁: A new process changes average delivery time.
```

## 3. Significance Level
A significance level, often written as alpha (α), is chosen before interpreting the result. `0.05` is commonly used, but it is not a universal rule.

## 4. P-Value
A p-value describes how compatible the observed result is with the null hypothesis under the selected test model. A small p-value can provide evidence against H₀.

A p-value is **not** the probability that H₀ is true.

## 5. Basic Workflow
1. Define the research question.
2. State H₀ and H₁.
3. Select an appropriate test.
4. Choose alpha.
5. Prepare the data.
6. Calculate the statistic and p-value.
7. Interpret the result in context.

## 6. Python Example
```python
from scipy import stats

sample = [48, 51, 49, 52, 50, 53, 47, 51]
result = stats.ttest_1samp(sample, popmean=50)

print(result.statistic)
print(result.pvalue)
```

The correct interpretation depends on the hypotheses, assumptions, and research design.

## 7. Statistical vs Practical Significance
A statistically significant result is not automatically practically important. Always consider effect size, sample size, context, and consequences.

## Real-World Example
A company tests whether a redesigned checkout increases average order value. A statistical test can evaluate whether the observed change is compatible with the baseline assumption.

## Important Terminology
Null hypothesis, alternative hypothesis, significance level, p-value, effect size, statistical significance.

## Key Takeaways
- Define hypotheses before evaluating results.
- Select a test that matches the research question.
- Interpret p-values carefully.
- Statistical significance and practical importance are different.

## Review Questions
1. What is H₀?
2. What does a p-value represent?
3. Why choose alpha before the test?
4. Why is statistical significance not the same as practical significance?
5. Why must the test match the data?
