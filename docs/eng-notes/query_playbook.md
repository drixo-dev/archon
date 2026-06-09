# Archon Query Playbook

## Purpose

This document defines the core Neo4j/Cypher queries used for:

* graph validation
* debugging
* architecture exploration
* dependency analysis
* semantic traversal
* repository intelligence

As Archon evolves, this playbook becomes the foundation for:

* developer tooling
* graph observability
* architecture analytics
* AI-assisted reasoning
* semantic repository navigation

---

# 1. Full Graph Visualization

## Purpose

Visualize the complete graph topology.

Useful for:

* debugging ingestion
* understanding graph shape
* validating relationships
* demos

## Query

```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 500
```

## Returns

* all nodes
* all relationships
* complete graph visualization

---

# 2. Repository Structure Query

## Purpose

Visualize repository ownership hierarchy.

Useful for:

* repository structure validation
* file organization analysis

## Query

```cypher
MATCH (r:Repository)-[rel:CONTAINS]->(f:File)
RETURN r, rel, f
```

## Graph Pattern

```text
Repository
    └── CONTAINS ──> File
```

---

# 3. File → Function Semantic Structure

## Purpose

Visualize which functions belong to which files.

Useful for:

* semantic indexing validation
* function ownership analysis
* complexity analysis

## Query

```cypher
MATCH (f:File)-[r:DEFINES]->(func:Function)
RETURN f, r, func
LIMIT 200
```

## Graph Pattern

```text
File
    └── DEFINES ──> Function
```

---

# 4. File Import Dependency Graph

## Purpose

Visualize file dependency declarations.

Useful for:

* dependency topology
* import analysis
* architecture exploration

## Query

```cypher
MATCH (f:File)-[r:IMPORTS]->(i:Import)
RETURN f, r, i
LIMIT 200
```

## Graph Pattern

```text
File
    └── IMPORTS ──> Import
```

---

# 5. Full Semantic Architecture Graph

## Purpose

Visualize all currently supported semantic layers.

Useful for:

* architecture demos
* full graph inspection
* semantic validation

## Query

```cypher
MATCH (r:Repository)-[:CONTAINS]->(f:File)
OPTIONAL MATCH (f)-[:DEFINES]->(func:Function)
OPTIONAL MATCH (f)-[:IMPORTS]->(i:Import)

RETURN r, f, func, i
LIMIT 500
```

## Graph Pattern

```text
Repository
    └── CONTAINS ──> File
            ├── DEFINES ──> Function
            └── IMPORTS ──> Import
```

---

# 6. Most Imported Modules

## Purpose

Find commonly used dependencies.

Useful for:

* dependency hotspot analysis
* framework usage detection
* shared dependency analysis

## Query

```cypher
MATCH (:File)-[:IMPORTS]->(i:Import)
RETURN i.module AS module, COUNT(*) AS usage_count
ORDER BY usage_count DESC
LIMIT 20
```

## Insights

Helps identify:

* central libraries
* heavily reused packages
* infrastructure dependencies

---

# 7. Files With Highest Import Count

## Purpose

Find highly coupled files.

Useful for:

* coupling analysis
* architecture risk analysis
* maintainability inspection

## Query

```cypher
MATCH (f:File)-[:IMPORTS]->(i:Import)
RETURN f.path AS file, COUNT(i) AS imports
ORDER BY imports DESC
LIMIT 20
```

## Insights

Highly coupled files may indicate:

* architecture bottlenecks
* unstable modules
* poor separation of concerns

---

# 8. Files With Most Functions

## Purpose

Find semantically dense files.

Useful for:

* complexity analysis
* oversized module detection
* maintainability analysis

## Query

```cypher
MATCH (f:File)-[:DEFINES]->(func:Function)
RETURN f.path AS file, COUNT(func) AS function_count
ORDER BY function_count DESC
LIMIT 20
```

## Insights

Large function counts may indicate:

* God objects
* oversized modules
* refactoring opportunities

---

# 9. Search Functions By Name

## Purpose

Perform semantic function lookup.

Useful for:

* code exploration
* semantic navigation
* developer tooling

## Query

```cypher
MATCH (func:Function)
WHERE func.name CONTAINS "test"
RETURN func
LIMIT 50
```

## Example Use Cases

Search for:

* test functions
* handlers
* utilities
* services

---

# 10. File Neighborhood Traversal

## Purpose

Explore local graph connectivity around a file.

Useful for:

* graph navigation
* dependency exploration
* architecture debugging

## Query

```cypher
MATCH (f:File {path: "tests/test_types.py"})-[r]-(n)
RETURN f, r, n
LIMIT 100
```

## Graph Pattern

```text
(File)
    ├── DEFINES
    ├── IMPORTS
    └── connected semantic entities
```

---

# 11. Multi-Hop Import Traversal

## Purpose

Explore dependency chains.

Useful for:

* dependency propagation analysis
* architecture exploration
* future impact analysis

## Query

```cypher
MATCH path = (f:File)-[:IMPORTS*1..3]->(i)
RETURN path
LIMIT 50
```

## Future Potential

Will become much more powerful after import resolution.

---

# 12. Count Nodes By Label

## Purpose

Validate graph ingestion integrity.

Useful for:

* debugging
* ingestion verification
* graph monitoring

## Query

```cypher
MATCH (n)
RETURN labels(n), COUNT(*)
```

---

# 13. Count Relationships By Type

## Purpose

Validate relationship generation.

Useful for:

* debugging
* relationship verification
* graph consistency checks

## Query

```cypher
MATCH ()-[r]->()
RETURN type(r), COUNT(*)
```

---

# 14. Detect Orphan Nodes

## Purpose

Find disconnected graph entities.

Useful for:

* graph integrity debugging
* ingestion validation
* cleanup analysis

## Query

```cypher
MATCH (n)
WHERE NOT (n)--()
RETURN n
LIMIT 50
```

## Why It Matters

Orphan nodes often indicate:

* ingestion bugs
* broken relationships
* incomplete graph construction

---

# Current Archon Graph Model

## Current Node Types

| Label      | Meaning                |
| ---------- | ---------------------- |
| Repository | repository root        |
| File       | source code file       |
| Function   | function definition    |
| Import     | dependency declaration |

---

## Current Relationship Types

| Relationship | Meaning                |
| ------------ | ---------------------- |
| CONTAINS     | ownership hierarchy    |
| DEFINES      | semantic ownership     |
| IMPORTS      | dependency declaration |

---

# Current Architectural Capability

Archon currently supports:

* repository structure analysis
* semantic function indexing
* dependency declaration analysis
* graph traversal
* graph visualization
* semantic repository exploration

---

# Future Planned Query Categories

## Import Resolution Queries

Planned relationship:

```text
(File)-[:DEPENDS_ON]->(File)
```

Future capabilities:

* dependency chains
* circular dependency detection
* architectural layering analysis
* impact propagation

---

## Behavioral Graph Queries

Planned relationship:

```text
(Function)-[:CALLS]->(Function)
```

Future capabilities:

* execution graph traversal
* behavioral analysis
* runtime flow approximation

---

## Graph Algorithm Queries

Future graph analytics:

* PageRank
* centrality analysis
* connected components
* community detection
* hotspot detection

---

# Long-Term Vision

Archon is evolving toward:

```text
Repository
    ↓
Semantic Knowledge Graph
    ↓
Architecture Intelligence Platform
    ↓
AI-Assisted Repository Understanding
```

This query playbook becomes the foundation for:

* developer intelligence tooling
* semantic retrieval
* AI reasoning
* architecture analytics
* graph-powered repository exploration
