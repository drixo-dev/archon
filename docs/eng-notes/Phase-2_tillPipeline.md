# Archon — Phase 2 Foundation Notes

# Neo4j Graph Construction + Repository Knowledge Graphs

---

# 1. What Is Archon?

Archon is an AI-powered Repository Architecture Intelligence Platform.

Goal:
Transform repositories into machine-understandable semantic knowledge graphs.

Instead of treating repositories as:

* plain files
* raw text

Archon treats repositories as:

* entities
* relationships
* architecture structures
* dependency networks

---

# 2. Core Idea

Repositories are NOT just collections of files.

Repositories are:

# semantic networks of relationships

Example:

```text
Repository
    ↓
Files
    ↓
Functions
    ↓
Dependencies
    ↓
Behavior
```

This is why graph databases fit extremely well.

---

# 3. Why Neo4j?

Traditional relational databases are good for:

* tables
* structured rows
* transactional data

But repositories are highly connected systems.

Graph databases are better for:

* traversals
* dependency analysis
* architecture graphs
* relationship-heavy systems

Neo4j stores:

* nodes
* relationships
* properties

directly.

---

# 4. Important Graph Concepts

---

# Node

Represents an entity.

Examples:

* Repository
* File
* Function

Example:

```text
(:File)
```

---

# Relationship

Represents a connection between entities.

Example:

```text
(File)-[:DEFINES]->(Function)
```

Relationships have:

* direction
* meaning

---

# Properties

Metadata stored on nodes.

Example:

```json
{
  "path": "app/main.py",
  "language": "python"
}
```

---

# 5. Semantic Meaning

Semantic means:

# meaning-aware

Example:

Syntax:

```python
def abc():
```

Semantics:

```text
This function handles authentication
```

Archon focuses on:

# semantic architecture understanding

not only syntax parsing.

---

# 6. Current Graph Model

Current graph:

```text
Repository
    ↓ CONTAINS
File
    ↓ DEFINES
Function
```

---

# Repository Node

Represents:

* source repository
* project identity

---

# File Node

Represents:

* Python source file
* module/container

Properties:

* path
* language

---

# Function Node

Represents:

* executable behavior unit

Properties:

* name
* qualified_name
* file_path

---

# 7. Why Qualified Names Matter

Function names alone are NOT unique.

Example:

```python
def main():
```

may exist in many files.

So Archon uses:

```text
file_path:function_name
```

Example:

```text
app/main.py:start
```

This is called:

# canonical identity

Very important graph engineering concept.

---

# 8. Canonicalization

Canonicalization means:

# converting data into stable normalized form

Example:

BAD:

```text
/app/datasets/repositories/fastapi/app/main.py
```

GOOD:

```text
app/main.py
```

Why?

* portable
* stable
* cleaner graph
* environment-independent

---

# 9. Current Pipeline Architecture

```text
GitHub URL
    ↓
Repository Cloning
    ↓
Filesystem Scanning
    ↓
AST Parsing
    ↓
Semantic Extraction
    ↓
Graph Builder
    ↓
Neo4j
```

---

# 10. Layer Responsibilities

---

# github_loader.py

Responsible for:

* cloning repositories

---

# scanner.py

Responsible for:

* recursively finding Python files

---

# python_parser.py

Responsible for:

* AST parsing
* import extraction
* function extraction
* call extraction

---

# graph_service.py

Responsible for:

* Neo4j Cypher queries
* graph persistence
* node creation
* relationship creation

Low-level DB layer.

---

# graph_builder.py

Responsible for:

* orchestration
* parser-to-graph transformation
* ingestion workflow

High-level orchestration layer.

---

# 11. Why Separation of Concerns Matters

Each layer has:

# one responsibility

Benefits:

* easier debugging
* cleaner architecture
* easier scaling
* easier replacement
* modular systems

This is foundational backend engineering.

---

# 12. Important Graph Relationships

---

# CONTAINS

```text
Repository → File
```

Meaning:

* repository owns file

Structural relationship.

---

# DEFINES

```text
File → Function
```

Meaning:

* file defines function

Behavior ownership relationship.

---

# 13. Syntax vs Semantics

Syntax:

# how code is written

Semantics:

# what code means

Archon aims to understand:

* architecture meaning
* dependency meaning
* behavioral meaning

---

# 14. Current Limitations

Current parser:

* extracts flat imports
* extracts flat function calls

But does NOT yet:

* resolve imports
* map caller → callee
* build accurate execution flow

These come later.

---

# 15. Why Imports Matter

Imports represent:

# dependency architecture

Example:

```python
from app.db import session
```

Means:

```text
this module depends on database layer
```

Dependency graphs help detect:

* coupling
* architecture boundaries
* dependency flow

---

# 16. Why Call Graphs Matter

Function calls represent:

# execution behavior

Example:

```text
login()
    ↓
validate_user()
```

Call graphs enable:

* impact analysis
* execution tracing
* AI reasoning
* architecture understanding

---

# 17. Important Backend Engineering Concepts Learned

---

# Orchestration

High-level workflow coordination.

Example:

```text
clone → scan → parse → graph
```

---

# Infrastructure Layer

Reusable low-level systems.

Examples:

* DB layer
* parser
* scanner

---

# Entry Point

Where user/system input enters.

Currently:

```text
test_ingestion_pipeline.py
```

Later:

* API endpoint
* background worker
* scheduler

---

# Runtime Data vs Source Code

Cloned repositories are:

# runtime datasets

NOT application source code.

Therefore:

```text
backend/datasets/repositories/
```

must be `.gitignore`d.

---

# 18. Debugging Lessons Learned

---

# Graph Visualization ≠ Graph Data

Neo4j Browser may display ugly captions.

This does NOT mean graph is incorrect.

Always distinguish:

* visualization issue
* query issue
* storage issue

---

# Stateful Systems

Neo4j stores persistent graph state.

Changing code does NOT automatically rewrite old graph data.

This is why:

```cypher
MATCH (n)
DETACH DELETE n
```

was needed.

---

# 19. Current Engineering State

Archon now supports:

* automated repository ingestion
* semantic graph generation
* repository-agnostic processing
* graph persistence
* ownership graph modeling

This is already:

# real backend systems engineering

not just tutorial scripting.

---

# 20. Next Phase

Next:

# Dependency Graph Layer

Planned relationships:

```text
File → IMPORTS → Import/File
```

Later:

```text
Function → CALLS → Function
```

This will evolve Archon into:

# true repository architecture intelligence platform
