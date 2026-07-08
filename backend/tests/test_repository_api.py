from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app


def test_list_repositories_endpoint():
    with patch(
        "api.repositories.repository_service.list_repositories",
        return_value=[
            {
                "id": "typer",
                "name": "typer",
                "github_url": "https://github.com/fastapi/typer",
                "status": "ready",
                "progress": 100,
                "created_at": "2026-01-01T00:00:00+00:00",
                "files_scanned": 84,
                "functions_indexed": 593,
                "embeddings_generated": 593,
                "error": None,
            }
        ],
    ):
        with TestClient(app) as client:
            response = client.get("/repositories")

        assert response.status_code == 200
        assert response.json()["repositories"][0]["name"] == "typer"


def test_create_repository_endpoint():
    with patch(
        "api.repositories.repository_service.create_repository",
        return_value={
            "id": "typer",
            "name": "typer",
            "github_url": "https://github.com/fastapi/typer",
            "status": "queued",
            "progress": 0,
            "created_at": "2026-01-01T00:00:00+00:00",
            "files_scanned": 0,
            "functions_indexed": 0,
            "embeddings_generated": 0,
            "error": None,
        },
    ) as create_repository:
        with TestClient(app) as client:
            response = client.post(
                "/repositories",
                json={"github_url": "https://github.com/fastapi/typer"},
            )

        assert response.status_code == 200
        create_repository.assert_called_once_with(
            "https://github.com/fastapi/typer"
        )


def test_get_repository_endpoint():
    with patch(
        "api.repositories.repository_service.get_repository",
        return_value={
            "id": "typer",
            "name": "typer",
            "github_url": "https://github.com/fastapi/typer",
            "status": "embedding",
            "progress": 80,
            "created_at": "2026-01-01T00:00:00+00:00",
            "files_scanned": 84,
            "functions_indexed": 593,
            "embeddings_generated": 311,
            "error": None,
        },
    ):
        with TestClient(app) as client:
            response = client.get("/repositories/typer")

        assert response.status_code == 200
        assert response.json()["repository"]["id"] == "typer"
        assert response.json()["repository"]["progress"] == 80


def test_get_repository_not_found_endpoint():
    with patch(
        "api.repositories.repository_service.get_repository",
        return_value=None,
    ):
        with TestClient(app) as client:
            response = client.get("/repositories/missing")

        assert response.status_code == 404
        assert response.json()["detail"] == "Repository not found"
