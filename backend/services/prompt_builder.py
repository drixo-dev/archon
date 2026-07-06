class PromptBuilder:

    def build_repository_chat_prompt(
        self,
        question: str,
        repository_context: dict,
        repository_name: str = "Unknown Repository"
    ) -> str:
        context_text = self._format_repository_context(
            repository_context
        )

        return f"""
You are an AI software architect.

Answer the user's question using only the supplied repository context.

If the repository context is not enough to answer confidently, say that the
context is insufficient and explain what is missing.

Do not invent files, functions, or behavior that are not present in the
repository context.

Repository:

{repository_name}

Question:

{question}

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
        max_lines: int = 30,
        max_characters: int = 1000
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


prompt_builder = PromptBuilder()
