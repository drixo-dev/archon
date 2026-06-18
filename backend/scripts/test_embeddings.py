from services.embedding_service import (
    embedding_service
)


def test_embeddings():

    sample_text = """
    def validate_user(username, password):

        user = get_user(username)

        return verify_password(
            password,
            user.password_hash
        )
    """

    embedding = (
        embedding_service.generate_embedding(
            sample_text
        )
    )

    print("\nEmbedding Length:")
    print(len(embedding))

    print("\nFirst 10 Values:")
    print(embedding[:10])


if __name__ == "__main__":
    test_embeddings()