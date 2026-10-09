---
id: 02-hdfs-mapreduce-yarn
title: HDFS, MapReduce and YARN
sidebar_position: 2
---

# HDFS, MapReduce and YARN

## HDFS

HDFS uses distributed storage. Large files can be divided into blocks and distributed across DataNodes.

Important ideas:

- Distributed storage
- Block-based files
- Metadata management
- Replication for fault tolerance

## MapReduce Example

Input:

```text
AI data
AI model
data science
```

Mapper output:

```text
(AI, 1)
(data, 1)
(AI, 1)
(model, 1)
(data, 1)
(science, 1)
```

Reducer output:

```text
AI      → 2
data    → 2
model   → 1
science → 1
```

## YARN

YARN separates resource management from application execution. Understand its role in scheduling and managing cluster resources.

## Exercise

Write pseudocode for MapReduce word count and identify mapper output and reducer input.
