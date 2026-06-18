from app.db.postgres import (
    postgres_connection
)


class EmbeddingRepository:

    def insert_embedding(
        self,
        embedding_id: str,
        file_path: str,
        source_code: str,
        embedding: list
    ):

        connection = (
            postgres_connection.get_connection()
        )

        cursor = connection.cursor()

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
                embedding
            )
        )

        connection.commit()

        cursor.close()
        
    def search_similar(
        self,
        query_embedding: list,
        limit: int = 5
    ):
        
        connection = (
            postgres_connection.get_connection()
        )

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                file_path,
                source_code
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