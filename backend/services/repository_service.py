from pathlib import Path
from threading import Thread

from app.db.neo4j import neo4j_connection
from app.db.postgres import postgres_connection
from ingestion.github_loader import clone_repository
from services.embedding_service import embedding_service
from services.graph_builder import graph_builder
from services.graph_service import graph_service
from services.import_resolver import import_resolver
from repositories.embedding_repository import embedding_repository
from ingestion.scanner import scan_python_files


class RepositoryService:
    def __init__(self):
        self._repositories = []
        self._ingestion_threads = {}

    def create_repository(self, github_url: str) -> dict:
        repo_name = github_url.rstrip("/").split("/")[-1].replace(".git", "")
        repo_path = clone_repository(github_url)

        repository_record = {
            "id": repo_name,
            "name": repo_name,
            "github_url": github_url,
            "status": "ready",
        }

        if repository_record not in self._repositories:
            self._repositories.append(repository_record)

        thread = Thread(
            target=self._run_ingestion,
            args=(repo_name, repo_path),
            daemon=True,
        )
        self._ingestion_threads[repo_name] = thread
        thread.start()

        return repository_record

    def list_repositories(self) -> list[dict]:
        return list(self._repositories)

    def _run_ingestion(self, repository_name: str, repository_path: Path):
        try:
            self._ingest_repository(repository_name, repository_path)
        except Exception:
            pass

    def _ingest_repository(self, repository_name: str, repository_path: Path):
        neo4j_connection.connect()
        postgres_connection.connect()

        try:
            graph_service.create_repository(
                name=repository_name,
                url=repository_path.as_posix(),
            )

            python_files = scan_python_files(repository_path)
            module_index = import_resolver.build_module_index(repository_path, python_files)
            function_index = import_resolver.build_function_index(repository_path, python_files)

            for file_path in python_files:
                graph_builder.ingest_file(
                    repository_name=repository_name,
                    repository_path=repository_path,
                    file_path=file_path,
                    module_index=module_index,
                    function_index=function_index,
                )

            functions = graph_service.get_all_functions(
                exclude_tests=True,
                repository_name=repository_name,
            )
            for function in functions:
                if function["file_path"].startswith("tests/"):
                    continue

                embedding = embedding_service.generate_embedding(function["source_code"])
                embedding_repository.insert_embedding(
                    embedding_id=function["qualified_name"],
                    file_path=function["file_path"],
                    source_code=function["source_code"],
                    embedding=embedding,
                    repository_id=repository_name,
                )
        except Exception as exc:
            print(f"Repository ingestion failed: {exc}")
            raise


repository_service = RepositoryService()
