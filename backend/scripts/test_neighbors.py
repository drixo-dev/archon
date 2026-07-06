from app.db.neo4j import (
    neo4j_connection
)

from services.graph_service import (
    graph_service
)


def test_neighbors():

    neo4j_connection.connect()

    neighbors = (
        graph_service.get_function_neighbors(
            "typer/completion.py:shell_complete"
        )
    )

    print(neighbors)

    neo4j_connection.close()


if __name__ == "__main__":
    test_neighbors()