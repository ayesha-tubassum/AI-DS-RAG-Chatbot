---
id: 02-probability-and-distributions
title: Probability and Distributions
sidebar_position: 2
---

# Probability and Distributions

## Learning Objectives
- Understand probability and uncertainty.
- Explain outcomes, events, and random variables.
- Understand probability distributions.
- Recognize Normal, Binomial, and Poisson distributions.
- Connect probability to machine learning.

## 1. Probability
Probability measures how likely an event is. It ranges from 0 to 1.

For equally likely outcomes:

```text
P(Event) = Favorable outcomes / Total outcomes
```

For a fair die, the probability of rolling a 6 is `1/6`.

## 2. Outcomes and Events
An **outcome** is one possible result. An **event** is one or more outcomes of interest.

For a die:
```text
Sample space = {1, 2, 3, 4, 5, 6}
Even event = {2, 4, 6}
```

## 3. Probability Distributions
A probability distribution describes how probability is assigned to possible values of a random variable.

This module focuses on:
- Normal distribution.
- Binomial distribution.
- Poisson distribution.

### Normal Distribution
The Normal distribution is a continuous, bell-shaped distribution described by a center and spread. Many measurements can be approximately modeled this way when appropriate assumptions hold.

### Binomial Distribution
The Binomial distribution models the number of successes in a fixed number of independent trials with two possible outcomes.

```python
from scipy.stats import binom
print(binom.pmf(3, n=10, p=0.5))
```

### Poisson Distribution
The Poisson distribution is commonly used for counts of events in a specified interval when its assumptions are appropriate.

```python
from scipy.stats import poisson
print(poisson.pmf(4, mu=3))
```

## 4. Probability in ML
Probability is used in classification, uncertainty estimation, sampling, probabilistic models, and many evaluation methods.

## Real-World Example
A support center can analyze the number of calls received per hour. A suitable probability model can help describe the likelihood of different call volumes.

## Important Terminology
- Probability
- Outcome
- Event
- Random variable
- Distribution
- Normal distribution
- Binomial distribution
- Poisson distribution

## Key Takeaways
- Probability gives a language for uncertainty.
- Different distributions model different types of situations.
- Distribution choice depends on the data-generating situation.
- Probability is foundational to machine learning.

## Review Questions
1. What is probability?
2. What is an event?
3. When is Binomial distribution useful?
4. What type of problem can Poisson distribution model?
5. Why does ML use probability?
