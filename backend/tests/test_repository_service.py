from services.repository_service import RepositoryService


def test_create_repository_adds_repo_to_list(monkeypatch):
    service = RepositoryService()

    class StubThread:
        def __init__(self, target, args, daemon):
            self.target = target
            self.args = args
            self.daemon = daemon

        def start(self):
            return None

    monkeypatch.setattr("services.repository_service.Thread", StubThread)

    result = service.create_repository("https://github.com/fastapi/typer")

    assert result["name"] == "typer"
    assert result["status"] == "queued"
    assert result["progress"] == 0
    assert result["files_scanned"] == 0
    assert result["functions_indexed"] == 0
    assert result["embeddings_generated"] == 0
    assert result["error"] is None
    assert result["created_at"]
    assert service.list_repositories()[0]["id"] == "typer"


def test_run_ingestion_marks_failed_when_clone_errors(monkeypatch):
    service = RepositoryService()
    service._repositories.append(
        {
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
        }
    )
    service._repository_index["typer"] = service._repositories[0]

    def _raise_clone_error(_github_url):
        raise RuntimeError("clone failed")

    monkeypatch.setattr("services.repository_service.clone_repository", _raise_clone_error)

    service._run_ingestion("typer", "https://github.com/fastapi/typer")
    repository = service.get_repository("typer")

    assert repository is not None
    assert repository["status"] == "failed"
    assert repository["error"] == "clone failed"
