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

        print("\n===================================")
        print("Loading Embedding Model...")
        print("===================================\n")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"Using Device : {self.device.upper()}")

        self.model = SentenceTransformer(

            EMBEDDING_MODEL,

            device=self.device

        )

        self.embedding_dimension = (

            self.model.get_embedding_dimension()

        )

        print(f"Embedding Model : {EMBEDDING_MODEL}")

        print(f"Embedding Dimension : {self.embedding_dimension}")

        print("\nEmbedding Model Loaded Successfully.\n")

    # =====================================================
    # Clean Text
    # =====================================================

    @staticmethod
    def clean_text(text):

        if not text:

            return ""

        return " ".join(

            str(text).split()

        )

    # =====================================================
    # Batch Embeddings
    # =====================================================

    def encode(self, texts):

        if isinstance(texts, str):

            texts = [texts]

        texts = [

            self.clean_text(text)

            for text in texts

            if text and self.clean_text(text)

        ]

        if not texts:

            return np.empty(

                (0, self.embedding_dimension),

                dtype=np.float32

            )

        try:

            embeddings = self.model.encode(

                texts,

                batch_size=EMBEDDING_BATCH_SIZE,

                convert_to_numpy=True,

                normalize_embeddings=NORMALIZE_EMBEDDINGS,

                show_progress_bar=False

            )

            return embeddings.astype(np.float32)

        except Exception as e:

            print(f"Embedding Error : {e}")

            return np.empty(

                (0, self.embedding_dimension),

                dtype=np.float32

            )

    # =====================================================
    # Query Embedding
    # =====================================================

    def encode_query(self, query):

        query = self.clean_text(query)

        if not query:

            return np.empty(

                self.embedding_dimension,

                dtype=np.float32

            )

        try:

            embedding = self.model.encode(

                query,

                convert_to_numpy=True,

                normalize_embeddings=NORMALIZE_EMBEDDINGS,

                show_progress_bar=False

            )

            return embedding.astype(np.float32)

        except Exception as e:

            print(f"Query Embedding Error : {e}")

            return np.empty(

                self.embedding_dimension,

                dtype=np.float32

            )

    # =====================================================
    # Cosine Similarity
    # =====================================================

    @staticmethod
    def cosine_similarity(vec1, vec2):

        try:

            return float(

                np.dot(vec1, vec2) /

                (

                    np.linalg.norm(vec1) *

                    np.linalg.norm(vec2)

                )

            )

        except Exception:

            return 0.0

    # =====================================================
    # Embedding Dimension
    # =====================================================

    def dimension(self):

        return self.embedding_dimension

    # =====================================================
    # Model Information
    # =====================================================

    def info(self):

        return {

            "model": EMBEDDING_MODEL,

            "dimension": self.embedding_dimension,

            "device": self.device,

            "normalized": NORMALIZE_EMBEDDINGS

        }