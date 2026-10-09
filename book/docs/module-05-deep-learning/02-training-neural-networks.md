---
id: 02-training-neural-networks
title: Training Neural Networks
sidebar_position: 2
---

# Training Neural Networks

## 1. Dataset Splits
A deep-learning project commonly separates data into training, validation, and test sets.

```text
Training → Learn parameters
Validation → Select/tune the model
Test → Final unseen evaluation
```

## 2. Epochs and Batches
An **epoch** is one complete pass through the training data.

A **batch** is a smaller group of examples processed together.

```python
history = model.fit(
    X_train,
    y_train,
    epochs=20,
    batch_size=32,
    validation_split=0.2
)
```

## 3. Overfitting
A neural network can memorize training data instead of learning general patterns.

Typical warning signs:
- Training loss keeps improving.
- Validation loss stops improving or gets worse.

## 4. Regularization
Useful approaches include:
- Dropout
- Weight regularization
- Data augmentation for images
- Early stopping

```python
callback = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=3,
    restore_best_weights=True
)
```

## 5. Monitoring Learning
Plot training and validation loss/metrics to understand whether the model is learning effectively.

## 6. Practical Workflow
```text
Prepare Data
→ Build Model
→ Compile
→ Train
→ Monitor Validation
→ Evaluate Test Set
→ Save Model
```

## Key Takeaways
Training requires more than choosing layers. Data preparation, validation, optimization, and regularization all influence performance.

## Review Questions
1. What is an epoch?
2. What is a batch?
3. Why use validation data?
4. What is overfitting?
5. Name two regularization techniques.

