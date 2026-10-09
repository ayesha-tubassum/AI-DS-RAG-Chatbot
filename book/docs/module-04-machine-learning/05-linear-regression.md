---
id: 05-linear-regression
title: Linear Regression
sidebar_position: 5
---

# Linear Regression

## Regression
Regression predicts a continuous numerical value such as price, sales, or delivery time.

A simple model:
`y = b0 + b1x`

Multiple features:
`y = b0 + b1x1 + b2x2 + ... + bnxn`

## Training
```python
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
```

## Evaluation
MAE:
`average(|actual - predicted|)`

MSE:
`average((actual - predicted)^2)`

RMSE is the square root of MSE.

R² describes the proportion of target variation explained by the model under its standard definition.

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

print(mean_absolute_error(y_test, predictions))
print(mean_squared_error(y_test, predictions))
print(r2_score(y_test, predictions))
```

## House Price Example
Features might include area, bedrooms, bathrooms, and age. Target: price.

A coefficient describes the model's fitted relationship; it should not automatically be interpreted as a causal effect.

## Key Takeaways
Linear Regression is a fundamental baseline for continuous prediction. Always evaluate on unseen data.

## Review Questions
1. What is regression?
2. What does MAE measure?
3. Why does MSE emphasize large errors?
4. What does R² describe?


## Syllabus Focus

Regression, linear relationships, coefficients, MAE, MSE, RMSE, R², scikit-learn implementation.
