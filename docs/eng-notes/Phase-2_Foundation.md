# Archon — Phase 2 Notes (Part 1)

# Neo4j Graph Infrastructure Foundation

---

# 1. What Is Archon?

Archon is a:

> Repository Architecture Intelligence Platform

Goal:

Understand repositories semantically instead of just reading files like text.

---

# Traditional View of Repository

Most people think repositories are:

```text
repo/
  app/
    api.py
    db.py
```

But this is only a filesystem view.

This does NOT tell:

* architecture
* dependencies
* relationships
* execution flow

---

# Real Architecture View

Repositories are actually:

```text
Function A → calls → Function B

File A → imports → File B

Service → depends on → Database
```

Repositories are:

# networks of relationships

This is why graphs are useful.

---

# 2. What Did We Build in Phase 1?

Phase 1 extracted repository semantics.

Pipeline:

```text
GitHub Repo
    ↓
Clone Repository
    ↓
Filesystem Traversal
    ↓
AST Parsing
    ↓
Semantic Extraction
```

We extracted:

```python
{
    "file": "...",
    "imports": [...],
    "functions": [...],
    "calls": [...]
}
```

This is called:

# structured semantic representation

---

# Important Idea

We are NOT storing raw text.

We are storing:

* structure
* relationships
* semantics

This is what code intelligence systems do.

---

# 3. Why Phase 2 Exists

Phase 1 gave isolated facts.

Example:

```text
Function create_user exists
```

But isolated facts are not enough.

We need:

```text
create_user() CALLS validate_user()
```

Relationships create intelligence.

---

# Phase 2 Goal

Convert parsed semantics into:

# Knowledge Graph

---

# 4. What Is a Knowledge Graph?

A graph contains:

* nodes
* relationships (edges)

Example:

```text
(File)-[:IMPORTS]->(File)

(Function)-[:CALLS]->(Function)
```

This models relationships naturally.

---

# Why Graphs Matter

Graphs are excellent for:

* dependency analysis
* architecture traversal
* relationship reasoning
* shortest paths
* connected systems

Repositories are naturally graph-shaped.

---

# 5. Why Not Just Use PostgreSQL?

Important backend engineering question.

---

# Relational Databases

SQL databases are good for:

```text
Users
Orders
Payments
```

Tabular business data.

---

# Problem

Repository intelligence needs:

```text
Find all functions reachable from API route X
```

This requires:

* recursive traversal
* relationship exploration

SQL joins become complicated and slow.

---

# Graph Databases Solve This Naturally

Graphs specialize in:

# traversing relationships

This is why we use Neo4j.

---

# 6. What Is Neo4j?

Neo4j is:

# graph database

It stores:

* nodes
* edges
* properties

instead of rows/tables.

---

# Example Node

```text
(:File {
    path: "app/api.py"
})
```

---

# Example Relationship

```text
(:File)-[:IMPORTS]->(:File)
```

---

# Example Graph

```text
(File)-[:DEFINES]->(Function)

(Function)-[:CALLS]->(Function)
```

---

# 7. Neo4j Core Concepts

---

# Node

Represents an entity.

Examples:

* Repository
* File
* Function

---

# Relationship

Represents connection.

Examples:

* IMPORTS
* CALLS
* DEFINES

---

# Property

Metadata attached to nodes.

Example:

```text
path = "app/api.py"
```

---

# Label

Category/type of node.

Examples:

```text
:Repository
:File
:Function
```

---

# 8. Why Graphs Fit Repositories Perfectly

Repositories are already:

```text
connected systems
```

Examples:

```text
File A imports File B

Function X calls Function Y
```

Graphs model this naturally.

---

# 9. Our Graph Schema (Current)

Current architecture:

```text
(:Repository)
```

Soon:

```text
(:Repository)-[:CONTAINS]->(:File)

(:File)-[:DEFINES]->(:Function)

(:Function)-[:CALLS]->(:Function)
```

---

# 10. Why We Started Small

Very important engineering principle:

# avoid overengineering

We intentionally did NOT model:

* classes
* inheritance
* decorators
* frameworks
* APIs
* runtime traces

Why?

Because early systems should optimize for:

* correctness
* iteration speed
* simplicity

---

# 11. Backend Architecture We Built

Current architecture:

```text
FastAPI
    ↓
Graph Service
    ↓
Neo4j Driver
    ↓
Bolt Protocol
    ↓
Neo4j Database
```

---

# 12. What Is a Database Driver?

A driver is:

# communication library

It allows Python to speak to database.

Examples:

* PostgreSQL → psycopg
* MongoDB → pymongo
* Neo4j → neo4j driver

---

# Driver Responsibilities

* networking
* authentication
* connection pooling
* query execution
* retries
* result streaming

---

# 13. What Is Bolt Protocol?

Neo4j communicates using:

# Bolt protocol

Port:

```text
7687
```

Bolt is:

* binary
* fast
* optimized for graph queries

---

# Why Not HTTP?

Bolt is:

* faster
* lower overhead
* persistent
* optimized for Cypher

---

# 14. Docker Networking Concept

Important concept:

Inside containers:

```text
localhost != host machine
```

This confuses beginners a lot.

---

# In Docker Compose

Service names become hostnames.

Example:

```yaml
services:
  api:
  neo4j:
```

Then inside backend container:

```text
neo4j
```

becomes hostname for Neo4j container.

---

# Correct URI

```text
bolt://neo4j:7687
```

NOT localhost.

---

# 15. Why `.env` Exists

`.env` stores:

# runtime configuration

Examples:

* passwords
* URLs
* secrets

---

# Why Not Hardcode?

Bad:

```python
password = "123"
```

Problems:

* insecure
* hard to deploy
* environment-specific

---

# Good Practice

```env
NEO4J_URI=bolt://neo4j:7687
```

This separates:

* code
* infrastructure config

---

# 16. Why `pydantic-settings` Exists

Modern FastAPI uses:

```python
from pydantic_settings import BaseSettings
```

Purpose:

* load env variables
* validate config
* provide type safety

---

# Why Type Safety Matters

Bad:

```python
PORT = os.getenv("PORT")
```

Everything becomes string.

Good:

```python
PORT: int
```

Pydantic validates automatically.

---

# 17. Configuration Architecture

We created:

```text
app/config.py
```

Purpose:

# centralized configuration layer

This becomes:

* single source of truth
* reusable
* scalable

---

# 18. Why Centralized Config Matters

Without centralized config:

```text
password duplicated everywhere
```

This becomes maintenance nightmare.

---

# 19. Neo4j Driver Layer

We created:

```text
app/db/neo4j.py
```

Purpose:

* driver lifecycle management
* session creation
* centralized DB access

---

# Why Separate DB Layer?

Very important architecture principle.

Parser should NOT know:

* Neo4j
* database details
* Cypher

Parser responsibility:

```text
extract semantics
```

DB responsibility:

```text
persist graph
```

---

# 20. Driver vs Session vs Transaction

Important Neo4j concepts.

---

# Driver

Top-level infrastructure object.

Handles:

* connection pool
* networking
* auth

Usually shared globally.

---

# Session

Lightweight interaction context.

Created frequently.

---

# Transaction

Atomic unit of work.

Example:

```text
create nodes
create relationships
```

All succeed OR rollback.

---

# Hierarchy

```text
Driver
   ↓
Session
   ↓
Transaction
```

---

# 21. Why We Reuse Driver

Creating connections repeatedly is expensive.

Driver creation may involve:

* TCP connection
* authentication
* pool creation

So backend systems:

* create one driver
* reuse globally

---

# 22. What Is Connection Pooling?

Connection pool:

# reusable connection manager

Instead of:

```text
open new connection every query
```

Pool reuses existing connections.

Benefits:

* lower latency
* better scalability
* less overhead

---

# 23. Important Python Import Lesson

We hit:

```text
ModuleNotFoundError
```

Reason:

* Python execution context issue

---

# Wrong Way

```bash
python scripts/test.py
```

---

# Correct Professional Way

```bash
python -m scripts.test
```

Why?

Because:

* preserves package structure
* fixes import resolution

---

# 24. What Is Cypher?

Cypher is:

# Neo4j query language

Equivalent of SQL for graphs.

---

# Create Node

```cypher
CREATE (:Repository {name: "fastapi"})
```

---

# Create Relationship

```cypher
(a)-[:IMPORTS]->(b)
```

---

# Match Nodes

```cypher
MATCH (n)
RETURN n
```

---

# 25. Important Cypher Concepts

---

# MATCH

Find graph patterns.

Equivalent to SELECT in SQL.

---

# CREATE

Always create new node.

Can create duplicates.

---

# MERGE

Very important.

```cypher
MERGE (r:Repository {name: "fastapi"})
```

Meaning:

* find existing node
* else create

Equivalent to:

```text
create if not exists
```

---

# Why MERGE Matters

Without MERGE:

```text
duplicate graph nodes
```

become huge problem.

---

# 26. Graph Identity Concept

Very important.

We need stable identifiers.

---

# File Identity

```text
file path
```

---

# Function Identity

```text
file_path + function_name
```

Example:

```text
app/service/user.py:create_user
```

---

# Why Identity Matters

Without identity:

```text
same function duplicated repeatedly
```

Graph becomes corrupted.

---

# 27. What We Successfully Built

We created:

```text
(:Repository {
    name,
    url
})
```

using:

* GraphService
* Cypher MERGE
* Neo4j driver
* sessions

---

# 28. Neo4j Browser

We opened:

```text
http://localhost:7474
```

This is:

# graph visualization UI

We ran:

```cypher
MATCH (n)
RETURN n
```

and visually saw graph node.

---

# Why Visualization Matters

Graphs become intuitive visually.

You begin thinking in:

* relationships
* traversals
* architecture

instead of tables.

---

# 29. Debugging Mindset Learned

Very important backend lesson.

Debug layer-by-layer.

---

# Example Layers

---

# Layer 1

Python imports

---

# Layer 2

Config loading

---

# Layer 3

Docker networking

---

# Layer 4

Authentication

---

# Layer 5

Cypher queries

---

# Senior Engineers Ask

```text
WHICH layer failed?
```

NOT:

```text
everything broken
```

---

# 30. Stateful Infrastructure Lesson

We learned:

```text
containers are ephemeral
volumes are persistent
```

Neo4j password issue happened because:

* DB volume already existed
* initialization only happens first time

This is real distributed systems behavior.

---

# 31. Current Backend Architecture

```text
app/
├── config.py
├── db/
│   └── neo4j.py
├── services/
│   └── graph_service.py
```

---

# 32. Why Layered Architecture Matters

Each layer owns responsibility.

---

# Config Layer

Environment/configuration

---

# DB Layer

Infrastructure communication

---

# Service Layer

Business logic

---

# Parser Layer

Semantic extraction

---

# This creates:

* maintainability
* scalability
* testability

---

# 33. What Comes Next

Next phase of graph construction:

```text
Repository
    ↓
Files
    ↓
Functions
    ↓
Imports
    ↓
Call Graph
```

---

# 34. Final Important Mental Model

Archon is NOT:

```text
CRUD application
```

Archon IS:

```text
semantic architecture intelligence system
```

That changes:

* database choice
* graph design
* architecture thinking
* retrieval design
* AI integration

completely.

---

# 35. Biggest Lessons From This Phase

* repositories are graphs
* relationships create intelligence
* graphs model architecture naturally
* infrastructure must be layered
* debugging must be systematic
* config should be centralized
* stateful systems behave differently
* Docker networking is isolated
* graph identity is critical
* Cypher models patterns, not tables

---

# 36. Current Milestone Achieved

You now have:

✅ Neo4j integration

✅ Dockerized graph infrastructure

✅ Centralized config system

✅ Graph service architecture

✅ Cypher persistence

✅ First graph node

✅ Neo4j visualization

✅ Backend graph infrastructure foundation

This is the foundation for:

* architecture traversal
* dependency analysis
* semantic retrieval
* AI context assembly
* repository intelligence
* agentic code understanding

End of Phase 2 Foundation Notes.
