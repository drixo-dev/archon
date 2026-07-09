import os

context_builder_content = """from repositories.embedding_repository import embedding_repository
from services.embedding_service import embedding_service
from services.graph_service import graph_service

class ContextBuilder:

    def build_context(
        self,
        question: str,
        retrieval_limit: int = 30,
        same_file_limit: int = 3,
        dependency_limit: int = 3,
        call_neighbor_limit: int = 4,
        max_total_functions: int = 12,
        repository_id: str | None = None
    ):
        query_embedding = embedding_service.generate_embedding(question)

        matches = embedding_repository.search_similar(
            query_embedding=query_embedding,
            limit=retrieval_limit,
            repository_id=repository_id
        )

        retrieved_functions = [
            self._function_from_search_result(result)
            for result in matches
        ]

        return self.expand_context(
            question=question,
            retrieved_functions=retrieved_functions,
            repository_id=repository_id,
            same_file_limit=same_file_limit
        )

    def expand_context(
        self,
        question: str,
        retrieved_functions: list[dict],
        repository_id: str | None = None,
        same_file_limit: int = 3
    ):
        # 1. Group by source file
        candidate_files = {}
        for func in retrieved_functions:
            fp = func["file_path"]
            if fp not in candidate_files:
                candidate_files[fp] = []
            candidate_files[fp].append(func)

        # 2. Score each file
        all_stats = graph_service.get_file_statistics_for_folders(repository_id) if repository_id else []
        stats_by_file = {s["path"]: s for s in all_stats}

        scored_files = []
        for fp, funcs in candidate_files.items():
            semantic_score = len(funcs) * 10
            stats = stats_by_file.get(fp, {"incoming_deps": 0, "outgoing_deps": []})
            
            proximity_score = 0
            for dep in stats.get("outgoing_deps", []):
                if dep in candidate_files:
                    proximity_score += 5
                    
            call_frequency = stats.get("incoming_deps", 0) * 2
            
            total_score = semantic_score + proximity_score + call_frequency
            scored_files.append({
                "file_path": fp,
                "score": total_score,
                "functions": funcs,
                "dependencies": stats.get("outgoing_deps", []),
                "incoming_deps": stats.get("incoming_deps", 0)
            })

        # Sort and take top 5
        scored_files.sort(key=lambda x: x["score"], reverse=True)
        top_files = scored_files[:5]

        # 3. Expand to related files/functions using Neo4j
        feature_files = []
        for f in top_files:
            file_funcs = graph_service.get_functions_by_file(f["file_path"], limit=max(5, same_file_limit))
            seen = {fn["qualified_name"] for fn in f["functions"]}
            merged_funcs = list(f["functions"])
            for fn in file_funcs:
                if fn["qualified_name"] not in seen:
                    merged_funcs.append(fn)
                    seen.add(fn["qualified_name"])

            feature_files.append({
                "file_path": f["file_path"],
                "score": f["score"],
                "functions": merged_funcs,
                "dependencies": f["dependencies"]
            })

        return {
            "question": question,
            "feature_files": feature_files
        }

    def _function_from_search_result(self, result):
        return {
            "qualified_name": result[0],
            "file_path": result[1],
            "source_code": result[2]
        }

context_builder = ContextBuilder()
"""

prompt_builder_content = """class PromptBuilder:

    def build_repository_chat_prompt(
        self,
        question: str,
        repository_context: dict,
        repository_name: str = "Unknown Repository",
        response_mode: str = "concise"
    ) -> str:
        context_text = self._format_repository_context(repository_context)

        return f\"\"\"
You are Archon, a premium AI Repository Intelligence Platform.

Purpose:
Act as a world-class principal engineer helping developers understand unfamiliar repositories. Your responses should feel like a premium, auto-generated technical design document.

Rules:
- Never invent implementation details. Do not hallucinate.
- Use only evidence from the repository context. If context is insufficient, explicitly state what additional files or modules would help instead of hallucinating.
- Maintain consistent terminology.
- Provide beginner-friendly explanations.
- Always include a TL;DR first.
- Use numbered explanations for step-by-step logic.
- Include ASCII architecture diagrams and flow diagrams where appropriate.
- Highlight important files and important functions.
- Explain core concepts used in the code.
- Provide a summary and a "Learn Next" section.
- Use concise bullet points instead of long paragraphs.

Response format:

# TL;DR

# Architecture

# Execution Flow

# Relevant Files

# Relevant Functions

# Step-by-Step Explanation

# ASCII Diagram

# Design Decisions

# Related Components

# Learn Next

Repository: {repository_name}

Question: {question}

Response Mode: {response_mode}

Repository Context:
{context_text}

Answer:
\"\"\".strip()

    def _format_repository_context(self, repository_context: dict) -> str:
        feature_files = repository_context.get("feature_files", [])
        if not feature_files:
            return "No context found."
            
        sections = []
        for f in feature_files:
            file_path = f.get("file_path", "")
            score = f.get("score", 0)
            dependencies = ", ".join(f.get("dependencies", []))
            
            section = f"File: {file_path} (Relevance Score: {score})\\n"
            if dependencies:
                section += f"Dependencies: {dependencies}\\n"
                
            funcs = []
            for func in f.get("functions", []):
                funcs.append(self._format_function(func))
                
            section += "\\n" + "\\n\\n".join(funcs)
            sections.append(section)
            
        return "\\n\\n---\\n\\n".join(sections)

    def _format_function(self, function: dict) -> str:
        return f\"\"\"
Function: {function.get("qualified_name")}
Source:
```python
{self._truncate_source(function.get("source_code"))}
```
\"\"\".strip()

    def _truncate_source(
        self,
        source_code: str | None,
        max_lines: int = 30,
        max_characters: int = 1500
    ) -> str:
        if not source_code:
            return ""

        lines = source_code.splitlines()
        truncated_lines = lines[:max_lines]
        truncated_source = "\\n".join(truncated_lines)

        if len(truncated_source) > max_characters:
            truncated_source = truncated_source[:max_characters]

        was_truncated = len(lines) > max_lines or len(source_code) > len(truncated_source)

        if was_truncated:
            return f"{truncated_source}\\n..."

        return truncated_source

    def build_repository_overview_prompt(
        self,
        repository_name: str,
        repository_context: dict
    ) -> str:
        context_text = self._format_repository_context(repository_context)
        
        return f\"\"\"
You are Archon, a premium AI Repository Intelligence Platform.

Generate a comprehensive Technical Design Document and Repository Overview.
Your output must feel like a premium, automatically generated technical report.

Your response MUST be valid JSON. Do not include markdown code blocks or any other text outside the JSON.

Rules:
- Write in concise bullets instead of long paragraphs.
- Use ASCII diagrams where appropriate (e.g., in high_level_flow).
- Provide beginner-friendly explanations that break down complex systems.
- Use structured sections and maintain consistent terminology.
- Base all insights strictly on evidence from the repository. Do NOT invent information or hallucinate.

Required JSON Schema:
{{
  "repository_summary": {{
    "purpose": "",
    "primary_users": "",
    "architecture_style": ""
  }},
  "technology_stack": {{
    "languages": [],
    "frameworks": [],
    "databases": [],
    "libraries": []
  }},
  "architecture": {{
    "description": "",
    "high_level_flow": ""
  }},
  "important_modules": [],
  "entry_points": [],
  "learning_path": [],
  "suggested_questions": []
}}

Repository: {repository_name}

Repository Context:
{context_text}
\"\"\".strip()


prompt_builder = PromptBuilder()
"""

with open('backend/services/context_builder.py', 'w') as f:
    f.write(context_builder_content)

with open('backend/services/prompt_builder.py', 'w') as f:
    f.write(prompt_builder_content)

print("Files updated successfully!")
