# 🚀 Batching Optimization Guide

Production-focused checklist for ingesting **5M–100M** objects. Assumes a **3+ node** cluster.

## 1. Optimization Checklist
- Connectivity: Prefer **gRPC (50051)**; REST is a bottleneck at this scale.
- Sharding: Set `desired_count` up-front (e.g., **6 shards on 3 nodes**) to parallelize CPUs and allow future node growth without re-import.
- Quantization: Enable **rotational quantization (RQ)** to cut RAM, costs, and improve query throughput.
- Batch mode: Use `collection.batch.fixed_size()` for high-volume imports.
- Vectors: **Pre-compute vectors** to avoid embedding latency during the import loop.
- Error handling: After the batch context closes, inspect `collection.batch.failed_objects` to capture per-object failures.

## 2. Infrastructure
- **Over-sharding:** 6 shards on 3 nodes = better CPU saturation now, zero-migration expansion to 6 nodes later.
- **Multi-tenancy:** In MT, **1 tenant = 1 shard**; Weaviate auto-distributes shards. You typically **do not** set `desired_count` manually for MT.

## 3. Decision Tree — “Is Import Taking Too Long?”
- **Weaviate CPU > 80%:** Cluster is saturated → **Scale up**.
- **Embedding is slow:** External API wait → raise `concurrent_requests`, use `.rate_limit()`, or **pre-compute vectors**.
- **Network latency high:** Increase `concurrent_requests` to keep gRPC pipeline full.
- **Weaviate CPU < 50%:** Raise `concurrent_requests` (6 → 8 → 12). If still slow, raise `batch_size` (up to ~500–1000).

## 4. Recommended Batch Template
```python
try:
    with collection.batch.fixed_size(batch_size=500, concurrent_requests=4) as batch:
        for row in data_generator:
            batch.add_object(
                properties=row["props"],
                vector=row["vector"],
            )

    failed = collection.batch.failed_objects
    if failed:
        print(f"Failed count: {len(failed)}")
        for i, err in enumerate(failed[:5], 1):
            print(f"Error {i}: {err.message}")
except Exception as e:
    print(f"Critical System Error: {e}")
```

## 5. Troubleshooting Cheat Sheet
| Situation | Diagnosis | Fix |
| --- | --- | --- |
| Deadline exceeded (gRPC) | Batch payload too heavy | Lower `batch_size` (try 50) |
| OOM / memory errors | Indexing exceeds RAM | Lower `batch_size`; ensure **RQ compression** enabled |
| Integration model errors | Hitting API rate limits | Use `collection.batch.rate_limit(rpm=X)` |
| Slow + low CPU | Client/network bottleneck | Increase `concurrent_requests` (8–12) |
