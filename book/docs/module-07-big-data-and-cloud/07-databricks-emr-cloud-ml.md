---
id: 07-databricks-emr-cloud-ml
title: Databricks, EMR and Cloud ML Deployment
sidebar_position: 7
---

# Databricks, EMR and Cloud ML Deployment

The syllabus introduces Databricks / EMR as cloud-based platforms for Spark and Hadoop workloads.

## Cloud Data Workflow

```text
Cloud Storage
     ↓
Spark / Distributed Processing
     ↓
Cleaned Data
     ↓
Feature Engineering
     ↓
ML Training
     ↓
Model Artifact
     ↓
Deployment
```

## Deploying ML Models on Cloud

1. Train the model.
2. Save the model artifact.
3. Package inference code.
4. Select compute infrastructure.
5. Configure dependencies.
6. Deploy the service.
7. Test predictions.
8. Monitor the service.

## Cost Awareness

Cloud resources can incur charges. Shut down unused compute resources and understand service pricing.

## Exercise

Draw a cloud architecture in which S3 stores data, Spark processes it, an ML model is trained, and a prediction service is deployed.
