# System Architecture

Project: Archon

Version: MVP v1

Status: Living Document

---

# Purpose

This document defines the backend architecture of Archon.

Every service must have exactly one responsibility.

Business logic should remain inside services.

Routes should only orchestrate requests.

Repositories should only access databases.

Prompt generation should remain isolated from AI providers.

This separation makes every component independently testable and replaceable.

---

# High-Level Architecture

                        GitHub Repository
                                │
                                ▼
                     Repository Ingestion
                                │
            ┌───────────────────┴───────────────────┐
            ▼                                       ▼
     Python Parser                          Repository Metadata
            │
            ▼
     Semantic Extraction
            │
     ┌──────┴──────────┐
     ▼                 ▼
 Neo4j Graph      PostgreSQL + pgvector
     │                 │
     └──────┬──────────┘
            ▼
      Context Builder
            │
            ▼
      Prompt Builder
            │
            ▼
       Gemini LLM
            │
            ▼
      Structured Response
            │
            ▼
        FastAPI API
            │
            ▼
         Frontend

---

# Core Principles

Every layer has exactly one responsibility.

Never combine

Database

+

Prompt Generation

+

AI Calling

inside one service.

---

# Backend Layers

Client

↓

FastAPI Routes

↓

Application Services

↓

Repositories

↓

Database

---

# Layer Responsibilities

## API Layer

Responsibilities

Receive HTTP requests.

Validate request body.

Call services.

Return responses.

Should NEVER

Parse repositories.

Build prompts.

Query databases directly.

Call Gemini directly.

---

## Service Layer

Responsibilities

Business logic.

Repository orchestration.

Graph traversal.

Context generation.

Prompt generation.

LLM orchestration.

Should NEVER

Contain SQL.

Contain Cypher.

Contain API routing.

---

## Repository Layer

Responsibilities

Database access only.

SQL queries.

Cypher queries.

Vector search.

Should NEVER

Contain AI logic.

Contain prompt logic.

Contain HTTP logic.

---

# Databases

## PostgreSQL

Purpose

Structured repository storage.

Stores

Repositories

Embeddings

Metadata

Future

Reports

Bookmarks

User projects

---

## pgvector

Purpose

Semantic similarity search.

Input

Question embedding.

Output

Most similar functions.

---

## Neo4j

Purpose

Repository relationships.

Stores

Files

Functions

Imports

Dependencies

Calls

Future

Classes

Methods

Interfaces

Architecture graphs.

---

# Services

Every service owns one responsibility.

---

Repository Service

Repository lifecycle.

Create repository.

Update progress.

Track ingestion.

---

Ingestion Service

Clone repositories.

Start ingestion.

Coordinate parsing.

---

Parser

Parse source code.

Extract

Functions

Imports

Classes

Calls

---

Graph Builder

Convert parsed data into graph.

Populate Neo4j.

---

Embedding Service

Generate embeddings.

No database logic.

---

Embedding Repository

Store embeddings.

Search embeddings.

Only SQL.

---

Graph Service

All Neo4j queries.

Examples

Same file

Dependencies

Neighbors

Call graph

Architecture graph

---

Context Builder

Input

Question.

Output

Expanded repository context.

Combines

Semantic retrieval

Graph traversal

Dependency expansion

Same-file context

---

Prompt Builder

Input

Repository context.

Output

LLM prompt.

Supports

Overview

Learning

Architecture

Navigation

Planning

Investigation

Quick

---

LLM Service

Single responsibility

Talk to Gemini.

Future

Claude

GPT

Local LLM

Should be replaceable without affecting the rest of the system.

---

Report Service

Future.

Automatically generates Repository Intelligence Report.

Stores report.

Returns report.

---

# API Flow

User

↓

POST /repositories

↓

Repository Service

↓

Clone Repository

↓

Parse

↓

Graph

↓

Embeddings

↓

Repository Ready

---

Chat Flow

User Question

↓

Embedding Service

↓

Embedding Repository

↓

Context Builder

↓

Prompt Builder

↓

LLM Service

↓

Structured Response

↓

API Response

---

Repository Report Flow

Repository Finished

↓

Report Service

↓

Prompt Builder (Overview Mode)

↓

LLM

↓

Structured Report

↓

Store

↓

GET /repositories/{id}/overview

---

# Design Rules

Rules

One service.

One responsibility.

Routes stay thin.

Repositories stay dumb.

PromptBuilder never queries databases.

LLMService never knows Neo4j exists.

ContextBuilder never calls Gemini.

Repositories never contain business logic.

---

# Dependency Direction

Allowed

API

↓

Services

↓

Repositories

↓

Database

Forbidden

Repository

↓

Service

LLM

↓

Database

PromptBuilder

↓

Database

---

# Future Extensions

Multi-language parsers.

Tree-sitter.

Redis cache.

Async ingestion workers.

Planner Agent.

Tool Calling.

Streaming responses.

Collaborative workspaces.

---

# Engineering Goal

The backend should remain modular enough that replacing

Gemini

↓

Claude

or

Neo4j

↓

Memgraph

requires minimal changes.

Architecture should evolve through composition, not rewrites.