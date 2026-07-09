class PromptBuilder:

    def build_repository_chat_prompt(
        self,
        question: str,
        repository_context: dict,
        repository_name: str = "Unknown Repository",
        response_mode: str = "concise"
    ) -> str:
        context_text = self._format_repository_context(repository_context)
        
        metadata = repository_context.get("metadata", {})
        metadata_text = f"Files: {metadata.get('files', 0)}\nFunctions: {metadata.get('functions', 0)}\nGraph Expansion: {metadata.get('graph_expansion', '0 hops')}"

        return f"""
You are Archon, a premium AI Repository Intelligence Platform.

Purpose:
Act as a world-class principal engineer helping developers understand unfamiliar repositories. Your responses should feel like a premium, auto-generated technical design document.

Rules:
- Never invent implementation details. Do not hallucinate.
- Use only evidence from the repository context. If context is insufficient, explicitly state what additional files or modules would help instead of hallucinating.
- Maintain consistent terminology.
- Provide beginner-friendly explanations.
- Avoid repeating the execution flow across multiple sections. Architecture should be high-level components. Execution Flow is a single, concise path. Code Walkthrough tracks the actual function calls.
- Use concise bullet points instead of long paragraphs.
- For Relevant Files, explicitly explain what each file does based on context (e.g., "router.py - Entry point for the API"). Do not just list the files.
- The Code Walkthrough must trace the execution path function-by-function (e.g., `1. initialize() -> 2. process_data()`), noting the Purpose of each step. Do not restate the architecture here.
- The Learn Next section must provide a sequential reading path of the retrieved files to guide a developer through reading the implementation (e.g., `api.py -> service.py -> models.py`).
- At the end, provide a Confidence rating (High / Medium / Low) with a specific Reason based on the context provided. Never hallucinate confidence.
- Finally, include a Context Used section with the exact provided retrieval metadata.

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

# Context Used

Repository: {repository_name}

Question: {question}

Response Mode: {response_mode}

Retrieval Metadata:
{metadata_text}

Repository Context:
{context_text}

Answer:
""".strip()

    def _format_repository_context(self, repository_context: dict) -> str:
        feature_files = repository_context.get("feature_files", [])
        if not feature_files:
            return "No context found."
            
        sections = []
        for f in feature_files:
            file_path = f.get("file_path", "")
            score = f.get("score", 0)
            dependencies = ", ".join(f.get("dependencies", []))
            
            section = f"File: {file_path} (Relevance Score: {score})\n"
            if dependencies:
                section += f"Dependencies: {dependencies}\n"
                
            funcs = []
            for func in f.get("functions", []):
                funcs.append(self._format_function(func))
                
            section += "\n" + "\n\n".join(funcs)
            sections.append(section)
            
        return "\n\n---\n\n".join(sections)

    def _format_function(self, function: dict) -> str:
        return f"""
Function: {function.get("qualified_name")}
Source:
```python
{self._truncate_source(function.get("source_code"))}
```
""".strip()

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
        truncated_source = "\n".join(truncated_lines)

        if len(truncated_source) > max_characters:
            truncated_source = truncated_source[:max_characters]

        was_truncated = len(lines) > max_lines or len(source_code) > len(truncated_source)

        if was_truncated:
            return f"{truncated_source}\n..."

        return truncated_source

    def build_repository_overview_prompt(
        self,
        repository_name: str,
        repository_context: dict
    ) -> str:
        context_text = self._format_repository_context(repository_context)
        
        return f"""
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
""".strip()


prompt_builder = PromptBuilder()
