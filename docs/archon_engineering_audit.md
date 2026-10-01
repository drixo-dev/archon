# Archon Backend — Engineering Audit

Scope: `backend/` as shipped in the uploaded zip. No frontend code is present in this
archive (docs correctly list "Frontend" under "Future," so this isn't a gap in the audit —
it's just not part of this repo yet). Findings below come from reading the actual source,
tracing the ingestion path end-to-end, and running `pytest` against the real test suite
(not from README/CURRENT_STATE.md, which I only used to cross-check claims).

---

## A. Current architecture (what the code actually does)

```
POST /repositories
  → RepositoryService.create_repository()
      → repo id = slug parsed from the URL (last path segment, ".git" stripped)
      → row written to Postgres `repositories` table
      → a daemon Thread is spawned to run ingestion (non-blocking request)

Background thread:
  → GitPython clones the repo into /app/datasets/repositories/<slug>
  → scanner.scan_python_files() → rglob("*.py") over the whole clone (no exclusions)
  → import_resolver builds two indexes:
      - module_index: {dotted.module.path: relative/file.py}
      - function_index: {bare_function_name: "relative/file.py:function_name"}   ← global, flat
  → for each file: ast-parse → imports / functions / naive call list
  → graph_builder writes Repository/File/Function/Import nodes + IMPORTS/DEPENDS_ON/CALLS
    edges into Neo4j via MERGE
  → for each Function node (excluding tests/): sentence-transformers embedding generated
    one at a time and upserted into Postgres/pgvector `function_embeddings`
  → repository row updated with status/progress at each stage
    (queued → cloning → scanning → graph → embedding → ready | failed)

Read path:
  GET /repositories, /repositories/{id}, /{id}/statistics, /{id}/overview, /{id}/guide
  POST /chat → ContextBuilder (pgvector similarity + Neo4j file-stat scoring) →
               PromptBuilder → LLMService (Gemini) → answer + context returned together
```

This is recognizably the pipeline the vision doc describes (deterministic graph + vector
retrieval + LLM explanation), and the *shape* is right. The problems are in the details of
identity, isolation, and failure handling, described below.

## B. Working components (verified by reading + partial execution)

- FastAPI app boots, routes register, `/` responds — `test_app_startup.py` passes in
  isolation once dependencies mock cleanly.
- Two-phase-ish node/relationship creation exists per file (nodes then edges), and imports
  resolve to real in-repo files via `module_index` correctly for the common
  `import x` / `from x import y` cases.
- `statistics_service.py` and `folder_service.py` **do** filter Neo4j queries by
  `repository_name` at read time — someone clearly tried to make stats repo-scoped.
- pgvector `search_similar` accepts and applies a `repository_id` filter.
- `tests/test_embedding_repository.py` passes and genuinely exercises the
  has-column / upsert branch of `insert_embedding`.
- Ingestion is non-blocking (background thread), and progress is tracked in Postgres with
  granular stage updates — reasonable UX foundation for polling.

## C. Broken / dangerous components (exact locations)

### C1. Cross-repository data corruption (graph layer) — the most serious bug in the repo
`services/graph_service.py`:
- `create_file`: `MERGE (f:File {path: $file_path})` — **the merge key is `path` alone**,
  not scoped by repository.
- `create_function`: `qualified_name = f"{file_path}:{function_name}"`, merged the same way
  — also **not scoped by repository**.

Two different repositories that both happen to have, say, `app/main.py` with a function
called `main` will MERGE onto the *same* Neo4j nodes. Their `CALLS`/`DEPENDS_ON` edges,
`source_code`, and `repository_name` property all get overwritten/merged across tenants.
This isn't hypothetical — it's the default outcome for any two repos with common file
layouts (`main.py`, `utils.py`, `__init__.py`, `config.py` are all very common).

### C2. The same collision exists in Postgres/pgvector
`repositories/embedding_repository.py`: `id TEXT PRIMARY KEY` is the same
`file_path:function_name` string, with `ON CONFLICT (id) DO UPDATE`. Same cross-repo
collision, same silent overwrite, no error raised.

### C3. Root cause: repository identity is just a URL slug
`services/repository_service.py`: `repo_name = github_url.rstrip("/").split("/")[-1]`.
`github.com/org-a/utils` and `github.com/org-b/utils` both become id `"utils"`. The second
`create_repository` call for a same-named repo from a different owner will find the
"existing" metadata row and **return it without re-ingesting**, silently serving one repo's
data as if it were another's. This single design choice is what makes C1/C2 land in
practice, not just in theory.

### C4. Global (non-file-scoped) call resolution produces confidently wrong edges
`services/import_resolver.py::build_function_index` builds one flat dict
`{function_name: qualified_name}` across the **entire repository**, overwriting earlier
entries whenever two files define a function with the same name (`get`, `run`, `main`,
`__init__`, `handle`, any repeated method name across classes, etc.). `graph_builder.py`
then resolves every call site against this global dict. The result: `CALLS` edges routinely
point at the wrong function. This directly contradicts the project's own stated principle
(vision doc §10): *"Prefer unknown/unresolved over confidently incorrect edges."* Right now
the system does the opposite — it always resolves if *any* function anywhere has a matching
name, with no file/scope awareness and no way to mark a call unresolved-but-known-external
vs. unresolved-and-ambiguous.

### C5. Parser silently drops `async def`
`parser/python_parser.py::extract_functions` and `extract_function_calls` only match
`ast.FunctionDef`, never `ast.AsyncFunctionDef`. Any `async def` function is invisible to
the graph and to embeddings — no node, no error, no log. In a modern FastAPI-style codebase
(including Archon's own backend) this silently drops a large fraction of functions.

### C6. Call attribution leaks into parent scope for nested functions
`extract_function_calls` uses `ast.walk(node)` starting from each `FunctionDef`, but doesn't
stop at nested `FunctionDef` boundaries — a call made inside a nested/inner function gets
attributed to the *outer* function too (double-counted, wrong caller).

### C7. Importing the app can crash the whole process on missing config
`services/llm_service.py` instantiates `LLMService()` at **module import time**, and
`__init__` raises `ValueError` if `GEMINI_API_KEY` isn't set. Because `api/chat.py` imports
`services.chat_service`, which imports `LLMService` at module scope, **the entire FastAPI
app fails to start** without a Gemini key — even though the vision doc is explicit that
deterministic features (stats, graph browsing) must work without an LLM. Right now a single
missing env var takes down everything, not just `/chat`.

### C8. Embedding model load is also a hard import-time dependency
`services/embedding_service.py` instantiates `SentenceTransformer(...)` at module import
time. This downloads/loads a model from Hugging Face Hub the moment
`services.repository_service` (or anything importing it) is imported. Confirmed directly:
running the shipped test suite in a network-restricted environment fails on collection with
`OSError: We couldn't connect to huggingface.co`, before a single test body executes. This
is not a leftover from an unusual sandbox — it means the test suite (and app startup) has a
hard, unmocked, uncached network dependency. No lazy loading, no offline-mode support, no
way to inject a fake embedder for tests.

### C9. The shipped test suite does not match the shipped code
- `tests/test_repository_service.py` references `RepositoryService()._repositories` and
  `._repository_index` — attributes that **do not exist** on the actual class (which uses
  `_ingestion_threads`/`_lock` and delegates all persistence to `metadata_repository`).
  These tests cannot pass against the real implementation.
- `tests/test_embedding_repository.py` mocks a method `_ensure_schema` that doesn't exist
  on `EmbeddingRepository` (the real method is `initialize_schema`). The test still "passes"
  only because `MagicMock` silently accepts the attribute assignment — it isn't actually
  testing schema initialization at all.
- Net effect: **`pytest` cannot even collect** in a clean environment (import chain drags in
  the network-dependent embedding model), and two of four test files assert against a class
  shape that doesn't exist. The test suite is not currently a safety net.

### C10. Single shared, non-pooled DB connections used from multiple threads
`app/db/postgres.py` and `app/db/neo4j.py` each hold **one module-level connection/driver**.
Ingestion runs on a background `Thread`, while request handlers run concurrently on other
threads, all sharing the same psycopg2 connection object with no locking around
cursor/commit sequences. Two ingestions running concurrently, or a request touching Postgres
mid-ingestion, can interleave commits/rollbacks on the same connection. There's also no
reconnect logic — if the connection drops, every subsequent call fails until process
restart.

### C11. `information_schema` queried on every single embedding insert
`embedding_repository.insert_embedding` runs a `SELECT ... FROM information_schema.columns`
before every insert (once per function, so hundreds/thousands of times per ingestion) to
check whether `repository_id` exists — a migration workaround left in permanently rather
than being a one-time startup check.

### C12. No input validation on GitHub URLs → SSRF / path-traversal surface
`models/repository.py::RepositoryCreateRequest.github_url` is a bare `str` (no scheme
allow-list, no host validation). `ingestion/github_loader.py::clone_repository` passes it
straight to `GitPython.Repo.clone_from` with no scheme restriction (git's `ext::`
transport and local/`file://` paths are not excluded) and derives the local clone directory
name (`repo_url.split("/")[-1]`) with no sanitization against `../` sequences before joining
it to `REPOSITORIES_DIR`. There's also no repo-size limit, no clone depth/timeout limit, and
`scan_python_files` walks every `.py` file in the clone with no exclusion list (`.git/`,
vendored deps, virtualenvs, etc. would all be scanned if present).

### C13. No authentication, authorization, or multi-tenancy anywhere
There is no `/auth` router, no user model, no ownership check on any repository-scoped
route. Every `/repositories/{id}/...` endpoint trusts the client-supplied ID completely.
Combined with C1–C3, this isn't just "add auth later" — the data model itself has no
concept of a tenant boundary to enforce.

## D. Architectural weaknesses, ranked

**P0 — blocks product/deployment**
1. Cross-repository data corruption in Neo4j and Postgres (C1, C2, C3)
2. Repository identity collisions from naive URL-slug IDs (C3)
3. Global flat function-name resolution producing wrong `CALLS` edges (C4)
4. App-wide startup crash on missing `GEMINI_API_KEY`, defeating the "useful without an
   LLM" requirement (C7)
5. Hard network/model dependency at import time breaks tests and slows/risks startup (C8)
6. No auth/ownership on any repository-scoped endpoint (C13)
7. Untrusted external URL fed directly into git clone + path join with no validation (C12)

**P1 — important, not launch-blocking on day one but close**
8. Async functions invisible to parser/graph (C5)
9. Nested-function call misattribution (C6)
10. Shared non-pooled DB connections across threads with no reconnect logic (C10)
11. Test suite doesn't match implementation and can't be collected offline (C9)
12. No migration tool — schema evolves via ad hoc `ALTER TABLE IF EXISTS ADD COLUMN IF NOT
    EXISTS` calls scattered in application code (metadata_repository, embedding_repository)
13. Embeddings generated one-at-a-time, no batching, no retry, no timeout, no failure record
    per function (violates the "resilient ingestion" and "no silent embedding failure" goals)
14. No vector index (ivfflat/hnsw) on the pgvector column — fine at current scale, will not
    scale

**P2 — real but lower urgency**
15. `information_schema` lookup on every embedding insert (C11)
16. `metadata_repository.update_repository` builds column names via f-string interpolation
    from a dict's keys (values are parameterized, so not exploitable today since only
    hardcoded keys are ever passed — but it's a SQL-injection-shaped pattern that becomes
    dangerous the moment any caller passes a user-influenced key)
17. `scan_python_files` has no exclusion list for `.git/`, virtualenvs, vendored code
18. No structured logging / request IDs / stage timing (only `print()`)

## E. Recommended target architecture (grounded in what's actually here)

The pipeline shape in the vision doc is correct and this codebase already follows it — the
fix is not a rewrite, it's making **identity repository-scoped everywhere** and
**decoupling optional dependencies from startup**:

- **Repository identity**: switch from a URL-derived slug to a generated repository ID
  (e.g., UUID or `owner/repo` normalized and validated against `github.com` hosts only),
  used as the join key everywhere.
- **Neo4j keys**: `File` and `Function` MERGE keys must include the repository ID
  (e.g., `File {repository_id, path}`, `Function {repository_id, qualified_name}`), with a
  uniqueness constraint created at startup (`CREATE CONSTRAINT ... IF NOT EXISTS`).
- **Postgres keys**: `function_embeddings.id` should be `(repository_id, qualified_name)`
  — either a composite primary key or a synthetic `repository_id || ':' || qualified_name`
  — never a bare cross-repo-collidable string.
- **Call resolution**: build `function_index` per-file first (same-file calls resolve
  first, unambiguously), then a repository-scoped cross-file index; when a name is
  ambiguous (multiple repository-wide candidates) or unresolved, record it as
  `unresolved`/`ambiguous` rather than guessing — this is explicitly what the vision doc
  asks for and the current code doesn't do it.
- **Optional dependencies must not block startup**: lazy-load the embedding model on first
  use (or behind a feature flag), and make `LLMService` construction lazy/on-demand inside
  `chat_service.chat()` rather than at import time, with a clear 503 if genuinely
  unavailable — never an app-wide crash.
- **Connections**: move to a small connection pool (`psycopg2.pool` or `asyncpg` pool) and
  a Neo4j driver used per-request/per-session rather than a single shared object crossed by
  threads.
- Everything else — the ingestion state machine, the Neo4j graph shape
  (Repository→File→Function, IMPORTS/DEPENDS_ON/CALLS), the stats/overview split from LLM
  chat, the background-thread async ingestion — is a reasonable foundation and should not
  be rewritten.

## F. Implementation roadmap (smallest sequence to a deployable, trustworthy MVP)

1. Fix repository identity + scope all Neo4j/Postgres keys by `repository_id` (C1/C2/C3) —
   this alone removes the worst correctness risk.
2. Make `LLMService` and `EmbeddingService` lazy so a missing Gemini key or no network
   access degrades gracefully instead of crashing the app (C7/C8) — restores "useful
   without an LLM."
3. Fix `import_resolver` to resolve same-file calls first and mark genuinely ambiguous
   cross-file calls as unresolved instead of silently picking one (C4).
4. Add `AsyncFunctionDef` support and fix nested-function call attribution in the parser
   (C5/C6).
5. Validate `github_url` (host allow-list, no local/`ext::` transports) and sanitize the
   derived clone directory name against path traversal (C12).
6. Rewrite the test suite to match the real class shapes, and inject a fake/no-op embedder
   for tests so `pytest` doesn't require network access (C9).
7. Only after 1–6: add auth/ownership (C13) — doing this first would just add an
   authorization layer on top of a data model that still corrupts across tenants.

Everything past this point (batching embeddings, connection pooling, vector indexes,
migrations, observability) is real but is P1/P2 polish, not a blocker for a correct
single/few-tenant MVP.

## G. Files that are stable and should not be touched without reason

- `app/main.py` (lifespan wiring is fine once F.2 makes construction lazy)
- `ingestion/scanner.py` (correct as far as it goes; only needs an exclusion list, not a
  rewrite)
- `services/graph_service.py`'s Cypher for read-side queries (`get_function_neighbors`,
  `get_file_statistics_for_folders`, etc.) — these are correctly repository-scoped already;
  only the *write*-side MERGE keys need to change
- `services/statistics_service.py`, `services/folder_service.py` — already repository-scoped
  and reasonably designed
- `docker-compose.yml` / `Dockerfile` — adequate for a first deployable milestone as-is; no
  need for Kubernetes or anything heavier yet

## H. Recommended first implementation task

**Fix repository-scoped identity in the graph and embedding layers (item 1 in the roadmap).**
This is the single change that eliminates the most severe and highest-blast-radius bug
(cross-tenant data corruption), it's well-contained (touches `graph_service.py`,
`embedding_repository.py`, and the ID-generation logic in `repository_service.py`), and
every other fix is safer to build on top of a data model whose keys are actually unique per
repository. I'd want to add the synthetic two-file-repo integration test from vision-doc §28
alongside this change to prove the fix, per your rule about not trusting apparent success.

I haven't touched any code yet, per your instruction to complete the audit first. Let me
know if you want me to start on this, or if you'd rather reprioritize (e.g., tackle C7/C8
first since they affect every dev's ability to even run the app locally).
