# Archon Engineering Notes

# Phase 3 - Function Call Graph → Neo4j → Embeddings → Semantic Retrieval

---

# Big Picture

Before this phase, Archon could:

* Scan repositories
* Parse Python files
* Extract imports
* Extract functions

Example:

```python
def login():
    validate_user()
    create_session()
```

We could see:

```text
Functions:
- login
- validate_user
- create_session
```

But Archon still did not understand relationships.

---

# Problem We Wanted To Solve

Suppose a repository contains:

```python
def login():
    validate_user()
    create_session()
```

and

```python
def logout():
    destroy_session()
```

A human immediately understands:

```text
login
 ├── validate_user
 └── create_session

logout
 └── destroy_session
```

But a computer only sees text.

We wanted Archon to understand these relationships.

---

# Function Call Graph

## What Is It?

A function call graph is a map showing:

```text
Caller Function
        ↓
Called Function
```

Example:

```python
def login():
    validate_user()
    create_session()
```

Produces:

```text
login
  ↓
validate_user

login
  ↓
create_session
```

---

# Why Do We Need It?

Without call graphs:

```text
Functions exist
```

With call graphs:

```text
Functions exist

AND

Functions interact
```

This allows us to answer:

```text
What does login depend on?

Which functions are most important?

What breaks if I change this function?
```

---

# How We Built It

Inside AST parsing:

```python
ast.FunctionDef
```

represents a function.

Inside each function we searched for:

```python
ast.Call
```

which represents a function call.

Example:

```python
def login():
    validate_user()
```

AST sees:

```text
FunctionDef(login)

Call(validate_user)
```

We store:

```json
{
  "caller": "login",
  "callee": "validate_user"
}
```

---

# Limitation

Currently:

```python
validate_user()
```

works well.

But:

```python
auth.validate_user()
```

only gives:

```text
validate_user
```

We lose some context.

This will be improved later.

---

# Neo4j Knowledge Graph

---

# What Is Neo4j?

Neo4j is a Graph Database.

Normal databases store:

```text
Rows
Columns
```

Example:

| id | name  |
| -- | ----- |
| 1  | login |

---

Neo4j stores:

```text
Nodes
Relationships
```

Example:

```text
(login)
   |
CALLS
   |
(validate_user)
```

This is much better for code relationships.

---

# Why Not PostgreSQL?

PostgreSQL is excellent for:

```text
Store Data
Search Data
```

Neo4j is excellent for:

```text
Understand Relationships
```

Archon needs both.

---

# Nodes In Archon

Repository

```text
(Repository)
```

File

```text
(File)
```

Function

```text
(Function)
```

Import

```text
(Import)
```

---

# Relationships In Archon

Repository contains File

```text
Repository
    |
CONTAINS
    |
File
```

File defines Function

```text
File
   |
DEFINES
   |
Function
```

File imports Module

```text
File
   |
IMPORTS
   |
Import
```

File depends on File

```text
File
   |
DEPENDS_ON
   |
File
```

Function calls Function

```text
Function
   |
CALLS
   |
Function
```

---

# Why Graph Databases Matter

Suppose user asks:

```text
Show me everything affected by login()
```

Graph traversal becomes:

```text
login
 ↓
validate_user
 ↓
database
```

Neo4j is designed for this.

---

# Source Code Storage

Earlier we only stored:

```text
Function Name
```

Example:

```text
login
```

That is not enough.

We later stored:

```text
Full Source Code
```

Example:

```python
def login():
    validate_user()
    create_session()
```

inside Neo4j.

---

# Why Store Source Code?

Because embeddings require actual content.

This:

```text
login
```

is not enough.

This:

```python
def login():
    validate_user()
```

contains meaning.

---

# Embeddings

This is the most important AI concept so far.

---

# What Is An Embedding?

An embedding is a vector.

Example:

```text
[0.12, -0.88, 0.42, ...]
```

Our model generates:

```text
384 numbers
```

for each function.

---

# Why?

Computers do not understand text.

They understand numbers.

Embedding converts:

```python
def shell_complete():
```

into:

```text
[384 numbers]
```

---

# Human Analogy

Imagine every function gets coordinates.

Example:

```text
Authentication functions

(1,2)
(2,2)
(1,3)
```

Email functions:

```text
(100,100)
(102,98)
```

Similar functions stay close together.

Different functions stay far apart.

Embeddings do exactly this.

---

# Embedding Model Used

We use:

```text
all-MiniLM-L6-v2
```

from Sentence Transformers.

Output:

```text
384 dimensions
```

Why?

Because:

```text
Small
Fast
Good quality
Free
```

Perfect for MVP.

---

# pgvector

---

# What Is pgvector?

Extension for PostgreSQL.

Allows PostgreSQL to store vectors.

Example:

```sql
embedding VECTOR(384)
```

Without pgvector:

```text
PostgreSQL stores text
```

With pgvector:

```text
PostgreSQL stores embeddings
```

---

# Table Structure

```sql
function_embeddings
```

Columns:

```text
id
file_path
source_code
embedding
```

Example:

```text
typer/core.py:shell_complete
```

plus its vector.

---

# Why Not Store Embeddings In Neo4j?

Neo4j:

```text
Graph Relationships
```

pgvector:

```text
Vector Search
```

Each database does what it is best at.

---

# Semantic Search

This is where AI begins.

---

# Traditional Search

Query:

```text
shell completion
```

Search engine:

```text
Find exact words
```

Problem:

```text
autocomplete
```

may never match.

---

# Semantic Search

Query:

```text
shell completion
```

Embedding generated:

```text
[384 numbers]
```

Database finds vectors closest to it.

---

# Example

Query:

```text
shell completion
```

Results:

```text
shell_complete()

get_completions()

_main_shell_completion()
```

Even if exact words differ.

This is semantic understanding.

---

# Similarity Search Query

pgvector uses:

```sql
ORDER BY embedding <=> query_embedding
```

Meaning:

```text
Small distance
=
More similar

Large distance
=
Less similar
```

---

# What We Achieved

For the first time Archon can:

```text
Question
    ↓
Embedding
    ↓
Vector Search
    ↓
Relevant Functions
```

Example:

```text
shell completion
```

returns:

```text
shell_complete()

get_completions()

_main_shell_completion()
```

from the Typer repository.

---

# Current Architecture

```text
Repository
    ↓

Scanner
    ↓

AST Parser
    ↓

Neo4j Graph
    ↓

Source Code
    ↓

Embedding Model
    ↓

pgvector
    ↓

Semantic Retrieval
```

---

# What We Have NOT Built Yet

Current:

```text
Question
   ↓
Relevant Functions
```

Missing:

```text
Question
   ↓
Relevant Functions
   ↓
LLM
   ↓
Answer
```

This future step is called:

```text
RAG
(Retrieval Augmented Generation)
```

---

# Interview Explanation

Question:

What have you built so far in Archon?

Answer:

I built a repository intelligence system that parses source code into an AST, extracts functions, imports and dependencies, stores relationships inside Neo4j as a knowledge graph, generates embeddings for source code using Sentence Transformers, stores vectors in PostgreSQL using pgvector, and performs semantic retrieval over repository functions. This allows users to search code using natural language rather than exact keywords.

```
```
