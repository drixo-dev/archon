from app.db.neo4j import neo4j_connection
from services.graph_service import graph_service

def test_function_graph():
    neo4j_connection.connect()

    functions = [
        ("app/main.py", "startup"),
        ("app/main.py", "shutdown"),
        ("app/config.py", "load_settings"),
        ("app/db/neo4j.py", "connect"),
        ("app/db/neo4j.py", "get_session")
    ]

    for file_path, function_name in functions:
        graph_service.create_function(
            file_path=file_path,
            function_name=function_name
        )

    neo4j_connection.close()


if __name__ == "__main__":
    test_function_graph()
