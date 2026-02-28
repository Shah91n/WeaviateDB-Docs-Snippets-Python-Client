# Weaviate Python Client Snippets & Optimization Guides

A comprehensive collection of production-ready code snippets, scripts, and optimization guides for working with Weaviate Vector Database using the Python client.

## 📂 Project Structure

### 🔗 **Connection Scripts** (`Connection_Scripts/`)
Establish and manage connections to Weaviate instances:
- `Connection_Methods.ipynb` - Multiple ways to connect to Weaviate
- `Connection_Tests_Script.ipynb` - Test and validate your connections
- `Weaviate_Connection_Manager_Singleton_Pattern.py` - Production-ready connection pooling with singleton pattern

### 📋 **Migration Scripts** (`Migration_Scripts/`)
Migrate data and collections between Weaviate instances:
- `collections_to_tenants_migration.ipynb` - Migrate multiple collections to a multi-tenant architecture
- `general_migration.ipynb` - General-purpose migration workflows

### ✂️ **Chunking Scripts** (`Chunking_Scripts/`)
Prepare text data for vectorization:
- `Recursive_chunk.py` - Recursive text chunking for optimal embedding windows

### 📚 **General Scripts** (`General_Scripts/`)
Essential utilities for schema management and database operations:
- `CreateCollectionViaBatchingFromFile.py` - Efficient bulk collection creation from file sources
- `DumpSchemaFromSourceEndpointStepOne.py` - Export schema from a Weaviate instance (Step 1 of replication)
- `DumpSchemaToNewEndpointStepTwo.py` - Import schema to a target Weaviate instance (Step 2 of replication)
- `Health_Checks.ipynb` - Monitor cluster health and connectivity
- `Read_Repair_Consistency.ipynb` - Trigger read repair operations for consistency

### 🚀 **Weaviate Operations** (`Weaviate_Operations/`)

#### Core Data Operations (CRUD)
Located in `CRUD/` subdirectory with complete examples:
- `create.ipynb` - Create objects in collections
- `read.ipynb` - Read and retrieve objects
- `update.ipynb` - Update existing objects
- `delete.ipynb` - Delete objects
- `general_queries.ipynb` - General query patterns

#### Search & Retrieval
Multiple search strategies with working examples:
- `vector_search.ipynb` - Pure vector/semantic search
- `keywords_search.ipynb` - BM25 keyword search
- `hybrid_search.ipynb` - Combined vector + keyword search
- `generative_search.ipynb` - Search with generative infill (RAG patterns)

#### Advanced Features
Production-ready implementations of Weaviate's advanced capabilities:
- `Agents.ipynb` - Agent-based automation and reasoning
- `Aggregation.ipynb` - Metrics and analytics aggregations
- `Backups.ipynb` - Backup and disaster recovery workflows
- `Bring_Your_Own_Vector.ipynb` - Custom vector imports and management
- `Cross_Reference.ipynb` - Define and query cross-references between collections
- `GraphQL.ipynb` - GraphQL query patterns and examples
- `RESTAPIs.ipynb` - Direct REST API examples
- `RoleBasedAccessControl.ipynb` - RBAC implementation and authorization
- `Shards.ipynb` - Shard management and configuration
- `Batching.ipynb` - High-performance batch ingestion patterns
- `Cluster.ipynb` - Multi-node cluster operations
- `Multi_Tenancy.ipynb` - Multi-tenant architecture and operations
- `Named_Vectors.ipynb` - Named vector fields and multi-vector storage

## 📚 Optimization Guides

Comprehensive guides for optimizing Weaviate deployments:

| Guide | Focus Area | Key Topics |
|-------|-----------|-----------|
| [**Inverted Index Optimization**](./Optimization_Guides/Inverted_Index.md) | Text Search | Tokenization, index types, BM25 configuration |
| [**Vector Index Optimization**](./Optimization_Guides/Vector_Index.md) | Vector Search | HNSW tuning, compression (RQ), dynamic indexing |
| [**Batching Optimization**](./Optimization_Guides/Batching.md) | Data Ingestion | Production patterns for 5M–100M object imports |
| [**Query Agent Optimization**](./Optimization_Guides/Query_Agent.md) | Query Performance | Schema design, property management, large collections |
| [**Multi-Tenancy Optimization**](./Optimization_Guides/Multi_Tenancy.md) | Architecture | Tenant state management, scaling to millions of tenants |

## 📖 Documentation Structure

- **Notebooks (.ipynb)**: Interactive examples with explanations and output
- **Python Scripts (.py)**: Production-ready utilities and tools
- **Markdown Guides (.md)**: Detailed optimization and best practices documentation

## 💡 Tips

- Check the [Optimization Guides](./Optimization_Guides/README.md) for architecture decisions

## 🤝 Contributing

We welcome contributions! If you have improvements, new examples, or bug fixes:

1. Create a feature branch
2. Make your changes
3. Submit a pull request with a clear description

## 📄 License

This repository is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.