from app.db.neo4j import neo4j_connection
from ingestion.github_loader import clone_repository
from ingestion.scanner import scan_python_files
from services.graph_builder import graph_builder


REPO_URL = "https://github.com/fastapi/typer.git"


def test_ingestion_pipeline():
    neo4j_connection.connect()

    repo_path = clone_repository(REPO_URL)

    repository_name = repo_path.name

    python_files = scan_python_files(repo_path)

    for file_path in python_files[:5]:
        print(f"Ingesting: {file_path}")

        graph_builder.ingest_file(
            repository_name=repository_name,
            repository_path=repo_path,
            file_path=file_path
        )

    neo4j_connection.close()


if __name__ == "__main__":
    test_ingestion_pipeline()