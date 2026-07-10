<div align="center">

# Archon

### Understand Any Codebase in Minutes

**An AI Repository Intelligence Platform that helps developers understand, learn, navigate, and safely modify unfamiliar codebases.**

<p>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Neo4j-Knowledge%20Graph-008CC1?logo=neo4j"/>
  <img src="https://img.shields.io/badge/PostgreSQL-pgvector-336791?logo=postgresql"/>
  <img src="https://img.shields.io/badge/Gemini-AI-4285F4"/>
  <img src="https://img.shields.io/badge/Status-Active-success"/>
</p>

---

**Paste a GitHub repository.**

Archon automatically analyzes the codebase, builds a knowledge graph, creates semantic embeddings, and lets you explore the repository through AI-powered architectural understanding.

</div>

---

# Why Archon?

Understanding a new repository is hard.

Most developers begin with:

- reading README
- opening random files
- searching symbols
- tracing function calls
- asking ChatGPT

This is slow.

Archon builds an **intelligence layer** over a repository before you even ask questions.

Instead of searching code,

you explore **knowledge**.

---

# What can Archon do?

## Repository Overview

Generate an intelligent report describing

- Repository purpose
- Architecture style
- Technology stack
- Important modules
- Entry points
- Learning path
- Suggested questions

---

## Repository Chat

Ask questions like

> How does authentication work?

> Where should I start reading?

> How are CLI arguments converted into Python types?

Archon retrieves relevant code, expands graph context, and generates evidence-based answers.

---

## Folder Intelligence

Understand every folder inside the project.

For each folder Archon explains

- Purpose
- Responsibilities
- Important files
- Reading priority
- Difficulty
- Why you should read it

---

## Repository Statistics

Automatically calculate

- Files
- Functions
- Imports
- Internal dependencies
- Call relationships
- Graph size
- Embedding coverage

---

## Knowledge Graph

Builds a Neo4j graph representing

```
Repository
      │
      ├──────── Files
      │
      ├──────── Functions
      │
      ├──────── Imports
      │
      └──────── Call Relationships
```

This graph powers retrieval and architectural reasoning.

---

# Current Product

## ✅ Implemented

### Repository Analysis

- GitHub Repository Ingestion
- Python AST Parsing
- Function Extraction
- Import Resolution
- Internal Dependency Graph
- Function Call Graph

### AI Intelligence

- Repository Overview
- Repository Chat
- Folder Overview
- Repository Statistics

### Retrieval

- Semantic Embeddings
- pgvector Search
- Context Expansion
- Hybrid Retrieval Pipeline

### Infrastructure

- FastAPI Backend
- Neo4j Knowledge Graph
- PostgreSQL + pgvector
- Docker Compose

---

## 🚧 In Progress

- Frontend Dashboard
- Architecture Explorer
- Learning Mode
- Interactive Dependency Graph

---

## 🔮 Planned

- Modification Planning
- Impact Analysis
- Multi-language Support
- Agentic Investigation Mode

---

# Architecture

```
                 GitHub Repository
                         │
                         ▼
                Repository Ingestion
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
     Python Parser              Repository Metadata
          │
          ▼
  AST Extraction
          │
          ├─────────────── Functions
          │
          ├─────────────── Imports
          │
          ├─────────────── Dependencies
          │
          └─────────────── Call Graph
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
   Neo4j Knowledge Graph         PostgreSQL + pgvector
          │                             │
          └──────────────┬──────────────┘
                         ▼
                 Context Builder
                         ▼
                 Prompt Builder
                         ▼
                    Gemini LLM
                         ▼
              Repository Intelligence
```

---

# Tech Stack

## Backend

- Python
- FastAPI

## AI

- Google Gemini
- Sentence Transformers

## Databases

- PostgreSQL
- pgvector
- Neo4j

## Infrastructure

- Docker
- Docker Compose

## Frontend *(In Progress)*

- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Framer Motion
- React Flow

---

# Example Workflow

```
Paste GitHub URL

        │

        ▼

Repository Indexed

        │

        ▼

Knowledge Graph Created

        │

        ▼

Embeddings Generated

        │

        ▼

Ask Questions

        │

        ▼

Repository Intelligence
```

---

# API

## Repository

```
POST /repositories
GET  /repositories
GET  /repositories/{id}
```

## Repository Intelligence

```
GET /repositories/{id}/overview

GET /repositories/{id}/folders

GET /repositories/{id}/statistics
```

## AI

```
POST /chat
```

Interactive Swagger documentation

```
http://localhost:8000/docs
```

---

# Project Structure

```
backend/

├── api/                FastAPI routes
├── app/                Configuration
├── ingestion/          Repository cloning
├── parser/             Python AST parsing
├── repositories/       Database layer
├── services/           Business logic
├── models/             API models

docs/

├── architecture/
├── eng-notes/
└── roadmap/

infrastructure/

docker-compose.yml
```

---

# Getting Started

## Clone

```bash
git clone https://github.com/drixo-dev/archon.git

cd archon
```

## Configure

Create

```
backend/.env
```

Example

```env
GEMINI_API_KEY=YOUR_KEY

POSTGRES_PASSWORD=password

NEO4J_PASSWORD=password
```

## Run

```bash
docker compose up --build
```

---

Open

Swagger

```
http://localhost:8000/docs
```

Neo4j Browser

```
http://localhost:7474
```

---

# Roadmap

## Backend

- [x] Repository ingestion
- [x] AST parser
- [x] Knowledge graph
- [x] Semantic retrieval
- [x] Repository overview
- [x] Folder overview
- [x] Repository statistics
- [x] AI repository chat

## Frontend

- [ ] Repository Dashboard
- [ ] Architecture Explorer
- [ ] Folder Explorer
- [ ] Interactive Graph
- [ ] Learning Path

## Future

- [ ] Modification Planning
- [ ] Impact Analysis
- [ ] Agentic Investigation
- [ ] Multi-language Support

---

# Project Philosophy

Archon is **not** another AI chat interface.

It is an **AI Repository Intelligence Platform**.

The goal is simple:

> Help developers understand unfamiliar codebases through architecture, knowledge graphs, semantic retrieval, and AI.

---

# Contributing

Contributions are welcome.

Please open an issue before large architectural changes.

For implementation work, follow the architecture documents inside `docs/architecture`.

---

# License

MIT License *(planned)*

---

<div align="center">

### Built to make understanding codebases as easy as reading documentation.

⭐ If you like the project, consider giving it a star.

</div>