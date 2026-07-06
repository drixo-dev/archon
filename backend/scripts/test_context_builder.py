from app.db.neo4j import (
    neo4j_connection
)
from app.db.postgres import (
    postgres_connection
)
from services.context_builder import (
    context_builder
)


def print_section(
    title: str,
    functions: list[dict]
):
    print(f"\n{title}")
    print("-" * len(title))

    if not functions:
        print("No functions found.")
        return

    for function in functions:
        print(function["qualified_name"])


def test_context_builder():
    postgres_connection.connect()
    neo4j_connection.connect()

    question = "shell completion"

    context = (
        context_builder.build_context(
            question=question,
            retrieval_limit=3
        )
    )

    print("\nQuestion:")
    print(context["question"])

    print_section(
        "Retrieved functions",
        context["retrieved_functions"]
    )

    print_section(
        "Same-file functions",
        context["same_file_functions"]
    )

    print_section(
        "Call-neighbor functions",
        context["call_neighbor_functions"]
    )

    print_section(
        "Dependency functions",
        context["dependency_functions"]
    )

    neo4j_connection.close()
    postgres_connection.close()


if __name__ == "__main__":
    test_context_builder()
