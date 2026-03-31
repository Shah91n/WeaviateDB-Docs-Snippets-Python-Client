# Memory Optimization & Scaling Guide

This guide provides practical strategies for optimizing memory usage and scaling Weaviate deployments. In most vector systems, memory is the primary cost driver and a key performance bottleneck.

---

## Weaviate's Memory Architecture

Weaviate uses two distinct memory spaces. Total Pod/container memory is the sum of these spaces plus runtime overhead.

| **Space** | **Components** |
| --- | --- |
| **Go Heap** | HNSW graph connections, vector cache, compressed vectors |
| **Off-Heap** | Memory-mapped (mmap) LSM segments, goroutine stacks, GC metadata |

> **The 1.5x Rule:** Container memory typically runs at about **1.5x Go heap in-use**. The OS needs additional space for page cache (off-heap) to maintain high-speed data retrieval.

---

## Core Memory Components

### 1. HNSW Graph Structure

Memory usage is dominated by Layer 0 connections (about 100% of nodes).

- **Formula:** `bytes_per_conn = 2-5 bytes` (variable encoding based on index size)
- **Optimization:** Reducing `maxConnections` can significantly lower RAM usage, with a possible small reduction in recall.

### 2. Vector Cache

Vectors are cached as `float32` values (4 bytes per dimension).

- **Formula:**
  - `Cache Memory = cached_vectors × (dimensions × 4 + 30) bytes`
- **Optimization:** Use `vectorCacheMaxObjects` to prevent unbounded cache growth.
  - Frequently queried vectors should remain in memory for consistent low-latency lookups.

### 3. Object Data (LSM Segments)

Object data resides in mmap'd segments off-heap. Files larger than 8 KB are memory-mapped. Segments at or below 8 KB are read into Go heap memory.

---

## Sizing & Requirement Calculation

Follow these steps to estimate production memory requirements:

1. **Calculate Go Heap:** `(HNSW + Vector Cache + 2 GB buffer)`.
2. **Set GOMEMLIMIT:** `Total Heap × 1.2` (adds 20% headroom under load).
3. **Set Container Limit:** `GOMEMLIMIT / 0.8` (Weaviate maps GOMEMLIMIT to 80% of container memory).

### Example: 10M Vectors (1536 Dimensions)

- **Go Heap:** about 68 GB.
- **GOMEMLIMIT:** 82 GB.
- **Container Limit:** `82 / 0.8 = about 103 GB`.
- **Expected Runtime Usage:** about 102 GB (aligned with the 1.5x rule).

---

## Scaling Triggers & Growth Management

As vector count grows, Go heap usage increases. Because of the **1.5x rule**, a 10 GB heap increase often requires about 15 GB additional container RAM to preserve performance.

- **80% Threshold:** If `go_memstats_heap_inuse_bytes` stays above 80% of `GOMEMLIMIT`, scale vertically or shard horizontally.
  - Horizontal scaling guidance: shard across nodes only when your design supports it (for example, `desiredCount=3` with `RF=3`), since rebalancing may occur.
- **Performance Degradation:** If heap usage approaches the limit, GC runs more frequently (CPU spikes), and the OS may evict off-heap page cache, which increases query latency.
- **Scaling Lead Time:** Scale before the limit is reached. For example, when planning growth from 10M to 15M vectors, estimate future heap and increase container memory by about 1.5x the projected heap increase.

---

## Optimization Strategies (Day-One and Ongoing)

- **Strategy 1: Reduce Graph Size:** Lower `maxConnections` to reduce HNSW graph RAM.
- **Strategy 2: Enable Compression:** Use PQ, SQ, BQ, or RQ to reduce vector memory footprint.
- **Strategy 3: Limit Cache:** Set `vectorCacheMaxObjects` intentionally, based on your hot data set.
- **Strategy 4: Set GOMEMLIMIT Correctly:** Set `GOMEMLIMIT` to about 80% of the container memory limit to avoid aggressive GC behavior and OOM risk.

---

## Developer Checklist

### Memory Sizing & Configuration

- [ ] **GOMEMLIMIT:** Set to 80% of total container memory to reduce OOM risk while preserving runtime overhead.
- [ ] **1.5x Rule Alignment:** Confirm container limits include the multiplier for OS page cache.
- [ ] **Vector Cache:** Explicitly set `vectorCacheMaxObjects` instead of relying on the default (`1e12`, effectively unlimited for most deployments).
- [ ] **Vertical Scaling Buffer:** Define a scale-up trigger (for example, heap in-use > 80% of `GOMEMLIMIT`) to keep enough operational lead time.

### Index Efficiency

- [ ] **HNSW `maxConnections`** is tuned to your recall vs. memory target.
- [ ] **Compression Strategy** (PQ/SQ/BQ/RQ) is selected and validated for your workload.

### Monitoring & Metrics

- [ ] **Heap Tracking:** Monitor `go_memstats_heap_inuse_bytes` as the primary active-memory baseline.
- [ ] **Off-Heap Approximation:** Track `container.memory.usage - go_memstats_heap_inuse_bytes` to monitor page cache health.

---

## Memory Calculator

You can also use this calculator for memory and CPU sizing: Weaviate-Memory-CPU-Calculator: https://github.com/Shah91n/Weaviate-Memory-CPU-Calculator
