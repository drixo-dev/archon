# Prompt Specification

Project: Archon

Version: 1.0

---

# Purpose

PromptBuilder is responsible for generating prompts for the LLM.

PromptBuilder does NOT perform retrieval.

PromptBuilder does NOT call Gemini.

PromptBuilder only transforms structured repository context into high-quality prompts.

---

# Prompt Pipeline

Question

↓

Context Builder

↓

Repository Context

↓

Prompt Builder

↓

Prompt

↓

LLM

↓

Structured Response

---

# Prompt Modes

PromptBuilder supports multiple modes.

Each mode has different objectives.

---

# Mode 1

Overview Mode

Purpose

Automatically generate the Repository Intelligence Report.

Input

Repository metadata

Knowledge graph

Semantic retrieval

Statistics

Output

Repository summary

Architecture

Tech stack

Reading order

Important modules

Suggested questions

No user question required.

---

# Mode 2

Architecture Mode

Purpose

Explain repository architecture.

Questions

Explain architecture.

Explain request lifecycle.

Explain module structure.

Response Rules

Must include

Architecture diagram

Layers

Responsibilities

Dependencies

Design decisions

Summary

---

# Mode 3

Learning Mode

Purpose

Teach repository concepts.

Questions

Explain middleware.

Explain authentication.

Teach dependency injection.

Response Rules

Must follow

TLDR

↓

Diagram

↓

Step-by-step

↓

Examples

↓

Concepts

↓

Learn Next

Should teach.

Not simply answer.

---

# Mode 4

Navigation Mode

Purpose

Locate implementation.

Examples

Find JWT.

Find authentication.

Where is routing?

Output

Relevant files

Relevant functions

Reason

Dependency relationships

---

# Mode 5

Investigation Mode

Purpose

Explain repository behavior.

Examples

Trace authentication.

Trace request lifecycle.

Who calls this?

What depends on this?

Output

Evidence

↓

Files

↓

Functions

↓

Flow

↓

Conclusion

---

# Mode 6

Planning Mode

Purpose

Help developers implement features.

Example

Add OAuth.

Implement Redis.

Introduce Celery.

Output

Recommended files

Implementation steps

Potential risks

Dependencies

Testing suggestions

---

# Mode 7

Quick Mode

Purpose

Fast answer.

Less than 300 words.

TLDR

Flow

Summary

---

# Prompt Rules

Every prompt must instruct the LLM to

Use repository evidence.

Never hallucinate.

Never invent files.

Never invent functions.

Never invent architecture.

If evidence is insufficient,

say so.

---

# Output Rules

Prefer

Bullet lists

ASCII diagrams

Tables

Hierarchies

Numbered steps

Avoid

Large paragraphs

Repeated explanations

Marketing language

---

# Repository Awareness

PromptBuilder should always provide

Repository name

Repository summary

Retrieved functions

Same-file context

Dependency context

Call graph context

Relevant modules

Question

Mode

The model should never answer without repository context when available.

---

# Future Prompt Modes

The following modes are planned.

Architecture Review

Security Review

Performance Review

Testing Review

Refactoring Review

Documentation Generation

Code Tour

Pull Request Review

These are not part of MVP.

---

# Prompt Evolution

MVP

Single PromptBuilder

↓

Version 2

Multiple Prompt Templates

↓

Version 3

Dynamic Prompt Selection

↓

Version 4

Planner Agent selects prompt mode automatically.

---

# Relationship With Agentic AI

Prompt modes are NOT agents.

Prompt modes define response style.

Agents decide

• Which tools to use

• Which repositories to search

• Which graph traversals to execute

• Which context to retrieve

PromptBuilder only converts context into prompts.

---

# Golden Rule

PromptBuilder should always optimize for understanding,

not simply answering.