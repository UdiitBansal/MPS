import numpy as np
import torch

from sentence_transformers import SentenceTransformer

from backend.config import (
    EMBEDDING_MODEL,
    EMBEDDING_BATCH_SIZE,
    NORMALIZE_EMBEDDINGS
)


class EmbeddingModel:

    def __init__(self):

        print("\nLoading Embedding Model...")

        device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"Using Device : {device.upper()}")

        self.model = SentenceTransformer(

            EMBEDDING_MODEL,

            device=device

        )

        # New API (replaces deprecated method)
        self.embedding_dimension = (

            self.model.get_embedding_dimension()

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

        try:

            embeddings = self.model.encode(

                texts,

                batch_size=EMBEDDING_BATCH_SIZE,

                convert_to_numpy=True,

                normalize_embeddings=NORMALIZE_EMBEDDINGS,

                show_progress_bar=False

            )

            return embeddings

        except Exception as e:

            print(f"Embedding Error : {e}")

            return np.array([])

    def encode_query(self, query):

        if not query:

            return np.array([])

        try:

            embedding = self.model.encode(

                query,

                convert_to_numpy=True,

                normalize_embeddings=NORMALIZE_EMBEDDINGS,

                show_progress_bar=False

            )

            return embedding

        except Exception as e:

            print(f"Query Embedding Error : {e}")

            return np.array([])

    def dimension(self):

        return self.embedding_dimension