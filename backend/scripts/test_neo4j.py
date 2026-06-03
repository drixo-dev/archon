from app.db.neo4j import neo4j_connection

def test_connection():
    neo4j_connection.connect()

    with neo4j_connection.get_session() as session:
        result = session.run(
            "RETURN 'Neo4j Connected' AS message"
        )

        for record in result:
            print(record["message"])

    neo4j_connection.close()


if __name__ == "__main__":
    test_connection()