# Archon Engineering Notes — Phase 1 Foundation

# What We Built So Far

We transformed Archon from:

* an empty folder
  into:
* a real distributed backend intelligence platform foundation.

We successfully built:

* WSL2 development environment
* Dockerized backend infrastructure
* FastAPI backend service
* PostgreSQL database container
* Neo4j graph database container
* Repository ingestion pipeline
* AST parsing system
* Semantic structure extraction

Most importantly:

We transitioned from:

* writing scripts
  to:

# building systems.

---

# Big Picture Architecture

Current Archon Pipeline:

```text
GitHub Repository
        ↓
Repository Cloning
        ↓
Filesystem Traversal
        ↓
Python File Discovery
        ↓
AST Parsing
        ↓
Semantic Structure Extraction
```

This is the beginning of:

# repository intelligence infrastructure.

---

# PART 1 — Development Environment

# What Is WSL2?

WSL2 stands for:

# Windows Subsystem for Linux 2

It allows Linux to run inside Windows.

We used:

* Ubuntu 24.04
* inside Windows
* with Docker integration

---

# Why We Needed Linux

Modern backend engineering heavily relies on:

* Linux tooling
* shell commands
* package managers
* Docker
* networking tools

Production servers are usually Linux-based.

So WSL2 gives:

# production-like backend environment.

---

# Important Concepts

| Concept      | Meaning                               |
| ------------ | ------------------------------------- |
| Host Machine | Your actual Windows computer          |
| WSL2         | Linux virtualized environment         |
| Ubuntu       | Linux distribution running inside WSL |
| Shell        | Command-line interface                |
| Terminal     | Window used to interact with shell    |

---

# PART 2 — Docker

# What Problem Docker Solves

Without Docker:

* everyone installs dependencies differently
* environments mismatch
* projects break

Example:

Developer A:

* Python 3.10

Developer B:

* Python 3.12

Application behaves differently.

Docker solves this by packaging:

* runtime
* dependencies
* filesystem
* environment

inside containers.

---

# Core Docker Mental Model

```text
Docker Image
        ↓
Docker Container
```

---

# Image

Blueprint/template.

Contains:

* Linux filesystem
* Python runtime
* dependencies
* application code

Example:

```dockerfile
FROM python:3.12-slim
```

---

# Container

Running instance of image.

Think:

| OOP Concept | Docker Concept |
| ----------- | -------------- |
| Class       | Image          |
| Object      | Container      |

---

# What Is Docker Compose?

Docker manages single containers.

Compose manages:

# multiple cooperating containers.

Archon currently runs:

| Service    | Purpose              |
| ---------- | -------------------- |
| API        | FastAPI backend      |
| PostgreSQL | relational/vector DB |
| Neo4j      | graph database       |

Compose orchestrates them together.

---

# Important Compose Concepts

## Service

A running containerized application.

Examples:

* api
* postgres
* neo4j

---

## Network

Compose automatically creates:

# private internal network.

Containers communicate using:

* service names
* NOT localhost

Example:

```python
postgres
```

instead of:

```python
localhost
```

inside containers.

---

## Volume

Persistent storage managed by Docker.

Used for:

* databases
* durable data

Without volumes:
database data disappears when container removed.

---

## Bind Mount

Synchronizes:
host folder ↔ container folder

Example:

```yaml
./backend:/app
```

This allows live code editing.

---

# Important Docker Commands

## Build + Start System

```bash
docker compose up --build
```

---

## Stop System

```bash
docker compose down
```

---

## View Running Containers

```bash
docker ps
```

---

## Execute Command Inside Container

```bash
docker compose exec api bash
```

---

# Important Backend Insight

Containers are:

# isolated runtime environments.

Meaning:

* separate filesystem
* separate processes
* separate networking

Container localhost refers to:

# the container itself.

NOT your computer.

This is one of the most important Docker concepts.

---

# PART 3 — FastAPI

# What Is FastAPI?

Modern Python backend framework.

Used for:

* APIs
* AI systems
* inference systems
* backend services

---

# FastAPI vs Uvicorn

| Component | Responsibility        |
| --------- | --------------------- |
| FastAPI   | application framework |
| Uvicorn   | ASGI web server       |

---

# Request Lifecycle

```text
Browser
    ↓
HTTP Request
    ↓
Uvicorn
    ↓
FastAPI Route
    ↓
Python Function
    ↓
Response
```

---

# Why `/docs` Worked

FastAPI automatically generates:

# OpenAPI documentation.

This gives:

* Swagger UI
* endpoint testing
* schema visualization

Very useful professionally.

---

# Important HTTP Concepts

| Method | Purpose       |
| ------ | ------------- |
| GET    | retrieve data |
| POST   | create data   |
| PUT    | update data   |
| DELETE | remove data   |

---

# PART 4 — Backend Architecture

# Why We Structured Backend Carefully

We separated responsibilities:

```text
backend/
├── ingestion
├── parser
├── services
├── models
├── app
```

This is called:

# separation of concerns.

---

# Why Separation Matters

Large systems become:

* difficult to debug
* difficult to scale
* difficult to maintain

without architecture boundaries.

Good systems divide:

# responsibilities.

---

# What Each Folder Means

| Folder    | Responsibility            |
| --------- | ------------------------- |
| ingestion | external data acquisition |
| parser    | semantic code analysis    |
| services  | business logic            |
| models    | data structures           |
| app       | FastAPI runtime           |

---

# PART 5 — Repository Ingestion

# What Is Ingestion?

Ingestion means:

# bringing external data into system.

Examples:

* logs into observability system
* documents into search engine
* repositories into Archon

---

# What Archon Ingestion Does

```text
GitHub URL
        ↓
Clone Repository
        ↓
Store Local Copy
        ↓
Scan Filesystem
        ↓
Identify Python Files
```

---

# Why Local Repository Cache Matters

We clone repositories locally because:

* repeated downloading expensive
* parsing needs filesystem access
* indexing becomes faster

This is called:

# caching.

Very common backend systems pattern.

---

# GitPython

Python wrapper around Git.

Allows:

* programmatic repository cloning
* repository management

Important distinction:

| Type              | Example   |
| ----------------- | --------- |
| Python library    | GitPython |
| System executable | git       |

GitPython still required actual Git installed inside container.

This taught us:

# Python dependency != system dependency.

---

# PART 6 — AST Parsing

# What Is AST?

AST means:

# Abstract Syntax Tree

Tree representation of source code structure.

---

# Why AST Exists

Source code is not just text.

Example:

```python
def login(user):
    return validate(user)
```

Humans see:

* words
* formatting

Parser sees:

* function definition
* parameter
* return statement
* function call

---

# Conceptual AST

```text
FunctionDef
 ├── name: login
 ├── args:
 │    └── user
 └── Return
      └── Call(validate)
```

---

# Why AST Is Powerful

AST enables:

* static analysis
* code intelligence
* architecture understanding
* dependency extraction

Without executing code.

---

# Static Analysis

Analyzing code WITHOUT running it.

Very important because:

* safer
* scalable
* works on untrusted repos

---

# Important AST Concepts

| Concept   | Meaning                     |
| --------- | --------------------------- |
| Node      | syntax structure            |
| Tree      | hierarchical representation |
| Traversal | walking through nodes       |
| Parser    | converts source code → AST  |

---

# AST Nodes We Used

| Node Type   | Meaning             |
| ----------- | ------------------- |
| Import      | import statement    |
| ImportFrom  | from x import y     |
| FunctionDef | function definition |

---

# What We Extracted

We successfully extracted:

* imports
* function names

from real repositories.

Example:

```python
import fastapi
```

becomes:

```text
dependency relationship
```

---

# Why Imports Matter

Imports represent:

# architectural dependencies.

Example:

```text
auth.py
    imports
database.py
```

This becomes:

# graph edge later.

---

# What We Built Technically

Our parser pipeline currently does:

```text
Repository
    ↓
Filesystem Traversal
    ↓
Python File Discovery
    ↓
AST Parsing
    ↓
Import Extraction
    ↓
Function Extraction
```

This is:

# semantic repository analysis.

---

# PART 7 — Python Packaging Lessons

# Why Imports Failed Initially

Python imports depend on:

# execution context.

This failed:

```bash
python scripts/test_parser.py
```

because Python treated:

```text
scripts/
```

as root.

---

# Proper Solution

```bash
python -m scripts.test_parser
```

This runs module properly.

---

# Important Packaging Concept

`__init__.py`

Marks folder as Python package.

Allows:

* module imports
* package resolution

---

# PART 8 — Infrastructure Debugging Lessons

# Important Real Errors We Solved

---

# Error 1 — Git Missing Inside Container

Cause:

* container did not have system git installed

Fix:

```dockerfile
RUN apt-get update && apt-get install -y git
```

Lesson:

# containers are minimal isolated environments.

---

# Error 2 — Scripts Missing

Cause:

* scripts folder outside mounted container filesystem

Lesson:

# container filesystem != host filesystem.

---

# Error 3 — Python Import Errors

Cause:

* package root misunderstanding

Lesson:

# Python module resolution depends on execution entrypoint.

---

# PART 9 — Most Important Engineering Concepts Learned

| Concept                             | Why Important             |
| ----------------------------------- | ------------------------- |
| Containers are isolated             | core Docker understanding |
| Services communicate via network    | distributed systems       |
| AST represents semantic structure   | code intelligence         |
| Imports create dependency graph     | architecture mapping      |
| Parsing != execution                | static analysis           |
| Backend systems are pipelines       | architecture design       |
| Infrastructure debugging is layered | systems reasoning         |

---

# What Archon Is Becoming

Archon is slowly evolving into:

```text
Repository
    ↓
Parser
    ↓
Intermediate Representation
    ↓
Knowledge Graph
    ↓
Semantic Retrieval
    ↓
LLM Context Assembly
```

This is:

# repository architecture intelligence.

---

# Current Milestone Achieved

We successfully built:

✅ WSL2 backend environment
✅ Dockerized infrastructure
✅ FastAPI backend service
✅ PostgreSQL container
✅ Neo4j graph database
✅ repository ingestion pipeline
✅ AST parsing system
✅ semantic extraction pipeline
✅ structured backend architecture

This is already far beyond beginner CRUD projects.

---

# Next Phase

Next we will implement:

# function call extraction

Example:

```python
login()
    calls
validate_user()
```

This becomes:

# call graph intelligence.

Which eventually powers:

* architecture understanding
* dependency traversal
* hybrid retrieval
* AI reasoning over repositories
