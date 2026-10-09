---
id: 06-cloud-storage-and-compute
title: Cloud: S3 Storage and EC2 Basics
sidebar_position: 6
---

# Cloud: S3 Storage and EC2 Basics

## Why Cloud?

Cloud platforms provide scalable storage and compute resources. The syllabus permits AWS or Azure; this chapter uses AWS terminology where the syllabus names S3 and EC2.

## S3 Storage

Amazon S3 is object storage.

```text
Bucket
 ├── raw/
 ├── processed/
 ├── models/
 └── reports/
```

## EC2 Basics

Amazon EC2 provides virtual compute instances.

```text
Cloud → EC2 Instance → OS → Python / Spark / Application
```

## Security

Never place cloud credentials directly inside source code. Use secure credential-management mechanisms and least-privilege permissions.

## Exercise

Design a cloud storage layout with separate raw data, processed data, models, and reports areas.
