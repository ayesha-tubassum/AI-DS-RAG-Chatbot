---
id: 01-big-data-and-hadoop
title: Big Data and Hadoop
sidebar_position: 1
---

# Big Data and Hadoop

## What Is Big Data?

Big Data refers to datasets whose volume, velocity, or variety can make traditional single-machine processing difficult.

Key characteristics include:

- **Volume:** very large amounts of data
- **Velocity:** data arriving quickly
- **Variety:** different formats and sources

## Why Distributed Processing?

Distributed systems divide data and computation across multiple machines.

```text
Large Dataset
     ↓
Partition
 ┌───┼───┐
 ↓   ↓   ↓
W1  W2  W3
 └───┼───┘
     ↓
   Result
```

## Hadoop

The syllabus introduces Hadoop as a framework for distributed storage and processing. The main topics are HDFS, MapReduce, and YARN.

## HDFS

**Hadoop Distributed File System (HDFS)** stores large files across multiple machines.

```text
Client
  ↓
NameNode → Metadata
  ↓
DataNodes → Data Blocks
```

## MapReduce

MapReduce is a distributed processing model:

```text
Input → Map → Shuffle/Group → Reduce → Output
```

A word-count task can map each word to `(word, 1)` and reduce repeated words by summing values.

## YARN

YARN is Hadoop's resource-management layer. It helps coordinate cluster resources and applications.

## Exercise

Draw an architecture showing HDFS storage, DataNodes, MapReduce processing, and YARN resource management.
