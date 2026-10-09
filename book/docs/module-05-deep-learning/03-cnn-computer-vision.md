---
id: 03-cnn-computer-vision
title: Computer Vision and CNNs
sidebar_position: 3
---

# Computer Vision and CNNs

## Learning Objectives
Understand how Convolutional Neural Networks process image data and extract useful visual features.

## 1. Images as Data
A color image can be represented as a tensor:

```text
Height × Width × Channels
```

For RGB images, channels usually represent red, green, and blue.

## 2. Convolution
A convolutional layer applies learnable filters across an image. Early filters may learn simple patterns such as edges; deeper layers can represent increasingly complex patterns.

```text
Image → Convolution → Activation → Pooling → Deeper Features → Classifier
```

## 3. CNN Components
Common components:
- Convolutional layers
- Activation functions
- Pooling layers
- Flattening or global pooling
- Dense classification layers

## 4. Example CNN

```python
import tensorflow as tf

model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, 3, activation="relu",
                           input_shape=(128, 128, 3)),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Conv2D(64, 3, activation="relu"),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(64, activation="relu"),
    tf.keras.layers.Dense(1, activation="sigmoid")
])

model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)
```

## 5. Image Augmentation
Augmentation creates varied training examples through transformations such as:
- Horizontal flips
- Small rotations
- Cropping
- Zooming

Use augmentation carefully so transformations remain realistic for the task.

## 6. Evaluation
For image classification, examine:
- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix

## Key Takeaways
CNNs learn spatial patterns directly from image tensors. Convolution and pooling help construct hierarchical visual representations.

## Review Questions
1. What is a convolution?
2. Why are CNNs useful for images?
3. What does pooling do?
4. Why use data augmentation?

