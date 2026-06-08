from app.db.neo4j import neo4j_connection
from services.graph_service import graph_service


def test_file_graph():
    neo4j_connection.connect()

    files = [
        "app/main.py",
        "app/config.py",
        "app/db/neo4j.py",
        "services/graph_service.py"
    ]

    for file_path in files:
        graph_service.create_file(
            repository_name="fastapi",
            file_path=file_path
        )

    neo4j_connection.close()


if __name__ == "__main__":
    test_file_graph()
