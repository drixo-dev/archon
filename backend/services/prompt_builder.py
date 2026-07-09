class PromptBuilder:

    def build_repository_chat_prompt(
        self,
        question: str,
        repository_context: dict,
        repository_name: str = "Unknown Repository",
        response_mode: str = "concise"
    ) -> str:
        context_text = self._format_repository_context(
            repository_context
        )

        return f"""
You are Archon.

Purpose:
Help developers understand unfamiliar repositories.

Rules:
- Never invent implementation details.
- Use only repository evidence.
- Prefer bullet points.
- Prefer numbered steps.
- Prefer tables.
- Prefer ASCII diagrams.
- Avoid large paragraphs.
- Mention only relevant functions.
- Mention missing context when necessary.

Response format:

# TL;DR

# High-Level Flow

# Step-by-Step

# Important Files

# Important Functions

# Concepts Used

# Summary

# Learn Next

Repository: {repository_name}

Question: {question}

Response Mode: {response_mode}

Repository Context:
{context_text}

Answer:
""".strip()

    def _format_repository_context(
        self,
        repository_context: dict
    ) -> str:
        sections = [
            self._format_function_section(
                title="Retrieved Functions",
                functions=repository_context.get(
                    "retrieved_functions",
                    []
                )
            ),
            self._format_function_section(
                title="Same File Functions",
                functions=repository_context.get(
                    "same_file_functions",
                    []
                )
            ),
            self._format_function_section(
                title="Call Neighbor Functions",
                functions=repository_context.get(
                    "call_neighbor_functions",
                    []
                )
            ),
            self._format_function_section(
                title="Dependency Functions",
                functions=repository_context.get(
                    "dependency_functions",
                    []
                )
            )
        ]

        return "\n\n".join(sections)

    def _format_function_section(
        self,
        title: str,
        functions: list[dict]
    ) -> str:
        if not functions:
            return f"{title}:\nNo functions found."

        formatted_functions = []

        for function in functions:
            formatted_functions.append(
                self._format_function(function)
            )

        return (
            f"{title}:\n"
            + "\n\n".join(formatted_functions)
        )

    def _format_function(
        self,
        function: dict
    ) -> str:
        return f"""
Function: {function.get("qualified_name")}
File: {function.get("file_path")}
Source:
```python
{self._truncate_source(function.get("source_code"))}
```
""".strip()

    def _truncate_source(
        self,
        source_code: str | None,
        max_lines: int = 20,
        max_characters: int = 700
    ) -> str:
        if not source_code:
            return ""

        lines = source_code.splitlines()
        truncated_lines = lines[:max_lines]
        truncated_source = "\n".join(truncated_lines)

        if len(truncated_source) > max_characters:
            truncated_source = (
                truncated_source[:max_characters]
            )

        was_truncated = (
            len(lines) > max_lines
            or len(source_code) > len(truncated_source)
        )

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
Generate a Repository Intelligence Report.

Your response MUST be valid JSON. Do not include markdown code blocks or any other text outside the JSON.

Explicit requirements:
- concise descriptions
- no essays
- ASCII architecture flow
- beginner-friendly learning order
- suggested questions based on the repository

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
