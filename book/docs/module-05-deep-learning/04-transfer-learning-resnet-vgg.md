---
id: 04-transfer-learning-resnet-vgg
title: Transfer Learning — ResNet and VGG
sidebar_position: 4
---

# Transfer Learning — ResNet and VGG

## 1. What Is Transfer Learning?
Transfer learning starts with a model trained on a large dataset and adapts it to a new task.

Instead of learning every visual feature from scratch:

```text
Pre-trained Model → Adapt to New Dataset → Fine-Tune
```

The syllabus specifically includes **ResNet** and **VGG** as examples.

## 2. Why Use It?
Transfer learning can:
- Reduce training time.
- Work well when the new dataset is relatively small.
- Reuse useful visual representations.

## 3. Feature Extraction
A common approach is to freeze the pre-trained backbone and train a new classification head.

Conceptually:

```python
base_model.trainable = False
```

Then add a task-specific output layer.

## 4. Fine-Tuning
After the new head has learned, selected layers of the backbone may be unfrozen and trained with a small learning rate.

This should be validated carefully because aggressive fine-tuning can damage useful pre-trained representations.

## 5. Example Structure

```python
import tensorflow as tf

base = tf.keras.applications.ResNet50(
    include_top=False,
    weights="imagenet",
    input_shape=(224, 224, 3)
)

base.trainable = False

model = tf.keras.Sequential([
    base,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(1, activation="sigmoid")
])
```

## Key Takeaways
Transfer learning reuses learned representations. ResNet and VGG are important examples of pre-trained image models.

## Review Questions
1. What is transfer learning?
2. Why freeze a pre-trained model initially?
3. What is fine-tuning?
4. Name the two example architectures in this syllabus.

