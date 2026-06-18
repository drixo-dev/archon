from app.db.postgres import (
    postgres_connection
)

from services.embedding_service import (
    embedding_service
)

from repositories.embedding_repository import (
    embedding_repository
)


def test_similarity_search():

    postgres_connection.connect()

    query = "shell completion"

    query_embedding = (
        embedding_service.generate_embedding(
            query
        )
    )

    results = (
        embedding_repository.search_similar(
            query_embedding=query_embedding,
            limit=10
        )
    )

    print("\nQuery:")
    print(query)

    print("\nResults:\n")

    for result in results:

        print(
            f"ID: {result[0]}"
        )

        print(
            f"File: {result[1]}"
        )

        print("-" * 50)

    postgres_connection.close()


if __name__ == "__main__":
    test_similarity_search()