---
id: 11-transfer-learning-project
title: Class Project — Transfer Learning with ResNet/VGG
sidebar_position: 11
---

# Class Project — Transfer Learning with ResNet/VGG

## Goal
Apply a pre-trained ResNet or VGG model to a new image-classification task.

## Required Comparison
Compare:
1. A small CNN baseline.
2. A transfer-learning model.

## Workflow
```text
Dataset
→ Resize/Normalize
→ Pre-trained Backbone
→ Freeze
→ New Classification Head
→ Train
→ Optional Fine-Tuning
→ Evaluate
```

## Questions
- Does transfer learning outperform the baseline?
- How much training time is saved?
- Does fine-tuning improve validation performance?
- Does the model overfit?

## Deliverables
Baseline results, transfer-learning results, training curves, confusion matrix, comparison table, and conclusion.

