---
id: 04-fine-tuning-lora-qlora
title: Fine-Tuning with LoRA and QLoRA
sidebar_position: 4
---

# Fine-Tuning with LoRA and QLoRA

## 1. Why Fine-Tune?

A pretrained language model already contains general language knowledge. Fine-tuning can adapt a model toward a particular task, style, or domain.

```text
Pretrained Model
       ↓
Task/Domain Dataset
       ↓
Fine-Tuning
       ↓
Specialized Model
```

## 2. Full Fine-Tuning

Full fine-tuning updates a large portion or all of a model's parameters. For large language models, this can require substantial compute and memory.

## 3. LoRA

**Low-Rank Adaptation (LoRA)** adds trainable low-rank components while keeping the original model weights largely frozen.

Benefits can include:

- Lower trainable parameter count
- Lower memory requirements
- Smaller adapter artifacts
- Easier experimentation

## 4. QLoRA

QLoRA combines quantization with LoRA-style adaptation to reduce memory requirements further.

Conceptually:

```text
Quantized Base Model
        +
LoRA Adapters
        ↓
Efficient Fine-Tuning
```

## 5. When Fine-Tuning Is Not the Best Choice

Fine-tuning is not automatically the answer to every knowledge problem.

If the main requirement is giving the model access to changing or private documents, **RAG** may be more appropriate.

## Exercise

Compare prompting, RAG, and fine-tuning for these cases:
- Company policy documents
- A consistent writing style
- Frequently changing product information
- A classification task with a labeled dataset
