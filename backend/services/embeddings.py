import numpy as np
from sentence_transformers import SentenceTransformer

from backend.config import (
    EMBEDDING_MODEL,
    EMBEDDING_BATCH_SIZE,
    NORMALIZE_EMBEDDINGS
)


class EmbeddingModel:

    def __init__(self):

        print("\nLoading Embedding Model...")

        self.model = SentenceTransformer(
            EMBEDDING_MODEL,
            device="cpu"
        )

        self.embedding_dimension = (
            self.model.get_sentence_embedding_dimension()
        )

        print("Embedding Model Loaded Successfully.\n")

    def encode(self, texts):

        if isinstance(texts, str):
            texts = [texts]

        texts = [

            text.strip()

            for text in texts

            if text and text.strip()

        ]

        if not texts:
            return np.array([])

        embeddings = self.model.encode(

            texts,

            batch_size=EMBEDDING_BATCH_SIZE,

            convert_to_numpy=True,

            normalize_embeddings=NORMALIZE_EMBEDDINGS,

            show_progress_bar=False

        )

        return embeddings

    def encode_query(self, query):

        embedding = self.model.encode(

            query,

            convert_to_numpy=True,

            normalize_embeddings=NORMALIZE_EMBEDDINGS,

            show_progress_bar=False

        )

        return embedding

    def dimension(self):

        return self.embedding_dimension