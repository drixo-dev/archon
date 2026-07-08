from app.db.neo4j import neo4j_connection
from app.db.postgres import postgres_connection
from services.chat_service import chat_service


REPOSITORY_NAME = "Typer"
QUESTION = "How does shell completion work?"


def test_repository_chat():
    postgres_connection.connect()
    neo4j_connection.connect()

    try:
        result = chat_service.chat(
            repository=REPOSITORY_NAME,
            question=QUESTION
        )
        repository_context = result["context"]

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
        print("AI Answer")
        print(result["answer"])
    finally:
        neo4j_connection.close()
        postgres_connection.close()


if __name__ == "__main__":
    test_repository_chat()
