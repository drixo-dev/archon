from app.db.postgres import (
    postgres_connection
)


class EmbeddingRepository:

    def initialize_schema(self):
        connection = postgres_connection.get_connection()
        if not connection:
            return

        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS function_embeddings (
                id TEXT PRIMARY KEY,
                file_path TEXT,
                source_code TEXT,
                embedding VECTOR(384),
                repository_id TEXT
            )
            """
        )
        cursor.execute(
            "ALTER TABLE IF EXISTS function_embeddings ADD COLUMN IF NOT EXISTS repository_id TEXT"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_function_embeddings_repository_id ON function_embeddings (repository_id)"
        )
        connection.commit()
        cursor.close()

    def insert_embedding(
        self,
        embedding_id: str,
        file_path: str,
        source_code: str,
        embedding: list,
        repository_id: str | None = None
    ):


        connection = (
            postgres_connection.get_connection()
        )

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s AND column_name = %s
            """,
            ("function_embeddings", "repository_id"),
        )
        has_repository_id = cursor.fetchone() is not None

        if has_repository_id:
            cursor.execute(
                """
                INSERT INTO function_embeddings (
                    id,
                    file_path,
                    source_code,
                    embedding,
                    repository_id
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id)
                DO UPDATE SET
                    file_path = EXCLUDED.file_path,
                    source_code = EXCLUDED.source_code,
                    embedding = EXCLUDED.embedding,
                    repository_id = EXCLUDED.repository_id
                """,
                (
                    embedding_id,
                    file_path,
                    source_code,
                    embedding,
                    repository_id,
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO function_embeddings (
                    id,
                    file_path,
                    source_code,
                    embedding
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id)
                DO NOTHING
                """,
                (
                    embedding_id,
                    file_path,
                    source_code,
                    embedding,
                ),
            )

        connection.commit()

        cursor.close()
        
    def search_similar(
        self,
        query_embedding: list,
        limit: int = 5,
        repository_id: str | None = None
    ):
        
        connection = (
            postgres_connection.get_connection()
        )


        cursor = connection.cursor()

        if repository_id:
            cursor.execute(
                """
                SELECT
                    id,
                    file_path,
                    source_code,
                    repository_id
                FROM function_embeddings
                WHERE repository_id = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    repository_id,
                    query_embedding,
                    limit
                )
            )
        else:
            cursor.execute(
                """
                SELECT
                    id,
                    file_path,
                    source_code,
                    repository_id
                FROM function_embeddings
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (
                    query_embedding,
                    limit
                )
            )

        results = cursor.fetchall()

        cursor.close()

        return results


embedding_repository = (
    EmbeddingRepository()
)