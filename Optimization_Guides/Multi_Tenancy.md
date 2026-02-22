# Multi-Tenancy Optimization Guide

A guide for architecting, configuring, and operating multi-tenant collections in Weaviate from initial setup through long-term resource management.

---

## 1. When to Use Multi-Tenancy

Use **multi-tenancy** when your use case fits the following criteria. Multi-Tenancy is the right choice when:

| Condition | Why It Matters |
| --- | --- |
| All tenants share the **same schema & configuration** | One schema, maintained once, benefits all |
| You **don't need cross-tenant queries** | Each tenant is fully isolated by design |
| You need to support **many tenants** (up to millions) | One shard per tenant scales efficiently |
| You anticipate **>100 datasets or e.g. clients** | Below this threshold, separate collections is efficient as well. |

### Key Concepts

- **Each tenant = its own shard.** Tenants are physically and logically isolated from one another.
- **Deleting a tenant deletes all of its data.** This makes compliance (e.g., GDPR right-to-erasure) straightforward, no complex data scrubbing required.

### ⚖️ Multi-Tenancy vs. Many Collections

| Factor | Multi-Tenancy | Many Collections |
| --- | --- | --- |
| Index overhead | Lower | Higher |
| Resource efficiency | Better | Less efficient |
| Schema evolution | Change once, all tenants benefit | Must update each collection |
| Isolation | Native | Requires careful separation |
| Scale up/down ease | Built-in via tenant states | Less efficient |

---

## 2. Tenant State Management

Tenant states are your primary lever for balancing **cost vs. performance**. Think of it as "temperature management": keep hot data accessible and archive cold data cheaply.

### State Overview

| State | Storage Location | Queries / CRUD | Reactivation Speed |
| --- | --- | --- | --- |
| `ACTIVE` | RAM / Hot Resources | ✅ Allowed | (Already Active) |
| `INACTIVE` | Local Disk (Warm) | ❌ Not allowed | ⚡ Fast |
| `OFFLOADED` | Cloud Storage (Cold) | ❌ Not allowed | 🐢 Slower |

### Recommended Strategy

```
Frequently accessed   →  ACTIVE      (fast queries, higher RAM cost)
Less active           →  INACTIVE    (local disk, lower RAM use)
Long-tail / archived  →  OFFLOADED   (cloud, lowest cost, slowest reactivation)
```

### ⚠️ Important Behaviors

- Tenant states are **eventually consistent** across nodes. Expect small delays between when you change a state and when data becomes available or unavailable.
- Offloading requires the **offload module** to be configured in your environment.

---

## 3. Backups & Data Safety

### ⚠️ Critical Limitation

**Backups only include `ACTIVE` tenants.** Tenants in `INACTIVE` or `OFFLOADED` states are excluded from backup snapshots.

### Best Practices

- **Before any scheduled backup**, activate tenants whose data must be preserved.
- **Document which tenants were active** at the time of each backup. This is critical for recovery planning.

---

## 4. Access Control & Security

Multi-tenancy provides **data isolation at the storage and query level**, but it does not replace authentication and authorization. You still need a proper auth layer on top.

### What Multi-Tenancy Gives You

- Physical shard-level isolation between tenants
- Fast tenant-level deletes (GDPR-friendly)

### What You Still Need to Build

Use **RBAC or admin-list authorization** to control who can:

- Read or write data within a specific collection
- Manage tenants (create, update states, delete)
- Access tenant metadata

---

## 5. Availability & Restart Optimization

### Environment Variables

| Variable | Recommended Value | Why It Matters |
| --- | --- | --- |
| `DISABLE_LAZY_LOAD_SHARDS` | `false` for multi-tenant | Keeps startup fast by loading shards on demand. |

---

## 6. Recommended Vector Index Configuration with Multi-Tenancy

For multi-tenant collections, use the **dynamic vector index**. It starts as `flat` (disk-based) and automatically upgrades to `hnsw` once a tenant's shard crosses a size threshold (default: 10,000 objects).

| Index Type | Best For | Memory | Speed |
| --- | --- | --- | --- |
| **Flat** | Small tenants | Very low | Good |
| **HNSW** | Large tenants | Higher | Fastest |
| **Dynamic** *(recommended)* | Depends on threshold | Adaptive | Adaptive |

### Why Dynamic Works Well Here

- **Small tenants** get a `flat` index on disk, low memory footprint with acceptable query performance.
- **Large tenants** automatically graduate to `HNSW`, enabling fast approximate nearest neighbor search with optional quantization (RQ recommended for ~98–99% recall).

> **Prerequisite:** Dynamic indexing requires `ASYNC_INDEXING=true` in your environment. Note: this is a one-way switch per shard. Once converted to HNSW, a shard will not revert to flat.

### Compression Recommendation

Apply **RQ compression** (Rotational Quantization) to large tenants:
- **RAM reduction**: ~4x improvement
- **Recall**: 98–99% with 8-bit compression
- **Query performance**: Often improves due to reduced memory pressure

---

## 7. How to Enable Multi-Tenancy

### Step 1 — Create the collection with multi-tenancy enabled

```python
from weaviate.classes.config import Configure

multi_collection = client.collections.create(
    name="MultiTenancyCollection",
    multi_tenancy_config=Configure.multi_tenancy(enabled=True)
)
```

### Step 2 — Add tenants

```python
from weaviate.classes.tenants import Tenant

mt_collection = client.collections.use("MultiTenancyCollection")

mt_collection.tenants.create(
    tenants=[
        Tenant(name="tenant1"),
        Tenant(name="tenant2"),
    ]
)
```

---

## 8. Production Checklist

### ✅ Production Do's

| # | Recommendation |
| --- | --- |
| 1 | Use **dynamic vector index** for all multi-tenant collections |
| 2 | Apply **RQ compression** (98–99% recall, 4x RAM reduction) |
| 3 | Keep `DISABLE_LAZY_LOAD_SHARDS=false` for multi-tenant deployments |
| 4 | Activate tenants before scheduled backups if their data must be included |
| 5 | Use RBAC to enforce tenant-level access control in your auth layer |
| 6 | Move less-active / idle tenants to `INACTIVE` or `OFFLOADED` to reduce RAM |
| 7 | Document tenant state transitions and backup coverage for disaster recovery |
| 8 | Monitor tenant state consistency across nodes during large-scale state transitions |

### ❌ Production Don'ts

| # | Pitfall | Why It's Dangerous |
| --- | --- | --- |
| 1 | **Don't set `DISABLE_LAZY_LOAD_SHARDS=true`** for multi-tenant | Causes extremely slow startup times when thousands (millions) of shards must be loaded. |
| 2 | **Don't assume backups cover all tenants** | Only `ACTIVE` tenants are backed up — `INACTIVE` and `OFFLOADED` are silently excluded |
| 3 | **Don't skip tenant state policies** | Without lifecycle management, all tenants default to `ACTIVE`, consuming full RAM indefinitely |
| 4 | **Don't skip auth** | Storage isolation alone is not access control — always layer RBAC on top |
| 5 | **Don't cross-query tenants** | Multi-tenancy is designed for isolation; cross-tenant queries defeat the purpose and violate isolation guarantees |

---

## 9. Key Takeaways

✨ **Multi-tenancy shines when:**
- You manage 100+ logical datasets with identical schemas
- Tenants are isolated
- Cost and RAM efficiency are critical
- GDPR compliance is a priority (fast, complete tenant deletion)

⚠️ **Multi-tenancy is not ideal if:**
- Tenants need different schemas
- You're managing < 100 datasets (separate collections is simpler)

🎯 **Always remember:**
- State management (ACTIVE/INACTIVE/OFFLOADED) is your cost lever
- Backups only cover ACTIVE tenants
- Combine multi-tenancy with proper RBAC for complete security
