# Archon

Archon is an AI-powered Repository Architecture Intelligence Platform designed to analyze source code repositories, construct semantic knowledge graphs, and enable intelligent architecture-aware reasoning over codebases.

The system combines:

* static code analysis
* AST parsing
* graph databases
* semantic extraction
* vector retrieval (planned)
* LLM-powered reasoning (planned)

to transform repositories into machine-understandable architectural knowledge.

---

# Vision

Modern repositories contain rich architectural relationships that are difficult to understand manually.

Archon aims to provide:

* repository knowledge graphs
* dependency analysis
* behavioral call graphs
* semantic code retrieval
* architecture-aware AI reasoning
* impact analysis
* intelligent repository exploration

---

# Current Architecture

```text
GitHub Repository
        ↓
Repository Cloning
        ↓
Filesystem Scanning
        ↓
Python AST Parsing
        ↓
Semantic Extraction
        ↓
Graph Builder
        ↓
Neo4j Knowledge Graph
```

Current graph layers:

```text
Repository
    ↓ CONTAINS
File
    ↓ DEFINES
Function
```

Upcoming graph layers:

```text
File
    ↓ IMPORTS
Import/File
```

```text
Function
    ↓ CALLS
Function
```

---

# Tech Stack

## Backend

* FastAPI
* Python

## Databases

* PostgreSQL
* Neo4j

## Infrastructure

* Docker
* Docker Compose

## Static Analysis

* Python AST

## Planned

* pgvector
* sentence-transformers
* hybrid retrieval
* LLM orchestration

---

# Current Features

* GitHub repository cloning
* Recursive repository scanning
* Python AST parsing
* Import extraction
* Function extraction
* Function call extraction
* Semantic structure generation
* Neo4j graph ingestion
* Repository knowledge graph generation
* Repository-agnostic ingestion pipeline

---

# Repository Ingestion Pipeline

Archon currently supports automated repository ingestion:

```text
GitHub URL
    ↓
Clone Repository
    ↓
Scan Python Files
    ↓
Extract AST Semantics
    ↓
Build Graph Relationships
    ↓
Store in Neo4j
```

---

# Knowledge Graph Model

## Nodes

### Repository

Represents a source code repository.

### File

Represents a Python source file.

### Function

Represents a function definition extracted from AST parsing.

---

## Relationships

### CONTAINS

```text
Repository → File
```

Represents repository ownership.

### DEFINES

```text
File → Function
```

Represents function ownership within a file.

---

# Project Structure

```text
backend/
├── app/
├── ingestion/
├── parser/
├── services/
├── scripts/
├── models/
```

---

# Local Setup

## Start Services

```bash
docker compose up --build
```

## Run Neo4j

Neo4j Browser:
http://localhost:7474

## Run Ingestion Pipeline

```bash
python -m scripts.test_ingestion_pipeline
```

---

# Roadmap

## Phase 1

* Dockerized backend environment
* AST parsing
* Repository ingestion

## Phase 2

* Neo4j knowledge graph construction
* Dependency graph generation
* Call graph generation

## Phase 3

* Embeddings + pgvector

## Phase 4

* Hybrid retrieval

## Phase 5

* LLM context assembly

## Phase 6

* AI architecture reasoning agent

## Phase 7

* Frontend + deployment
