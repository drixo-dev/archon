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
            "status": "ready",
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
