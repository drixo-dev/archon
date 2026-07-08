from pathlib import Path
from threading import Lock, Thread
from datetime import datetime, timezone
import traceback

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
        self._repository_index = {}
        self._lock = Lock()

    def create_repository(self, github_url: str) -> dict:
        repo_name = github_url.rstrip("/").split("/")[-1].replace(".git", "")

        with self._lock:
            existing_repository = self._repository_index.get(repo_name)
            if existing_repository:
                return dict(existing_repository)

        repository_record = {
            "id": repo_name,
            "name": repo_name,
            "github_url": github_url,
            "status": "queued",
            "progress": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "files_scanned": 0,
            "functions_indexed": 0,
            "embeddings_generated": 0,
            "error": None,
        }

        with self._lock:
            self._repositories.append(repository_record)
            self._repository_index[repo_name] = repository_record

        thread = Thread(
            target=self._run_ingestion,
            args=(repo_name, github_url),
            daemon=True,
        )
        self._ingestion_threads[repo_name] = thread
        thread.start()

        return dict(repository_record)

    def list_repositories(self) -> list[dict]:
        with self._lock:
            return [dict(repository) for repository in self._repositories]

    def get_repository(self, repository_id: str) -> dict | None:
        with self._lock:
            repository = self._repository_index.get(repository_id)
        if not repository:
            return None
        return dict(repository)

    def _update_repository(self, repository_id: str, **updates):
        with self._lock:
            repository = self._repository_index.get(repository_id)
            if not repository:
                return
            repository.update(updates)

    def _run_ingestion(self, repository_name: str, github_url: str):
        try:
            self._update_repository(
                repository_name,
                status="cloning",
                progress=5,
                error=None,
            )
            repository_path = clone_repository(github_url)
            self._ingest_repository(repository_name, repository_path)
        except Exception as exc:
            self._update_repository(
                repository_name,
                status="failed",
                error=str(exc),
            )
            traceback.print_exc()
        finally:
            self._ingestion_threads.pop(repository_name, None)

    def _ingest_repository(self, repository_name: str, repository_path: Path):
        neo4j_connection.connect()
        postgres_connection.connect()

        try:
            graph_service.create_repository(
                name=repository_name,
                url=repository_path.as_posix(),
            )

            self._update_repository(
                repository_name,
                status="scanning",
                progress=15,
            )
            python_files = scan_python_files(repository_path)
            self._update_repository(
                repository_name,
                files_scanned=len(python_files),
            )
            module_index = import_resolver.build_module_index(repository_path, python_files)
            function_index = import_resolver.build_function_index(repository_path, python_files)

            self._update_repository(
                repository_name,
                status="graph",
                progress=35,
            )
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
            total_functions = len(functions)
            self._update_repository(
                repository_name,
                status="embedding",
                progress=80,
                functions_indexed=total_functions,
                embeddings_generated=0,
            )

            generated_embeddings = 0
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
                generated_embeddings += 1
                embedding_progress = 80
                if total_functions > 0:
                    embedding_progress = 80 + int((generated_embeddings / total_functions) * 19)
                self._update_repository(
                    repository_name,
                    progress=min(99, embedding_progress),
                    embeddings_generated=generated_embeddings,
                )

            self._update_repository(
                repository_name,
                status="ready",
                progress=100,
                embeddings_generated=generated_embeddings,
                error=None,
            )
        except Exception as exc:
            self._update_repository(
                repository_name,
                status="failed",
                error=str(exc),
            )
            print(f"Repository ingestion failed: {exc}")
            raise


repository_service = RepositoryService()
