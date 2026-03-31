# Vector Index Optimization Guide

Optimize your vector search performance by choosing the right index strategy for your dataset size and requirements.

---

## Vector Index Strategy

Your choice of index determines the needs of RAM, operational cost and the retrieval latency of your cluster.

| **Index Type** | **Production Use Case** | Size | **Retrieval Speed** |
| --- | --- | --- | --- |
| **HNSW** | **High Performance (Production Recommended)** | Optimized for Large datasets | **Fastest** |
| **Flat** | **Memory Saver** | Best for small datasets only. Performs brute-force linear scans; uses zero graph memory. | **Good** |
| **Dynamic** | Balanced | Starts as **Flat** for efficiency, auto-upgrades to **HNSW** at a threshold (Default: 10,000). | **Adaptive** |

> **Dynamic Indexing** requires `ASYNC_INDEXING=true` in your environment. This is a **one-way switch**; once a shard converts to HNSW, it will not revert to Flat even if the object count drops.
> 

---

## Critical Environment Configuration

| Category | Variable | Optimization |
| --- | --- | --- |
| Persistence | `PERSISTENCE_HNSW_MAX_LOG_SIZE` | Set it close to your HNSW graph size (e.g. 1 GiB for a ~1 GiB graph) to speed up compaction. Note: This increases memory usage. |
| Deletions | `TOMBSTONE_DELETION_CONCURRENCY` | Default is already half your CPU cores. In large-core clusters, consider setting lower to prevent cleanup from consuming too many resources. For small-core clusters with heavy deletions, increase to speed up cleanup. |
| Deletions | `TOMBSTONE_DELETION_MIN_PER_CYCLE` | For very large indexes, set to **100000** (100k) to ensure cleanup happens before search speed degrades. |
| Deletions | `TOMBSTONE_DELETION_MAX_PER_CYCLE` | For very large indexes, set to 10000000 (10 million) to cap the number of tombstones deleted per cycle and prevent resource overconsumption. |
| Global Defaults | `DEFAULT_QUANTIZATION` | Set to RQ to ensure all new collections use 8-bit compression automatically. |

Tombstones are markers for deleted objects in the HNSW index. They get cleaned up periodically (controlled by `cleanupIntervalSeconds`).

---

## The HNSW Tuning

Tuning HNSW is a balance between graph density (Recall) and traversal speed (Latency). The following are **starting points** and should be validated per dataset.

### ✅ The Production DOs

- `Set ef: -1`: Enables Dynamic ef. This allows Weaviate to auto-tune search depth based on your query limit.
    - For predictable recall requirements where you need static performance, set `ef` between `300–500` (test your specific dataset to find optimal value).
- **Optimize `maxConnections`**: Reduce from 64 to 32 as a good default; increase only if you need higher recall and can afford extra memory. This provides significant RAM savings with minimal recall loss and often better QPS/recall performance.
- Bulk Import Performance: Use Async Indexing (`ASYNC_INDEXING=true`) to prevent graph construction from blocking data ingestion.

### ❌ The Production DON'Ts

- DON'T exceed `ef: 512` Causes massive latency penalties for negligible recall gains.

---

## High-Efficiency Compression

For production, **Rotational Quantization (RQ-8)** is the standard for compression.

- **RQ (Recommended):** Provides **98-99% recall** with a 4x reduction in vector RAM. It requires **no training phase,** compression is instant.
- **PQ (Large Scale):** Use only for massive datasets (>1M) where custom segment tuning is needed. Requires **10k–100k objects** per shard for training before it activates.

---

## Availability & Restart Optimization

In production, rolling updates can cause search latency spikes if the new Pod hasn't finished loading its cache. Use these settings to ensure a Pod is only "Ready" once it's fully performant.

| **Environment Variable** | **Recommended Value** | **Why it's Critical** |
| --- | --- | --- |
| `HNSW_STARTUP_WAIT_FOR_VECTOR_CACHE` | Default behavior | In `v1.36.6+`, default behavior is optimized by Core and can be adjusted automatically when lazy shard loading is enabled for a collection. |
| `PERSISTENCE_HNSW_DISABLE_SNAPSHOTS` | `false` | Snapshots capture a point-in-time state of the HNSW index to drastically reduce startup times. Instead of replaying the full commit log, Weaviate loads the snapshot and only replays the **delta** (changes since the last snapshot) |

> Why this matters: A pod that is "up" but hasn't loaded its HNSW graph, leading massive latency spikes during restarts. There are two complementary mechanisms for restart optimization: cache warming and HNSW Snapshots.
> 
- Snapshots trigger **on startup** or **periodically** based on configured intervals.
- A 10M object index drops from **70+ seconds → ~5 seconds** startup (~10–15x faster).
- If a snapshot fails to load, Weaviate **safely falls back** to full commit log replay.

---

## Developer Checklist

**Environment & Infrastructure:**

- [ ]  **For Availability:** From `v1.36.6+` Core auto-handles lazy shard loading per collection.
- [ ]  **Persistence**: `PERSISTENCE_HNSW_MAX_LOG_SIZE=1024MiB` (or match HNSW graph size; adjust based on dataset).
- [ ]  **Global Defaults:** `DEFAULT_QUANTIZATION RQ` (applies RQ compression to all new collections).
- [ ]  **Snapshots**: v1.36+ enabled by default. `PERSISTENCE_HNSW_DISABLE_SNAPSHOTS=false`

HNSW Configuration:

- [ ]  ef is set to -1 for dynamic optimization (or 300-500 for static predictable recall).
- [ ]  maxConnections=32 (reduced from 64 for modern high-dimensional vectors).
- [ ]  Never set ef > 512 (causes massive latency penalties).

Compression & Memory:

- [ ]  **Compression**: RQ is enabled for RAM efficiency (98-99% recall, 4x reduction).
- [ ]  **Memory**: Vector cache is sized to fit the "hot" portion of the dataset.

Deletions & Cleanup:

- [ ]  **Deletions**: `TOMBSTONE_DELETION_CONCURRENCY` at default (already half CPU cores) or lower for large clusters.
- [ ]  For Large Datasets, configure `TOMBSTONE_DELETION_MIN_PER_CYCLE` and `TOMBSTONE_DELETION_MAX_PER_CYCLE`.
