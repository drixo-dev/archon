# Archon Roadmap

> Last Updated: July 1, 2026

This roadmap is versioned with the repository so future sessions have a
shared, current understanding of what Archon is, what already exists, and what
should come next.

The repository remains the source of truth. If code and roadmap disagree, first
inspect the repository, then update this document.

---

## Vision

Archon is an AI-powered Repository Intelligence Platform.

It is not meant to be only a code search tool. The long-term goal is to help
users understand software architecture, dependencies, behavior, and change
impact by combining:

- static analysis
- repository knowledge graphs
- semantic retrieval
- context building
- LLM-based reasoning

---

## Design Principles

1. MVP before perfection.
2. Every feature should increase repository intelligence.
3. Prefer simple implementations that work.
4. Keep responsibilities clear and avoid hacks.
5. The repository is the source of truth.
6. Do not duplicate existing features.
7. Improve static analysis later unless it blocks the MVP.

---

## Current Architecture

```text
Repository
    |
    v
Repository Scanner
    |
    v
Python AST Parser
    |
    v
Semantic Extraction
    |
    v
Neo4j Knowledge Graph
    |
    v
Function Source Code
    |
    v
SentenceTransformer
    |
    v
384-dimensional Embeddings
    |
    v
PostgreSQL + pgvector
    |
    v
Semantic Retrieval
```

---

## Current Progress

```text
Infrastructure          Complete
Repository Ingestion    Complete
Static Analysis         Mostly complete for MVP
Knowledge Graph         Mostly complete for MVP
Embeddings              Complete
Semantic Retrieval      Complete
Context Builder         MVP slice implemented
Repository RAG          Missing
Repository Intelligence Missing
Frontend                Missing
Production              Missing
```

Estimated MVP completion: about 60%.

Estimated final product completion: about 22%.

These percentages are directional, not exact project metrics.

---

## Phase 0 - Infrastructure

Status: Complete

Completed:

- Docker Compose
- FastAPI backend container
- Neo4j service
- PostgreSQL with pgvector image
- Backend project structure
- Configuration loading with Pydantic settings

Deferred:

- Kubernetes
- CI/CD
- Monitoring
- Production deployment

---

## Phase 1 - Repository Ingestion

Status: Complete

Completed:

- GitHub repository cloning
- Local repository cache under the backend datasets area
- Recursive Python file scanning
- Repository-agnostic ingestion pipeline
- GraphBuilder orchestration

Future:

- Incremental sync
- Repository deletion/re-indexing workflow
- Multi-language scanning
- Background ingestion jobs

---

## Phase 2 - Static Analysis

Status: Mostly complete for MVP

Completed:

- Python AST parsing
- Import extraction
- Function extraction
- Function source extraction
- Function call extraction
- Module resolution
- Basic function-name resolution

Known limitations:

- Function call resolution is basic.
- Attribute calls lose some context.
- Duplicate function names can overwrite each other in the function index.
- Class methods are not modeled separately.

Deferred:

- Classes
- Methods
- Inheritance
- Decorators
- Type hints
- Async-specific analysis
- Docstrings
- Exception flow
- Advanced symbol resolution

Reason:

Perfect static analysis is not required for the MVP. Context expansion and RAG
can provide value before deeper analysis exists.

---

## Phase 3 - Knowledge Graph

Status: Mostly complete for MVP

Completed nodes:

- Repository
- File
- Function
- Import

Completed relationships:

- Repository `CONTAINS` File
- File `DEFINES` Function
- File `IMPORTS` Import
- File `DEPENDS_ON` File
- Function `CALLS` Function, basic only

Completed services:

- Neo4j connection layer
- GraphService persistence methods
- GraphBuilder ingestion orchestration
- ImportResolver module and function indexes

Recently started:

- Function neighbor lookup with callers and callees.

Deferred:

- Package graph
- Class graph
- Method graph
- Variable graph
- API graph

---

## Phase 4 - Semantic Retrieval

Status: Complete

Completed:

- SentenceTransformer embedding service
- Embedding generation for function source code
- PostgreSQL table for function embeddings
- pgvector similarity search
- Repository embedding loading script
- Manual semantic retrieval test script

Current model:

```text
BAAI/bge-small-en-v1.5
```

Embedding size:

```text
384 dimensions
```

Verified example:

```text
Query: shell completion

Relevant results include:
- shell_complete()
- get_completions()
- _main_shell_completion()
```

Lesson:

Semantic retrieval quality is good enough for the MVP.

---

## Phase 5 - Context Builder

Status: MVP slice implemented

Goal:

Turn retrieved functions into useful repository context before introducing an
LLM.

Target pipeline:

```text
Question
    |
    v
Semantic Retrieval
    |
    v
Context Expansion
    |
    v
Repository Context
```

Initial expansion strategy:

- include the retrieved function source
- include same-file functions
- include available callers and callees from the basic call graph
- include direct dependency or import neighbors where useful

Already present:

- `GraphService.get_function_neighbors()`
- `backend/scripts/test_neighbors.py`
- `GraphService.get_functions_by_file()`
- `GraphService.get_functions_by_qualified_names()`
- `GraphService.get_dependency_functions()`
- `ContextBuilder.build_context()`
- `backend/scripts/test_context_builder.py`

Still missing:

- context ranking
- token budgeting
- import-node context
- API endpoint for context building
- stronger call graph coverage

Verified example:

```text
Query: shell completion

Context Builder returns:
- retrieved shell-completion functions
- same-file surrounding functions
- empty call-neighbor functions for this query
- empty dependency functions for this query
```

Lesson:

Same-file expansion already improves context beyond semantic retrieval alone.
The empty graph-neighbor buckets confirm that the basic call graph remains
limited, which matches the current MVP assumptions.

Do not spend this phase perfecting static analysis.

---

## Phase 6 - Repository RAG

Status: Missing

Goal:

Use retrieved and expanded repository context to answer questions.

Target pipeline:

```text
Question
    |
    v
Retriever
    |
    v
Context Builder
    |
    v
LLM
    |
    v
Repository-aware Answer
```

Capabilities:

- repository chat
- architecture questions
- code explanation
- dependency explanation
- "where is this implemented?" questions

---

## Phase 7 - Repository Intelligence

Status: Missing

This is where Archon becomes more than semantic code search.

Planned capabilities:

- explain subsystem
- find implementation
- find entry points
- impact analysis
- architecture summaries
- dead code detection
- duplicate implementation detection
- dependency visualization
- refactoring suggestions

---

## Phase 8 - Tool Calling

Status: Missing

Potential tools:

- `search_code`
- `get_dependencies`
- `get_definition`
- `graph_traversal`
- `repository_summary`
- `build_context`

Later:

- agent planning
- multi-step reasoning
- tool result memory

---

## Phase 9 - Backend APIs

Status: Mostly missing

Current API:

- root health endpoint only

Needed:

- repository ingestion API
- semantic search API
- context builder API
- repository question API
- graph exploration API

---

## Phase 10 - Frontend

Status: Missing

Planned views:

- dashboard
- repository upload / registration
- ingestion status
- graph explorer
- semantic search
- AI chat
- architecture explorer

---

## Phase 11 - Production

Status: Missing

After MVP:

- authentication
- projects
- multi-user support
- background workers
- caching
- deployment
- monitoring
- rate limits

---

## Phase 12 - Multi-language Support

Status: Deferred

Possible future languages:

- TypeScript
- Go
- Rust
- Java

Likely future parser:

- Tree-sitter

Reason for deferral:

Python-only keeps the MVP focused while the architecture is still taking shape.

---

## Technical Decisions

### PostgreSQL + pgvector

Chosen over a dedicated vector database for the MVP.

Reason:

- simpler deployment
- already part of the stack
- enough for current retrieval needs
- can migrate later if needed

### Neo4j

Chosen because repository intelligence depends heavily on graph traversal.

Good for:

- dependencies
- callers and callees
- ownership relationships
- impact paths

### SentenceTransformer

Current model:

```text
BAAI/bge-small-en-v1.5
```

Reason:

- small enough for MVP
- free and local
- 384-dimensional output
- good enough semantic retrieval quality so far

### Static Analysis

Current decision:

Keep static analysis simple until the MVP proves the larger workflow.

Reason:

Advanced static analysis can consume a lot of time while only improving part of
the product. Context Builder and RAG are higher leverage right now.

---

## Current Priority

Refine the Context Builder and prepare it for Repository RAG.

Recommended next tasks:

1. Add context ranking and token budgeting.
2. Add a context builder API endpoint.
3. Decide how much source code to include in each context bucket.
4. Prepare the context object for LLM prompting.

After that:

1. Add Repository RAG.
2. Add backend APIs.
3. Build early repository intelligence features.
4. Add the frontend.

---

## Future Ideas

- GraphRAG
- hybrid retrieval
- better embeddings
- reranking
- multi-agent workflows
- architecture clustering
- impact prediction
- pull request review assistant
- automated onboarding
- repository health score

---

## Session Startup Checklist

At the start of every implementation session:

1. Inspect the repository structure.
2. Check Git status.
3. Compare implementation against this roadmap.
4. Identify completed, partial, missing, and outdated items.
5. Recommend the next highest-priority task based on the repository.
6. Update this roadmap after major milestones.

Before implementing a new feature:

1. Explain the goal.
2. Teach the underlying concept.
3. Show the architecture and data flow.
4. Ask 3-5 short understanding-check questions.
5. Continue only after misconceptions are corrected.
