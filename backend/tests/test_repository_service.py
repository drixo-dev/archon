from services.repository_service import RepositoryService


def test_create_repository_adds_repo_to_list(monkeypatch):
    service = RepositoryService()

    monkeypatch.setattr(
        "services.repository_service.clone_repository",
        lambda github_url: "/tmp/repo",
    )

    monkeypatch.setattr(service, "_ingest_repository", lambda repository_name, repository_path: None)

    result = service.create_repository("https://github.com/fastapi/typer")

    assert result["name"] == "typer"
    assert result["status"] == "ready"
    assert service.list_repositories()[0]["id"] == "typer"
