# Backend Architecture Notes

# What Backend Systems Actually Are

Backend systems are fundamentally:
data + computation + networking systems.

Not just APIs.

---

# Archon Architecture

Repository
    ↓
Ingestion
    ↓
AST Parsing
    ↓
Graph Construction
    ↓
Embeddings
    ↓
Hybrid Retrieval
    ↓
LLM Context Assembly

---

# Why Multiple Databases Exist

Different data shapes require different storage systems.

---

# Relational Data

Best for:
- metadata
- structured records
- transactions

Stored in:
PostgreSQL

---

# Graph Data

Best for:
- dependencies
- relationships
- traversals

Stored in:
Neo4j

---

# Vector Data

Best for:
- semantic similarity
- embeddings
- retrieval

Stored in:
pgvector

---

# Metadata

Data ABOUT data.

Example:
- repository name
- file path
- line count
- indexed timestamp

---

# Why Neo4j Fits Archon

Repositories naturally form graphs.

Examples:

File → IMPORTS → File
Function → CALLS → Function

Graph databases optimize:
- traversals
- relationships
- dependency walking

---

# Polyglot Persistence

Using multiple databases for different workloads.

Very common in modern systems.

Examples:
- Redis for cache
- Postgres for metadata
- Neo4j for graphs
- S3 for files

---

# Service Architecture

Archon currently has:
- API service
- Postgres service
- Neo4j service

These are independent distributed services.

---

# Infrastructure Concepts

## Orchestration

Managing multiple cooperating services.

---

## Service Discovery

Services finding each other over network.

---

## Persistence

Durable storage surviving container deletion.

---

# Important Engineering Insight

Good architecture often means:
store each data type in system best suited for it.

Not:
force everything into one technology.

---

# Backend Debugging Mindset

Always identify:
- build-time vs runtime error
- networking vs filesystem issue
- app vs infrastructure failure

Systematic debugging is critical backend skill.
