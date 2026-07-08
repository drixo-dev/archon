# Agent Roadmap

Project: Archon

Version: 1.0

Status: Future Roadmap

---

# Purpose

This document defines the evolution of Archon's AI architecture.

It explains

• Why the MVP is NOT agentic

• When agents become valuable

• Which agents exist

• Their responsibilities

• Their tools

• Their communication

The goal is to avoid unnecessary complexity while leaving a clear path toward a fully autonomous Repository Intelligence Platform.

---

# Philosophy

Agents are expensive.

Every additional agent introduces

• latency

• complexity

• debugging difficulty

• orchestration

• token usage

Therefore

Agents should only be introduced when they solve a problem that a deterministic pipeline cannot solve.

---

# MVP

Agent Count

0

Architecture

Pipeline

Question

↓

Embedding

↓

Semantic Retrieval

↓

Context Builder

↓

Prompt Builder

↓

LLM

↓

Answer

This architecture is deterministic.

Easy to debug.

Easy to improve.

Easy to benchmark.

---

# Why MVP Does Not Need Agents

Repository questions generally follow one path.

Question

↓

Retrieve Context

↓

Generate Answer

No planning required.

No decision making required.

A pipeline is simpler.

Faster.

Cheaper.

More reliable.

---

# Agent Evolution

Version 1

Pipeline

↓

Version 2

Planner Agent

↓

Version 3

Tool Agents

↓

Version 4

Multi-Agent Collaboration

↓

Version 5

Autonomous Repository Engineer

---

####################################################

# Version 2

Planner Agent

####################################################

Purpose

Determine HOW a question should be answered.

Example

Question

Where does authentication begin?

Planner decides

↓

Graph Search

↓

Semantic Search

↓

Architecture Prompt

↓

Answer

Another example

Question

Explain Dependency Injection.

Planner decides

↓

Learning Mode

↓

Relevant Files

↓

Architecture Diagram

↓

Answer

The Planner does NOT answer.

It chooses the strategy.

---

Planner Inputs

Question

Repository Metadata

Available Tools

Repository Statistics

---

Planner Outputs

Mode

Tools

Traversal Depth

Response Style

---

Planner Decisions

Should I

Use semantic retrieval?

Use graph traversal?

Use architecture prompt?

Use learning prompt?

Use planning prompt?

---

####################################################

# Version 3

Tool Agents

####################################################

Each agent owns exactly one capability.

---

Repository Search Agent

Purpose

Find files.

Find functions.

Find folders.

Find symbols.

Tool

Embedding Search

---

Graph Agent

Purpose

Traverse Neo4j.

Answer

Dependencies

Call graph

Import graph

Architecture graph

Tool

Neo4j

---

Learning Agent

Purpose

Turn repository context into lessons.

Produces

Learning paths

Tutorials

Repository onboarding

---

Architecture Agent

Purpose

Generate architecture reports.

Produces

Architecture diagrams

Layer explanations

Dependency summaries

Module responsibilities

---

Planning Agent

Purpose

Help developers implement features.

Example

"I want OAuth."

Produces

Files

Functions

Implementation order

Risks

Dependencies

---

Health Agent

Purpose

Repository analysis.

Detect

Dead code

Circular dependencies

Hotspots

Large modules

High coupling

Future

Complexity score.

---

####################################################

# Version 4

Multi-Agent Collaboration

####################################################

Question

Implement OAuth.

↓

Planner

↓

Planning Agent

↓

Repository Search Agent

↓

Graph Agent

↓

Architecture Agent

↓

Planner

↓

Prompt Builder

↓

LLM

↓

Answer

Each agent contributes evidence.

Planner combines everything.

---

####################################################

# Tool Definitions

####################################################

Repository Search Tool

Searches embeddings.

Returns

Functions

Files

Similarity scores.

---

Graph Tool

Traverses Neo4j.

Returns

Dependencies

Callers

Callees

Imports

Neighbors

Paths

---

Parser Tool

Reads parser metadata.

Returns

Functions

Classes

Imports

AST

---

Statistics Tool

Repository metrics.

Returns

File count

Function count

Module count

Languages

Technologies

---

Report Tool

Reads Repository Intelligence Report.

Returns

Summary

Architecture

Learning Path

Suggested Questions

---

####################################################

# Agent Communication

####################################################

Agents never communicate directly.

Planner owns orchestration.

Planner

↓

Agent

↓

Planner

↓

Agent

↓

Planner

↓

Prompt Builder

This keeps orchestration deterministic.

---

####################################################

# Future Memory

####################################################

Long term

Agents maintain

Repository history

Previous investigations

Bookmarks

Developer notes

Learning progress

Open questions

Not part of MVP.

---

####################################################

# Why Prompt Modes Still Exist

####################################################

Prompt Modes

≠

Agents

Prompt Modes define

HOW the answer should look.

Agents decide

HOW to collect information.

Example

Architecture Mode

↓

Architecture Prompt

↓

Architecture Response

No agent required.

---

Example

Question

Where should I implement OAuth?

Planner Agent

↓

Graph Agent

↓

Planning Agent

↓

Prompt Builder

↓

Planning Prompt

↓

LLM

Now agents become useful.

---

####################################################

# Long-Term Vision

####################################################

Eventually

Archon should behave like an experienced Staff Software Engineer.

The user asks

"I want to implement feature X."

Archon should

Understand the repository.

Explore dependencies.

Read architecture.

Estimate impact.

Generate implementation plan.

Recommend testing strategy.

Explain risks.

Without requiring the user to manually investigate.

---

# Engineering Principle

Never add an agent because it sounds impressive.

Add an agent only when

Planning

Reasoning

Orchestration

or

Tool Selection

cannot be implemented cleanly using deterministic pipelines.

If a pipeline solves the problem,

prefer the pipeline.

---

# Final Architecture Evolution

MVP

Pipeline

↓

Repository Intelligence

↓

Repository Learning

↓

Repository Navigation

↓

Repository Investigation

↓

Planner Agent

↓

Tool Agents

↓

Multi-Agent Collaboration

↓

Autonomous Repository Engineer

The transition should be evolutionary.

Never rewrite the system.

Every stage should build naturally on the previous architecture.