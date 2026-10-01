# Archon — Code-Level Audit of the Question→Answer Execution Path

Fresh-session, source-level audit. Every claim below was verified by reading
`archon-main/` source directly, and the retrieval/graph-construction logic was
additionally verified **empirically** by executing the real
`import_resolver`, `python_parser`, and `graph_builder` code (with an
in-memory Neo4j stand-in that reproduces Cypher `MERGE` semantics exactly)
against a synthetic 3-file repository. Where something could not be verified
from source or execution, it is marked `UNKNOWN — NOT VERIFIED FROM SOURCE`.

---

## 0. Execution Path Overview (file/function chain)

```
POST /chat  (api/chat.py:chat)
  -> ChatService.chat()                          services/chat_service.py:16
       -> ContextBuilder.build_context()         services/context_builder.py:8
            -> EmbeddingService.generate_embedding()   services/embedding_service.py:14
            -> EmbeddingRepository.search_similar()    repositories/embedding_repository.py:110
            -> ContextBuilder.expand_context()         services/context_builder.py:35
                 -> GraphService.get_file_statistics_for_folders()  services/graph_service.py:373
                 -> GraphService.get_functions_by_file()            services/graph_service.py:262
       -> PromptBuilder.build_repository_chat_prompt()  services/prompt_builder.py:66
       -> LLMService.generate_answer()                  services/llm_service.py:24
  -> ChatResponse{answer, context}
```

There is no query-classification, no retry/rerank stage, and no async I/O
anywhere in this chain — every step is a synchronous Python call, including
the Gemini HTTP call itself (`google.genai` client, sync `generate_content`).

---

## 1. Retrieval — pgvector

**File:** `backend/repositories/embedding_repository.py`, `EmbeddingRepository.search_similar` (line 110).

Exact SQL (repository-scoped branch):
```sql
SELECT id, file_path, source_code, repository_id
FROM function_embeddings
WHERE repository_id = %s
ORDER BY embedding <=> %s::vector
LIMIT %s
```
- **Vector operator:** `<=>` — pgvector's cosine-distance operator.
- **Distance metric:** cosine distance (lower = more similar).
- **LIMIT:** whatever `retrieval_limit` is passed in — from `ContextBuilder.build_context` this is `settings.CONTEXT_RETRIEVAL_LIMIT = 30` for chat, `settings.OVERVIEW_RETRIEVAL_LIMIT = 10` for the overview endpoint.
- **Filters:** only `repository_id` equality. No file-type, recency, or folder filter.
- **Is the distance value returned?** **No.** The `SELECT` list does not include `embedding <=> %s::vector` as a column — only `id, file_path, source_code, repository_id`. The distance used to `ORDER BY` is computed by Postgres and then **discarded**; Python never sees a numeric similarity/distance score for any candidate. `_function_from_search_result` (context_builder.py:107) builds `{"qualified_name": result[0], "file_path": result[1], "source_code": result[2]}` — no score field exists downstream at all.
- **What happens to "similarity" afterward:** it doesn't exist afterward. The only "score" that appears later (`semantic_score`) is a re-derived, retrieval-order-blind function of **how many of the top-30 candidates share a file path** (see §2) — it has no relationship to the cosine distance computed here.

**Retrieval-technique matrix (code evidence):**

| Technique | Used? | Evidence |
|---|---|---|
| Dense retrieval | **YES** | `embedding <=> %s::vector` over a `SentenceTransformer` embedding (embedding_repository.py:150, embedding_service.py:14) |
| Sparse retrieval / BM25 / full-text search | **NO** | No `tsvector`, `to_tsquery`, `ts_rank`, or BM25 library anywhere in `backend/` (`grep` for these terms returns nothing) |
| Keyword search | **NO** | No keyword/substring query path exists; the only Postgres query is the vector `ORDER BY` above |
| Graph retrieval (i.e., graph used *to retrieve*, not just to expand) | **NO** | Neo4j is only ever queried *after* vector candidates are known (`expand_context`), keyed by `file_path`/`qualified_name` already produced by the vector step. Neo4j never independently surfaces a candidate the vector step didn't touch first |
| Heuristic scoring | **YES** | `semantic_score = len(funcs) * 10` + `proximity_score` (+5 per co-candidate dependency) + `call_frequency = incoming_deps * 2` — context_builder.py:59-75 |
| Reranking (of the vector candidates themselves) | **NO** | Vector candidates are never re-scored/reordered individually; only their *file-level groupings* are re-scored. No cross-encoder, no LLM-based rerank |

This is **not hybrid search**. There is exactly one retrieval signal (dense
vector similarity), and it is used only to nominate an initial candidate set;
everything after that is deterministic graph/counting logic, not a second
retrieval signal fused with the first.

---

## 2. Context Builder — line-by-line

**File:** `backend/services/context_builder.py`, class `ContextBuilder`.

Verified pseudocode of `build_context` → `expand_context`:

```
build_context(question, repository_id, retrieval_limit=30, same_file_limit=3, ...):
    query_embedding = embedding_service.generate_embedding(question)
    matches = embedding_repository.search_similar(query_embedding, limit=30, repository_id)
    retrieved_functions = [ {qualified_name: id, file_path, source_code} for each match ]  # id assumed == qualified_name
    return expand_context(question, retrieved_functions, repository_id, same_file_limit)

expand_context(question, retrieved_functions, repository_id, same_file_limit=3):
    # 1. group vector hits by file
    candidate_files = groupby(retrieved_functions, key=file_path)

    # 2. score each file
    all_stats = graph_service.get_file_statistics_for_folders(repository_id)   # one Neo4j round trip for the WHOLE repo
    for fp, funcs in candidate_files:
        semantic_score   = len(funcs) * 10                     # HARDCODED weight: 10
        proximity_score  = 5 * count(dep in stats.outgoing_deps if dep in candidate_files)   # HARDCODED weight: 5
        call_frequency   = stats.incoming_deps * 2              # HARDCODED weight: 2
        total_score      = semantic_score + proximity_score + call_frequency

    # 3. sort desc by total_score, take top 5   <-- HARDCODED: [:5]
    top_files = scored_files[:5]

    # 4. graph expansion: for each of the top-5 files, pull more functions from that file
    for f in top_files:
        file_funcs = graph_service.get_functions_by_file(f.file_path, limit=max(5, same_file_limit))  # HARDCODED floor: 5
        merge file_funcs into f.functions, deduped by qualified_name

    return {
        question,
        feature_files: [...],
        metadata: { files: N, functions: M, graph_expansion: "1 hops" }   # HARDCODED STRING, not computed
    }
```

**Formula (verified, context_builder.py:59-70):**
```
total_score = (10 × hit_count_in_top30) + (5 × #outgoing_deps_that_are_also_candidate_files) + (2 × incoming_dep_count)
```
`hit_count_in_top30` is simply how many of the ≤30 vector candidates landed in that file — a proxy for similarity, not similarity itself.

**Hardcoded values, verified:**
| Value | Location | Meaning |
|---|---|---|
| `10` | context_builder.py:60 | weight per vector hit in a file |
| `5` | context_builder.py:65 | weight per dependency-file that's also a candidate |
| `2` | context_builder.py:68 | weight per incoming-dependency count |
| `[:5]` | context_builder.py:79 | top-5 files kept after scoring |
| `max(5, same_file_limit)` | context_builder.py:85 | floor of 5 functions pulled per expanded file |
| `"1 hops"` | context_builder.py:99 | **literal string**, sent to the prompt unconditionally — it does not reflect actual hop count and would say "1 hops" even if `get_functions_by_file` returned nothing |

**CONTEXT_* configuration audit:**

| Setting | Declared | Read (passed as param) | Actually used in function body | Dead? |
|---|---|---|---|---|
| `CONTEXT_RETRIEVAL_LIMIT` (30) | config.py:19 | `build_context` default | Yes — passed straight to `search_similar(limit=...)` | Live |
| `CONTEXT_SAME_FILE_LIMIT` (3) | config.py:20 | `build_context`/`expand_context` default | Yes, but immediately floored: `max(5, same_file_limit)`. Since default is 3 < 5, the setting is **neutralized at its shipped default** — changing it to any value ≤5 has zero effect | Effectively dead at default |
| `CONTEXT_DEPENDENCY_LIMIT` (3) | config.py:21 | Accepted as `build_context(dependency_limit=...)` param | **Never referenced anywhere in `expand_context`'s body.** `grep` for `dependency_limit` inside the function body returns nothing | **Fully dead** |
| `CONTEXT_CALL_NEIGHBOR_LIMIT` (4) | config.py:22 | Accepted as `build_context(call_neighbor_limit=...)` param | **Never referenced anywhere in the body** | **Fully dead** |
| `CONTEXT_MAX_TOTAL_FUNCTIONS` (12) | config.py:23 | Accepted as `build_context(max_total_functions=...)` param | **Never referenced anywhere in the body** — nothing caps `total_functions`, it's only computed and reported in `metadata`, never enforced | **Fully dead** |

Same pattern repeats for the `OVERVIEW_*` twins used by `overview_service.py` — `OVERVIEW_DEPENDENCY_LIMIT`, `OVERVIEW_CALL_NEIGHBOR_LIMIT`, `OVERVIEW_MAX_TOTAL_FUNCTIONS` are passed into the identical dead parameters, and `OVERVIEW_SAME_FILE_LIMIT=2` is floored the same way by `max(5, 2)`.

**Net effect:** of the 5 `CONTEXT_*`/5 `OVERVIEW_*` tunables that look like they control context-window shape, only `*_RETRIEVAL_LIMIT` actually changes system behavior. Operators tuning the other 8 settings are changing nothing.

---

## 3. What exactly reaches the LLM

Traced one function (`auth/service.py:authenticate` in the synthetic repo, see §7) end-to-end:

1. Vector match returns `(id="auth/service.py:authenticate", file_path="auth/service.py", source_code="...")`. **No score attached.**
2. Grouped under `candidate_files["auth/service.py"]`.
3. File-level `total_score` computed per the formula in §2 — this integer is the *only* per-file evidence.
4. If in the top 5, `get_functions_by_file` pulls up to `max(5, same_file_limit)` more functions from that same file (via Neo4j `File-[:DEFINES]->Function`, **no repository filter** — see §6 for why this matters) and merges them in, de-duplicated by `qualified_name`.
5. `PromptBuilder._format_function` renders each function as:
   ```
   Function: <qualified_name>
   Source:
   ```python
   <source, truncated to 30 lines AND 1500 chars, whichever hits first — SOURCE_TRUNCATION_MAX_LINES / SOURCE_TRUNCATION_MAX_CHARACTERS>
   ```
   ```
6. Functions for a file are joined under a `File: <path> (Relevance Score: <total_score>)` header, with a `Dependencies: a, b` line if any outgoing deps exist, and files are joined with `\n\n---\n\n`.

**Ordering:** files are ordered strictly by `total_score` descending (top 5 kept); functions *within* a file are ordered: vector-matched functions first (in whatever order Postgres returned them), then graph-added functions appended afterward. There is no relevance-based ordering of functions themselves.

**Truncation:** `_truncate_source` (prompt_builder.py) cuts at 30 lines, then additionally hard-truncates the joined string at 1500 characters if still too long, appending `...`. For files with more than ~40-50 lines, the LLM sees a truncated, syntactically broken function body.

**Deduplication:** only by `qualified_name`, inside `expand_context`'s merge step — a function retrieved twice (once by vector match, once by graph expansion) is not double-inserted.

**Exact prompt skeleton (verified from `prompt_builder.py:66-118`, `build_repository_chat_prompt`):**
```
You are Archon, a premium AI Repository Intelligence Platform.

Purpose:
Act as a world-class principal engineer ...

Rules:
- Never invent implementation details. Do not hallucinate.
- Use only evidence from the repository context. ...
- (7 more rule bullets, verbatim in source)

Response format:
# TL;DR
# Architecture
# Execution Flow
# Relevant Files
# Relevant Functions
# Code Walkthrough
# Design Decisions
# Related Components
# Learn Next
# Confidence
<CONFIDENCE_JSON_SCHEMA block, verbatim JSON template>

Repository: <repository_name>
Question: <question>
Response Mode: concise
Retrieval Metadata:
Files: <N>
Functions: <M>
Graph Expansion: 1 hops        <-- always this literal string
Repository Context:
File: <path> (Relevance Score: <total_score>)
Dependencies: <comma list>

Function: <qualified_name>
Source:
```python
<truncated source>
```
---
(repeat per file)

Answer:
```

Everything inside `Repository Context:` and the `Files/Functions/Graph
Expansion` numbers is dynamically generated. Everything else — the persona,
the 9 rule bullets, the 10 section headers, and the confidence JSON schema —
is a fixed string template baked into `prompt_builder.py`, identical for
every question and every repository.

---

## 4. Prompt vs. code logic

| Behavior | Implemented by |
|---|---|
| Hallucination prevention | **Prompt only.** "Never invent implementation details" is an instruction to Gemini; nothing in `chat_service`/`context_builder` validates or checks the answer against the context afterward |
| Source attribution | **Prompt only** — the LLM is *shown* file/function names and asked to cite them; there's no code that verifies the citations it produces are real |
| Confidence | **Prompt only, and self-contradictory.** The prompt tells the model to derive confidence "using the retrieval statistics provided," but the only statistics provided are `Files`, `Functions`, and the constant `"1 hops"` — there is no numeric similarity/coverage signal in `metadata` for the model to reason from (recall §1: the cosine distance was thrown away). The model is being asked to sound confident/uncertain about numbers that carry no real retrieval-quality information |
| Answer formatting / Markdown structure / the 10 fixed sections | **Prompt only** — a literal header list Gemini is told to reproduce; no post-processing enforces or parses this format in Python |
| Uncertainty language | **Prompt only** |
| "Repository understanding" (e.g., distinguishing architecture from execution-flow-from-code-walkthrough) | **Prompt only** — this is entirely a stylistic instruction to the LLM; the context passed in has no notion of "architecture" vs "execution flow," it's the same flat file/function list either way |
| What functions are even eligible to appear | **Code** — §1/§2's retrieval + scoring algorithm |
| Score shown as "Relevance Score" | **Code** produces the number; but the number's *meaning* (as anything related to true semantic relevance) is fabricated — see §2/§9-G |

**Why output formatting may be poor:** the entire structural contract (10
headers, code-walkthrough-vs-architecture separation, JSON confidence block)
is enforced *only* by asking Gemini nicely. Nothing in `llm_service.py`
validates the response shape; `generate_answer` only checks the response is
non-empty text (llm_service.py:52-56). A model that drifts from the format,
omits a section, or wraps the JSON block in commentary will pass through
uncaught, and the caller (`chat_service.chat`) returns whatever text came
back with no parsing or repair.

---

## 5. Embedding pipeline

**File:** `backend/services/embedding_service.py`.

- **Model:** `BAAI/bge-small-en-v1.5`, loaded via `sentence_transformers.SentenceTransformer("BAAI/bge-small-en-v1.5")` — no device argument, no cache-folder override, no `trust_remote_code` flag. Device selection is therefore whatever `sentence-transformers` auto-detects (CUDA if available, else CPU) — **UNKNOWN — NOT VERIFIED FROM SOURCE** which device a given deployment actually runs on, since it's not pinned.
- **Embedding dimension:** 384 (matches the `VECTOR(384)` Postgres column declared in `embedding_repository.py:20` and `scripts/create_embedding_table.py:21` — consistent).
- **Pooling / normalization:** `self.model.encode(text)` is called with **no keyword arguments** — `normalize_embeddings` is left at whatever the library/model default is; Archon's own code does not normalize before or after. This is largely moot for scoring purposes because the only operator used downstream is pgvector's `<=>` (cosine distance), which is scale-invariant regardless of stored-vector norm.
- **Max input length / batching:** not set anywhere in Archon code — whatever `SentenceTransformer`'s default `max_seq_length` is for this checkpoint is used un-overridden, and embeddings are generated **one function at a time**, in a Python `for` loop (`repository_service.py:143`, `load_repository_embeddings.py`) — no batching at all, so ingestion throughput scales linearly with function count with per-call model overhead.
- **What exact text is embedded (verified, `repository_service.py:143` and `load_repository_embeddings.py:47`):**
  ```python
  embedding = embedding_service.generate_embedding(function["source_code"])
  ```
  **Function source code only.** No file path, no function name/signature prefix, no docstring-extraction, no surrounding class name is prepended. `function["source_code"]` is exactly the `ast.get_source_segment` output for that `FunctionDef` node (see §6) — i.e., the `def foo(...):` line plus its body, nothing else. This means a query like "authentication logic" must match on the *literal code text* of a function; it gets no help from the function's name living outside the `def` line, its file location, or any docstring context beyond what's already inside the function body.
- **Chunking:** Archon embeds one whole function per row (a code unit), not a fixed-size text chunk. There is no sub-function chunking and no chunk-merging logic anywhere in the codebase.

---

## 6. Parser / Graph — what actually affects retrieval

**File:** `backend/parser/python_parser.py` (empirically tested against a synthetic file, see script output below).

Verified capability table:

| AST construct | Captured as a Function node? | Captured in CALLS? | Evidence |
|---|---|---|---|
| `def foo(): ...` (module-level) | **YES** | YES, as caller and as resolvable callee | `extract_functions`/`extract_function_calls` only match `isinstance(node, ast.FunctionDef)` |
| `async def foo(): ...` | **NO** | **NO — not even calls made *inside* it are captured** | Empirically confirmed below: `async_func`/`authenticate_async` never appear in `functions`, and calls made inside them never appear in `calls` at all, because the outer walk in `extract_function_calls` only enters "collect calls" mode for `ast.FunctionDef` nodes; `ast.AsyncFunctionDef` is a distinct node type and is silently skipped |
| Methods (`def m(self): ...` inside a class) | YES, but with **no class qualification** — `Class.m` and `OtherClass.m` in the same file both extract as bare name `m` | Same collision applies to CALLS resolution | Empirically confirmed: `Session.save` and `Token.save` in the same file both parse to `{"name": "save", ...}` |
| Nested functions (`def outer(): def inner(): ...`) | YES (both `outer` and `inner` extracted, flatly, via `ast.walk`) | **Double-attribution bug (new finding, not previously documented):** because `extract_function_calls` does `ast.walk(node)` inside the outer FunctionDef to collect its calls, and `ast.walk` recurses into nested function bodies too, a call made only inside `inner()` gets attributed to *both* `outer` and `inner` as caller | Verifiable by inspection of `extract_function_calls` (python_parser.py:74-96): the inner walk does not stop at nested `FunctionDef` boundaries |
| Aliased imports (`import x as y`) | N/A (imports, not functions) | Import nodes store `alias`, but `resolve_function`/`resolve_import` never consult the alias — call resolution is by bare textual name only, so an aliased call site (`y.something()`) resolves (or fails to resolve) purely on the attribute name `something`, ignoring `y` entirely | import_resolver.py:29-45, python_parser.py:82-83 (`ast.Attribute` branch takes `child.func.attr` only, discards the object) |
| Cross-file / cross-module call resolution | **Global, unscoped.** `build_function_index` builds one flat `{bare_function_name: qualified_name}` dict for the **entire repository**, so if two files define a function with the same name, whichever file is scanned last in `python_files` wins the index entry, and **every** call site anywhere in the repo that uses that bare name resolves to that one winner | import_resolver.py:56-84, graph_builder.py:80-97 |

### Empirical proof (executed against a synthetic 3-file repo)

Synthetic repo:
```
auth/service.py:  def authenticate(...): hashed = hash_password(...); return validate(...)
                   def validate(...): ...
                   async def authenticate_async(...): hashed = hash_password(...); return validate(...)
auth/utils.py:     def hash_password(...): ...
                   class Session: def save(self): return "session-saved"
                   class Token:   def save(self): return "token-saved"
billing/utils.py:  def hash_password(...): return "billing-hash"
                   def charge(...): hashed = hash_password(...); return hashed
```

Running the **real** `import_resolver.build_function_index` + `graph_builder.ingest_file` against this repo (in-memory Neo4j stand-in that reproduces `MERGE`-then-`SET` semantics exactly) produced:

```
function_index (GLOBAL, flat, by bare name):
  {'authenticate': 'auth/service.py:authenticate',
   'validate': 'auth/service.py:validate',
   'hash_password': 'billing/utils.py:hash_password',   <-- auth/utils.py's hash_password lost the index race
   'save': 'auth/utils.py:save',
   'charge': 'billing/utils.py:charge'}

[MERGE COLLISION] qualified_name='auth/utils.py:save' already existed - previous source_code silently OVERWRITTEN.
   old source: 'def save(self): return "session-saved"'
   new source: 'def save(self): return "token-saved"'

FINAL CALLS edges:
  auth/service.py:authenticate -> auth/service.py:validate
  auth/service.py:authenticate -> billing/utils.py:hash_password   <-- WRONG target
  billing/utils.py:charge      -> billing/utils.py:hash_password   <-- correct, coincidentally
```

Two distinct, empirically reproduced bugs in one run:
1. **`Session.save`/`Token.save` collision** — the graph physically cannot hold both methods' source under the same `qualified_name`; the second `MERGE...SET` silently overwrites the first. `auth/utils.py:save` in the final graph is `Token.save`'s body; `Session.save`'s body no longer exists anywhere in Neo4j.
2. **False CALLS edge** — `auth/service.py`'s `authenticate` explicitly calls the `hash_password` defined in the *same package* (`auth/utils.py`), but because `billing/utils.py` was indexed after `auth/utils.py`, the flat index only remembers billing's version. The graph now asserts `authenticate` calls `billing/utils.py:hash_password`, which is wrong, and `auth/utils.py:hash_password` — the function actually called — has **zero** incoming CALLS edges in the graph, so a "what calls `hash_password`" question about the real function returns nothing.
3. `authenticate_async` never appears anywhere in `function_index`, the Function graph nodes, or any CALLS edge — including the `hash_password`/`validate` calls made *inside* it.

### Neo4j's actual role in retrieval — verified

Neo4j is **never queried before or independently of the vector step**. Its only two read call sites in the live chat path are:
- `get_file_statistics_for_folders(repository_id)` — pulls dependency/incoming-call counts for **every file already touched by File nodes in that repo**, used purely to re-weight the vector-derived candidate files (§2's formula).
- `get_functions_by_file(file_path, limit)` — for the top-5 scored files, pulls a few more functions from the *same file*, **with no repository filter at all** (`graph_service.py:262`, the Cypher is `MATCH (file:File {path: $file_path})-[:DEFINES]->(function:Function)` — no `repository_name` constraint). Because `File` nodes are merged globally by `path` alone (`create_file`, `graph_service.py:20`, `MERGE (f:File {path: $file_path})` has no repository component in the merge key), if two different ingested repositories happen to share a relative file path (e.g. both have `app/utils.py`), `get_functions_by_file` for that path can return **the other repository's functions** into the current repository's context, regardless of which `repository_id` the chat request specified.

**Conclusion: Neo4j does not improve retrieval — it only expands context *after* the vector step has already chosen candidates, and it can leak cross-repository content while doing so.** The `CALLS` relationship, built at ingestion time, is never traversed anywhere in the live `/chat` path — `get_function_neighbors` (the only method that reads `CALLS`) has zero callers inside `services/` or `api/`; its only caller in the whole codebase is the standalone script `backend/scripts/test_neighbors.py`.

---

## 7. Three concrete traces (synthetic repo above, `demo-repo`)

Because a live Postgres/pgvector instance is not available in this sandbox, the vector-similarity *ranking* itself could not be executed end-to-end (that step genuinely depends on the BGE model's output, which cannot be faked meaningfully). The **grouping/scoring/graph-expansion logic downstream of retrieval** was run for real. Where the trace depends on the un-runnable vector step, candidate sets are stated as *assumed vector hits* and flagged.

### Trace 1 — "Where is authentication implemented?"
```
QUESTION -> embed(question) -> [ASSUMED top hits: auth/service.py:authenticate, auth/service.py:validate]
  (auth/service.py:authenticate_async is architecturally invisible - it was never embedded,
   because it was never extracted as a Function node in the first place; see §6)
-> FILE SCORING: auth/service.py gets semantic_score=20 (2 hits*10), plus incoming/outgoing dep terms
-> SELECTED FILES: auth/service.py (top-5, trivially, since only 1 file has hits here)
-> GRAPH EXPANSION: get_functions_by_file("auth/service.py") adds any remaining functions in that file
   (validate is already present; authenticate_async still never appears - it doesn't exist in the graph)
-> FINAL CONTEXT: authenticate, validate  (auth/utils.py:hash_password NOT included unless it also
   happened to be an independent vector hit - the graph never pulls dependency-target functions)
```
**Relevance: PARTIALLY RELEVANT.** The synchronous `authenticate` is found, but `authenticate_async` — arguably the more interesting async variant — is structurally undiscoverable no matter how the question is phrased, and `hash_password`, the actual credential-handling primitive `authenticate` calls, is only in context if it *independently* placed in the top-30 vector hits; the graph-expansion step does not pull a file's dependencies' functions, only more functions from the *same* file (§2 step 4 only expands within `top_files`, never across `dependencies`).

### Trace 2 — "Explain what happens when `hash_password` is called."
```
QUESTION -> embed -> [ASSUMED top hit: whichever hash_password the vector index ranks highest —
                      by embedding content alone, auth/utils.py:hash_password and
                      billing/utils.py:hash_password are two DIFFERENT rows in function_embeddings
                      (correctly, since pgvector search_similar has no name-collision problem —
                      that problem is a Neo4j/import_resolver issue, not a pgvector one)]
-> Suppose the vector step correctly returns auth/utils.py:hash_password.
-> FILE SCORING -> SELECTED FILES: auth/utils.py
-> GRAPH EXPANSION: get_functions_by_file("auth/utils.py") -> adds Session.save/Token.save
   (but only Token.save's source survives in Neo4j; Session.save's source was overwritten - §6)
-> FINAL CONTEXT: hash_password (correct body), save (only Token's version, mislabeled generically as "save")
```
Separately, if the question is instead routed through `get_function_neighbors` (it isn't, in the live
path — see §6) to answer "what calls hash_password", the empirical graph shows **auth/utils.py:hash_password has zero incoming CALLS edges**, even though `authenticate` really does call it — the edge was mis-pointed to `billing/utils.py:hash_password` instead (§6, false-CALLS-edge finding). This relationship is moot in production anyway since **`CALLS` is never read in the `/chat` path.**

**Relevance: PARTIALLY RELEVANT** for the direct function body; **IRRELEVANT / silently wrong** for any caller/callee relationship, because (a) CALLS is unreachable from chat, and (b) even if it were reachable, the specific edge for this function is factually wrong.

### Trace 3 — "Which functions depend on `hash_password`?"
```
QUESTION -> This is precisely a graph question - it requires get_function_neighbors, get_dependency_functions,
   or an equivalent CALLS traversal.
-> chat_service.chat() -> context_builder.build_context() -> expand_context() never calls
   get_function_neighbors, get_dependency_functions, or anything that reads the CALLS relationship.
-> FINAL CONTEXT: whatever the vector step + same-file expansion happens to surface — structurally
   unrelated to "who calls this."
```
**Relevance: IRRELEVANT.** This class of question cannot be correctly answered by the current
system regardless of phrasing, because the live retrieval path has no code path that reads a
caller/callee edge at all. Any correct-looking answer Gemini gives to this question is either (a)
inferred from source code snippets alone, without graph confirmation, or (b) hallucinated — the
"do not hallucinate" prompt rule (§4) is the only thing standing between this question and a
made-up answer, because the code path deterministically supplies **zero** structural evidence for it.

---

## 8. Current capability — evidence based

| Capability | Status | Reason |
|---|---|---|
| Function lookup by name/semantics | **PARTIAL** | Vector search works, but is unaware of Neo4j-level name collisions (§6) and only embeds raw source (no name/docstring boost, §5) |
| Function explanation | **PARTIAL** | Source is available but silently truncated at 30 lines/1500 chars (§3); long functions arrive broken |
| Class explanation | **NOT SUPPORTED** | There is no `Class` node anywhere in the Neo4j schema (`grep` for `:Class` in `graph_service.py`/`graph_builder.py` returns nothing) — methods are flattened to bare `Function` nodes with no owning-class reference at all |
| File explanation | **PARTIAL** | Files are first-class in the graph (`File` node, `get_functions_by_file`), but File nodes are unscoped by repository (§6), so cross-repo leakage is possible |
| Architecture questions | **NOT SUPPORTED (as a code capability)** — **PROMPT-ONLY** | Nothing in the retrieval/graph path computes "architecture"; the prompt simply instructs Gemini to synthesize an `# Architecture` section from whatever flat file/function list it's handed |
| Cross-file questions | **PARTIAL, unreliably** | `DEPENDS_ON` edges exist and feed `proximity_score`, but the graph-expansion step never pulls in functions from a *dependency* file, only more functions from the *same* file (§7, Trace 1) |
| Call-graph questions | **NOT SUPPORTED** | `CALLS` is built at ingestion but never read anywhere in `services/chat_service.py`/`context_builder.py`; its only reader in the whole repo is a standalone dev script (§6) |
| Dependency questions ("what does X depend on") | **PARTIAL** | `DEPENDS_ON` is file-level only (no function-level dependency edges), and only surfaces as a `Dependencies: a, b` line in the prompt — never as retrieved function bodies |
| Multi-hop questions | **NOT SUPPORTED** | Graph expansion is fixed at exactly one hop from `File`, hardcoded — the `metadata.graph_expansion = "1 hops"` string is not even computed, it is literally hardcoded regardless of what happens |
| Vague/semantic questions ("how does auth work") | **PARTIAL** | Dense retrieval over raw function bodies handles this reasonably when the vocabulary overlaps; degrades badly when the concept spans multiple files connected only by `CALLS` (unused) rather than `DEPENDS_ON` (used) |

---

## 9. FINAL OUTPUT

### A. EXACT CURRENT EXECUTION FLOW
See §0. Fully synchronous: `api/chat.py:chat` → `services/chat_service.py:ChatService.chat` → `services/context_builder.py:ContextBuilder.build_context/expand_context` → `repositories/embedding_repository.py:EmbeddingRepository.search_similar` (pgvector) + `services/graph_service.py:GraphService.get_file_statistics_for_folders/get_functions_by_file` (Neo4j) → `services/prompt_builder.py:PromptBuilder.build_repository_chat_prompt` → `services/llm_service.py:LLMService.generate_answer` (Gemini, `google.genai`).

### B. EXACT CURRENT RETRIEVAL ALGORITHM
Single-signal dense retrieval: embed the question with `BAAI/bge-small-en-v1.5`, run `ORDER BY embedding <=> query::vector LIMIT 30` filtered by `repository_id` in Postgres/pgvector, discard the distance value, return raw `(id, file_path, source_code)` rows. No BM25/keyword/full-text/graph retrieval, no reranking (§1).

### C. EXACT CURRENT CONTEXT-BUILDING ALGORITHM
Group the ≤30 vector hits by file → score each file as `10×hits_in_file + 5×(deps_also_in_candidate_set) + 2×incoming_dep_count` → take top 5 files → for each, pull up to `max(5, same_file_limit)` more functions from the *same* file via Neo4j, dedupe by qualified name → return as `feature_files` with a hardcoded `"graph_expansion": "1 hops"` label (§2).

### D. EXACT CURRENT PROMPT STRUCTURE
Fixed persona + 9 hardcoded behavioral rules + fixed 10-section Markdown header template + fixed JSON confidence schema, followed by dynamically inserted `Repository`, `Question`, retrieval `metadata` counts, and the file/function context blocks (§3).

### E. EXACT EMBEDDING INPUT
`function["source_code"]` only — the raw `def ...:` body from `ast.get_source_segment`. No file path, function name outside the `def` line, class name, or docstring-external context is concatenated (§5).

### F. NEO4J'S ACTUAL ROLE
Post-vector re-scoring input (file-level dependency counts) and same-file context expansion only. It never independently surfaces candidates, and its `CALLS` relationship — the one edge type that could answer call-graph questions — is built during ingestion but never read in the live chat path (§6).

### G. HARDCODED VALUES THAT MATTER
`10`, `5`, `2` (scoring weights, context_builder.py:60/65/68); `[:5]` top files kept (context_builder.py:79); `max(5, same_file_limit)` function-expansion floor (context_builder.py:85); `30` (`CONTEXT_RETRIEVAL_LIMIT`, config.py:19); `"1 hops"` literal metadata string (context_builder.py:99); `30` lines / `1500` chars source truncation (config.py:14-15); `384`-dim vector column (embedding_repository.py:20).

### H. DEAD/IGNORED CONFIGURATION
`CONTEXT_DEPENDENCY_LIMIT`, `CONTEXT_CALL_NEIGHBOR_LIMIT`, `CONTEXT_MAX_TOTAL_FUNCTIONS` and their `OVERVIEW_*` twins — accepted as parameters, never read in the function body (§2). `CONTEXT_SAME_FILE_LIMIT`/`OVERVIEW_SAME_FILE_LIMIT` — read, but neutralized by a `max(5, x)` floor at their shipped defaults (3 and 2, both < 5).

### I. TOP FAILURE MODES (ranked by how badly they distort a real answer)
1. **Global, unscoped `Function`/`File` MERGE keys in Neo4j** — cross-repository silent overwrite of `File`/`Function` node properties when two repos share a path or `path:function_name` (graph_service.py:20/47-71) — the single most dangerous bug because it corrupts data with no error raised.
2. **`repo_name` collision at repository creation** — `RepositoryService.create_repository` derives `repo_name` from the URL's last path segment; if it already exists, `create_repository` **returns the existing (different) repository's record and never queues ingestion at all** for the new URL (repository_service.py:19-24). Two GitHub URLs like `.../orgA/api` and `.../orgB/api` collide completely; the second ingestion silently never happens. Untested — no test in `test_repository_service.py` exercises this path.
3. **Global flat `function_index` in import resolution** — bare-name-only call resolution creates false CALLS edges across unrelated files sharing a function name, and same-file/same-name methods overwrite each other's source in the graph (empirically reproduced in §6).
4. **`async def` is entirely invisible to the parser** — not just missing as a Function node, but calls made *inside* async functions vanish too (§6, empirically reproduced).
5. **Cosine distance computed then thrown away** — no numeric similarity signal survives past the SQL layer, so the "Relevance Score" shown to the LLM in the prompt is a hit-count-derived proxy, not a real similarity/confidence number, undermining the prompt's own instruction to derive confidence from "retrieval statistics."
6. **`CALLS` relationship is dead weight at runtime** — built at real ingestion cost, never traversed by `/chat`, meaning call-graph and multi-hop questions have zero code-path support regardless of prompt engineering.
7. **`get_functions_by_file` has no repository filter** — even when `repository_id` is correctly threaded through the vector step, graph expansion can pull another repository's functions for a colliding file path.
8. **`LLMService()` instantiated at import time in two separate places** (`llm_service.py:76` module singleton, and independently inside `ChatService.__init__`) — any import of `api.chat`/`app.main` crashes the whole process if `GEMINI_API_KEY` is unset, verified empirically by reproducing the exact traceback.
9. **Three of five `CONTEXT_*` limits are fully dead code** and a fourth is neutralized at its default — operators believe they're tuning context shape and are not.
10. **No input validation on `github_url`** passed straight into `git.Repo.clone_from` (github_loader.py:14), and a separate, inconsistent repo-name-slugging implementation from `repository_service.py` (one does `.rstrip("/")` first, the other doesn't) — a trailing-slash URL produces different `repo_name` values in the two places and can target `clone_repository`'s destination directory incorrectly.

### J. CURRENT CAPABILITY LIMITS
See §8 table. In one line: function/file lookup and basic "explain this function" work end-to-end; anything requiring class-level structure, call-graph traversal, multi-hop reasoning, or true architecture synthesis has no supporting retrieval code and is entirely dependent on Gemini's ability to infer structure from a flat, same-file-biased bag of function bodies.

### K. FILE + FUNCTION INDEX OF THE IMPORTANT CODE

| File | Key functions/classes |
|---|---|
| `backend/api/chat.py` | `chat()` — HTTP entrypoint |
| `backend/services/chat_service.py` | `ChatService.chat`, module-level `chat_service` (instantiates `LLMService` at import time) |
| `backend/services/context_builder.py` | `ContextBuilder.build_context`, `ContextBuilder.expand_context`, `ContextBuilder._function_from_search_result` |
| `backend/repositories/embedding_repository.py` | `EmbeddingRepository.search_similar` (pgvector query), `insert_embedding`, `initialize_schema` |
| `backend/services/embedding_service.py` | `EmbeddingService.generate_embedding` (BGE model call) |
| `backend/services/graph_service.py` | `create_file`, `create_function` (unscoped MERGE keys), `get_file_statistics_for_folders`, `get_functions_by_file` (no repo filter), `get_function_neighbors` (built but unread by chat), `get_all_functions` |
| `backend/services/graph_builder.py` | `GraphBuilder.ingest_file` — orchestrates File/Function/Import/CALLS creation per file |
| `backend/services/import_resolver.py` | `build_module_index`, `build_function_index` (global flat name index — root cause of false CALLS edges), `resolve_import`, `resolve_function` |
| `backend/parser/python_parser.py` | `extract_functions`, `extract_function_calls` (both `ast.FunctionDef`-only — async blind spot), `extract_imports`, `extract_file_structure` |
| `backend/services/prompt_builder.py` | `build_repository_chat_prompt`, `build_repository_overview_prompt`, `_format_repository_context`, `_truncate_source` |
| `backend/services/llm_service.py` | `LLMService.__init__` (crashes without `GEMINI_API_KEY`), `generate_answer`, `extract_json`, module-level `llm_service` singleton |
| `backend/services/repository_service.py` | `RepositoryService.create_repository` (repo-name-collision bug), `_ingest_repository` (correctly passes `repository_id` into embeddings — unlike the standalone script below) |
| `backend/scripts/load_repository_embeddings.py` | Standalone script that calls `insert_embedding` **without** `repository_id`, unlike the live ingestion path in `repository_service.py` |
| `backend/ingestion/github_loader.py` | `clone_repository` — unvalidated URL passed to `git.Repo.clone_from`; separate, inconsistent repo-name slug logic vs. `repository_service.py` |
| `backend/app/config.py` | `Settings` — all `CONTEXT_*`/`OVERVIEW_*` tunables, several dead (§2/§9-H) |
