import os

prompt_builder_content = """from app.config import settings

class PromptBuilder:
    OVERVIEW_QUESTION = "Explain the architecture, main components, and purpose of this repository."

    OVERVIEW_SCHEMA = '''{
  "repository_summary": {
    "purpose": ["...", "..."],
    "primary_users": ["...", "..."]
  },
  "technology_stack": {
    "languages": ["..."],
    "frameworks": ["..."],
    "databases": ["..."],
    "libraries": ["..."]
  },
  "architecture": {
    "pattern": "...",
    "style": "...",
    "summary": ["...", "..."],
    "high_level_flow": {
      "diagram": "ASCII Diagram",
      "steps": ["...", "..."]
    },
    "key_design_decisions": ["...", "..."]
  },
  "important_modules": [
    {
      "module": "...",
      "purpose": "...",
      "importance": "High | Medium | Low",
      "why_it_matters": "...",
      "recommended_to_read_after": "..."
    }
  ],
  "entry_points": ["...", "..."],
  "learning_path": [
    {
      "step": 1,
      "title": "...",
      "difficulty": "Easy | Medium | Hard",
      "estimated_time": "15 min",
      "files": ["...", "..."],
      "why": "..."
    }
  ],
  "suggested_questions": {
    "understanding": ["..."],
    "architecture": ["..."],
    "navigation": ["..."],
    "learning": ["..."],
    "modification": ["..."]
  },
  "confidence": {
    "level": "High | Medium | Low",
    "reason": "...",
    "evidence": {
      "files_used": 0,
      "functions_used": 0,
      "graph_expansion": "1 hop",
      "assumptions": 0
    }
  }
}'''

    CONFIDENCE_JSON_SCHEMA = '''```json
{
    "confidence": {
        "level": "High | Medium | Low",
        "reason": "...",
        "evidence": {
            "files_used": 0,
            "functions_used": 0,
            "graph_expansion": "1 hop",
            "assumptions": 0
        }
    }
}
```'''

    def build_repository_chat_prompt(
        self,
        question: str,
        repository_context: dict,
        repository_name: str = "Unknown Repository",
        response_mode: str = "concise"
    ) -> str:
        context_text = self._format_repository_context(repository_context)
        
        metadata = repository_context.get("metadata", {})
        metadata_text = f"Files: {metadata.get('files', 0)}\\nFunctions: {metadata.get('functions', 0)}\\nGraph Expansion: {metadata.get('graph_expansion', '0 hops')}"

        return f\"\"\"
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
- Do NOT hallucinate confidence. Use the retrieval statistics provided to determine your confidence level.

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

{self.CONFIDENCE_JSON_SCHEMA}

Repository: {repository_name}

Question: {question}

Response Mode: {response_mode}

Retrieval Metadata:
{metadata_text}

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
        max_lines: int = settings.SOURCE_TRUNCATION_MAX_LINES,
        max_characters: int = settings.SOURCE_TRUNCATION_MAX_CHARACTERS
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
        
        metadata = repository_context.get("metadata", {})
        metadata_text = f"Files: {metadata.get('files', 0)}\\nFunctions: {metadata.get('functions', 0)}\\nGraph Expansion: {metadata.get('graph_expansion', '0 hops')}"
        
        return f\"\"\"
You are Archon, a premium AI Repository Intelligence Platform.

Generate a comprehensive Technical Design Document and Repository Overview.
Your output must feel like a premium, automatically generated technical report.

Your response MUST be valid JSON. Do not include markdown code blocks or any other text outside the JSON.

Rules:
- Write in concise bullet arrays instead of long string paragraphs. The frontend will render bullets.
- In `architecture.high_level_flow`, provide an ASCII diagram and a step-by-step list of the execution flow based on retrieved evidence.
- Important Modules should explain the purpose, importance level, and why it matters.
- Learning Path must estimate time based on complexity and explicitly guide the user through files.
- Suggested Questions must be repository-specific and categorized. Avoid generic questions.
- Provide a Confidence metadata block at the end, using the provided retrieval metadata. Do NOT hallucinate confidence.
- Base all insights strictly on evidence from the repository. Do NOT invent information or hallucinate.

Required JSON Schema:
{self.OVERVIEW_SCHEMA}

Repository: {repository_name}

Retrieval Metadata:
{metadata_text}

Repository Context:
{context_text}
\"\"\".strip()


prompt_builder = PromptBuilder()
"""

with open('backend/services/prompt_builder.py', 'w') as f:
    f.write(prompt_builder_content)

print("prompt_builder.py updated successfully!")
