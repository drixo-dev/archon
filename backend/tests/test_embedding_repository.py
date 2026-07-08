from unittest.mock import MagicMock, patch

from repositories.embedding_repository import EmbeddingRepository


def test_insert_embedding_updates_existing_row_with_repository_id():
    repository = EmbeddingRepository()
    repository._ensure_schema = MagicMock()

    cursor = MagicMock()
    cursor.fetchone.return_value = ("repository_id",)
    connection = MagicMock()
    connection.cursor.return_value = cursor

    with patch(
        "repositories.embedding_repository.postgres_connection.get_connection",
        return_value=connection,
    ):
        repository.insert_embedding(
            embedding_id="demo.fn",
            file_path="demo.py",
            source_code="def demo():\n    return 1",
            embedding=[0.1, 0.2, 0.3],
            repository_id="typer",
        )

    insert_query = cursor.execute.call_args_list[1].args[0]
    assert "DO UPDATE SET" in insert_query
    assert cursor.execute.call_args_list[1].args[1][4] == "typer"
