---
id: data-visualization
title: Data Visualization with Matplotlib, Seaborn and Plotly
sidebar_position: 6
---

# Data Visualization with Matplotlib, Seaborn and Plotly

## Learning Objectives

By the end of this chapter, you should be able to:

- Explain the purpose of data visualization.
- Create basic charts with Matplotlib.
- Use Seaborn for statistical visualizations.
- Understand the purpose of Plotly.
- Choose an appropriate chart for a question.
- Label and communicate visual findings clearly.

## 1. Why Visualize Data?

A table may contain thousands of values. A well-designed chart can make trends, differences, distributions, and relationships easier to recognize.

Visualization is not decoration. It is a method for exploring and communicating data.

## 2. Matplotlib

Matplotlib is a widely used Python visualization library.

```python
import matplotlib.pyplot as plt

months = ["Jan", "Feb", "Mar", "Apr"]
sales = [120, 150, 135, 180]

plt.plot(months, sales)
plt.title("Monthly Sales")
plt.xlabel("Month")
plt.ylabel("Sales")
plt.show()
```

## 3. Bar Charts

Bar charts are useful for comparing categories.

```python
products = ["Laptop", "Phone", "Tablet"]
sales = [120, 180, 90]

plt.bar(products, sales)
plt.title("Sales by Product")
plt.show()
```

## 4. Scatter Plots

Scatter plots help explore relationships between numerical variables.

```python
plt.scatter(df["advertising"], df["sales"])
plt.xlabel("Advertising")
plt.ylabel("Sales")
plt.show()
```

## 5. Seaborn

Seaborn builds on Matplotlib and provides convenient statistical plotting functions.

```python
import seaborn as sns

sns.histplot(df["age"])
plt.show()
```

A box plot can help inspect distributions and potential unusual observations:

```python
sns.boxplot(x=df["salary"])
plt.show()
```

## 6. Plotly

Plotly is useful for interactive visualizations.

```python
import plotly.express as px

fig = px.bar(
    df,
    x="product",
    y="sales",
    title="Sales by Product"
)

fig.show()
```

Interactive charts can allow users to inspect values and categories more easily.

## 7. Choosing the Right Chart

| Question | Useful Chart |
|---|---|
| Compare categories | Bar chart |
| Show a trend over time | Line chart |
| Explore two numerical variables | Scatter plot |
| Understand distribution | Histogram |
| Compare distributions | Box plot |
| Explore interactive business data | Plotly chart |

The chart should match the question being asked.

## 8. Good Visualization Practices

A useful visualization should have:

- A meaningful title.
- Clear axis labels.
- Appropriate scales.
- Readable categories.
- Minimal unnecessary decoration.
- A clear analytical purpose.

Avoid misleading charts that exaggerate differences or hide important context.

## Real-World Example

A sales team might use a line chart to monitor monthly revenue, a bar chart to compare products, and a scatter plot to explore the relationship between advertising expenditure and sales.

## Important Terminology

- **Visualization:** Graphical representation of data.
- **Distribution:** How values are spread.
- **Scatter plot:** A chart showing pairs of numerical observations.
- **Interactive visualization:** A chart users can explore dynamically.
- **Outlier:** An observation that differs substantially from other values.

## Key Takeaways

- Visualization helps humans understand patterns in data.
- Matplotlib provides a flexible foundation.
- Seaborn is convenient for statistical plots.
- Plotly supports interactive visualizations.
- Always choose a chart based on the analytical question.

## Review Questions

1. Why is visualization important?
2. When should you use a bar chart?
3. What does a scatter plot help you investigate?
4. What is one advantage of Plotly?
5. How can a visualization become misleading?
