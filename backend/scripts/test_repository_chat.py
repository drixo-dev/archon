from app.db.neo4j import neo4j_connection
from app.db.postgres import postgres_connection

from services.context_builder import context_builder
from services.llm_service import LLMService
from services.prompt_builder import prompt_builder


REPOSITORY_NAME = "Typer"
QUESTION = "How does shell completion work?"


def test_repository_chat():

    postgres_connection.connect()
    neo4j_connection.connect()

    try:

        repository_context = (
            context_builder.build_context(
                question=QUESTION
            )
        )

        prompt = (
            prompt_builder.build_repository_chat_prompt(
                question=QUESTION,
                repository_context=repository_context,
                repository_name=REPOSITORY_NAME
            )
        )

        llm_service = LLMService()

        answer = (
            llm_service.generate_answer(prompt)
        )

        print()
        print("Repository")
        print(REPOSITORY_NAME)

        print()
        print("Question")
        print(QUESTION)

        print()
        print("-" * 48)

        print()
        print("Retrieved Functions:")
        print(len(repository_context["retrieved_functions"]))

        print()
        print("Same File Functions:")
        print(len(repository_context["same_file_functions"]))

        print()
        print("Dependency Functions:")
        print(len(repository_context["dependency_functions"]))

        print()
        print("Call Neighbor Functions:")
        print(len(repository_context["call_neighbor_functions"]))

        print()
        print("-" * 48)

        print()
        print("Prompt Preview")
        print(prompt[:1000])

        if len(prompt) > 1000:
            print("\n...(Prompt Truncated)...")

        print()
        print("-" * 48)

        print()
        print("AI Answer")
        print(answer)

    finally:
        neo4j_connection.close()
        postgres_connection.close()


if __name__ == "__main__":
    test_repository_chat()