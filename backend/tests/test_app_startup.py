from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app


def test_app_lifespan_connects_databases():
    with patch("app.main.postgres_connection") as postgres_connection, patch(
        "app.main.neo4j_connection"
    ) as neo4j_connection:
        postgres_connection.connect = MagicMock()
        postgres_connection.close = MagicMock()
        neo4j_connection.connect = MagicMock()
        neo4j_connection.close = MagicMock()

        with TestClient(app) as client:
            assert client.get("/").status_code == 200

        postgres_connection.connect.assert_called_once()
        neo4j_connection.connect.assert_called_once()
        postgres_connection.close.assert_called_once()
        neo4j_connection.close.assert_called_once()
