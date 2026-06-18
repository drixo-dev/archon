from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):

        self.model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    def generate_embedding(
        self,
        text: str
    ):
        """
        Convert text into embedding vector.
        """

        embedding = self.model.encode(text)

        return embedding.tolist()


embedding_service = EmbeddingService()