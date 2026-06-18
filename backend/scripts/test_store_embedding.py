from app.db.postgres import (
    postgres_connection
)

from repositories.embedding_repository import (
    embedding_repository
)

from services.embedding_service import (
    embedding_service
)


def test_store_embedding():

    postgres_connection.connect()

    source_code = """
    def validate_user(username, password):
        user = get_user(username)
        return verify_password(
            password,
            user.password_hash
        )
    """

    embedding = (
        embedding_service.generate_embedding(
            source_code
        )
    )

    embedding_repository.insert_embedding(
        embedding_id="demo_function",
        file_path="auth/service.py",
        source_code=source_code,
        embedding=embedding
    )

    postgres_connection.close()

    print("Embedding stored.")


if __name__ == "__main__":
    test_store_embedding()