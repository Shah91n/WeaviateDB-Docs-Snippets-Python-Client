# Sharding Optimization Guide

This guide is designed for developers building Weaviate schema. It focuses on the architectural logic of sharding.

---

## 1. Core Concepts: Sharding vs. Replication

Understanding the difference is critical for a healthy cluster. While both distribute data, they serve different masters:

- **Sharding (Efficiency):** Splits your data into pieces across nodes. This allows you to use the combined **memory** and CPU of multiple nodes.
- **Replication (Availability):** Creates identical copies of those shards. If one node fails, another has the data. The default replication factor is **1**, but you can enforce a minimum replication factor (for example, 3 for high availability) by setting the **`REPLICATION_MINIMUM_FACTOR`** environment variable.

---

## 2. The "Immutable" Rules

In Weaviate, some schema decisions are permanent. Once a collection is created, you **cannot** change the following:

- **The Shard Count (`desiredCount`):** Re-sharding is **not supported yet**, so you cannot change shard count after collection creation. If you start with 3 shards and later need more, you must create a new collection and re-import your data.

> **Developer Tip:** Always plan shard count based on expected peak node count, not just your starting size.

---

## 3. Smart Default Behavior

By default, Weaviate tries to be helpful. When you create a collection without specific sharding instructions:

1. It counts the number of nodes currently in your cluster.
2. It sets **Shard Count** equal to that node count.
3. It assigns virtual shards per physical shard to keep distribution even.

---

## 4. Startup and Lazy Shard Loading (v1.36.6+)

From **v1.36.6+**, Weaviate auto-detects shard loading mode per collection at startup.

- Shards are eagerly loaded by default until a collection crosses one threshold.
- Thresholds:
  - **`LAZY_LOAD_SHARD_COUNT_THRESHOLD`** (default: `1000` tenants)
  - **`LAZY_LOAD_SHARD_SIZE_THRESHOLD_GB`** (default: `100` GB total shard size)
- Once either threshold is crossed, that collection flips to lazy loading automatically.
- `HNSW_STARTUP_WAIT_FOR_VECTOR_CACHE` defaults to `true`

---

## 5. Optimization and Resource Management

### The Disk vs. Memory Gap

There is a specific path in how Weaviate places data:

- **Placement Logic:**: Weaviate uses a disk-aware round-robin approach. It sorts nodes by most free disk space first, then distributes shards one-by-one across that list.

- **The Reality:** It’s a fair spread, not a "fill the emptiest node" policy. This is why shards don't automatically jump to a brand-new, empty node.

### Handling High Memory Pressure (Shards)

When a node runs low on resources, Weaviate takes protective measures:

- **Read-Only Mode:** Shards on that node can be flipped to read-only to prevent crashes. This can be triggered by high disk usage or high memory usage.

---

## 6. Manual Rebalancing

If your cluster becomes unbalanced (for example, some nodes are overloaded while others are idle), you can manually move data.

- **Execute Movement:** You can move or copy a specific shard replica from a **Source Node** to a **Target Node** only if **`REPLICA_MOVEMENT_ENABLED=true`** is set.
- Without that flag, replica movement endpoints return HTTP `501 Not Implemented`.

---

## 7. Best Practices Checklist

- [ ] **Set shard count early:** Match it to your intended cluster scale.
- [ ] **Monitor node distribution:** Use Nodes API verbose output to check `ShardCount` and `ObjectCount` per physical node.
- [ ] **Check disk and RAM:** Do not watch only disk. Ensure RAM headroom for vectors on hosted shards.
- [ ] **Use Core startup defaults on v1.36.6+:** Avoid manual lazy-load toggles unless explicitly required for testing.
