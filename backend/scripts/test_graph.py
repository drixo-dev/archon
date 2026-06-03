from app.db.neo4j import neo4j_connection
from services.graph_service import graph_service

def test_graph():
    neo4j_connection.connect()

    result = graph_service.create_repository(
        name="fastapi",
        url="https://github.com/fastapi/fastapi"
    )

    print(result)

    neo4j_connection.close()


if __name__ == "__main__":
    test_graph()