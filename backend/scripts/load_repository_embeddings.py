from app.db.neo4j import (
    neo4j_connection
)

from app.db.postgres import (
    postgres_connection
)

from services.graph_service import (
    graph_service
)

from services.embedding_service import (
    embedding_service
)

from repositories.embedding_repository import (
    embedding_repository
)


def load_repository_embeddings():

    # Connect databases
    neo4j_connection.connect()
    postgres_connection.connect()

    functions = (
        graph_service.get_all_functions()
    )

    print(
        f"Loaded {len(functions)} functions"
    )

    total = len(functions)

    for index, function in enumerate(
        functions,
        start=1
    ):

        print(
            f"[{index}/{total}] "
            f"{function['qualified_name']}"
        )

        embedding = (
            embedding_service.generate_embedding(
                function["source_code"]
            )
        )

        embedding_repository.insert_embedding(
            embedding_id=function[
                "qualified_name"
            ],
            file_path=function[
                "file_path"
            ],
            source_code=function[
                "source_code"
            ],
            embedding=embedding
        )

    # Close databases
    postgres_connection.close()
    neo4j_connection.close()

    print(
        "\nRepository embedding load complete."
    )


if __name__ == "__main__":
    load_repository_embeddings()