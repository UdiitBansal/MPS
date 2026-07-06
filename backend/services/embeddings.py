from sentence_transformers import SentenceTransformer
import numpy as np

from backend.config import EMBEDDING_MODEL


class EmbeddingModel:

    def __init__(self):

        print("\nLoading Embedding Model...")

        self.model = SentenceTransformer(
            EMBEDDING_MODEL
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

        if len(texts) == 0:

            return np.array([])

        embeddings = self.model.encode(

            texts,

            batch_size=32,

            convert_to_numpy=True,

            normalize_embeddings=True,

            show_progress_bar=False

        )

        return embeddings

    def encode_query(self, query):

        embedding = self.model.encode(

            [query],

            convert_to_numpy=True,

            normalize_embeddings=True,

            show_progress_bar=False

        )

        return embedding[0]

    def dimension(self):

        return self.model.get_sentence_embedding_dimension()