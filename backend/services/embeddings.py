import logging
import numpy as np
import torch

from sentence_transformers import SentenceTransformer

from backend.config import (
    EMBEDDING_MODEL,
    EMBEDDING_BATCH_SIZE,
    NORMALIZE_EMBEDDINGS
)

logger = logging.getLogger(__name__)


class EmbeddingModel:

    def __init__(self):

        logger.info("===================================")
        logger.info("Loading Embedding Model...")
        logger.info("===================================")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info(f"Using Device : {self.device.upper()}")

        try:

            self.model = SentenceTransformer(
                EMBEDDING_MODEL,
                device=self.device
            )

        except Exception as e:

            logger.exception("Failed to load embedding model")

            raise RuntimeError(
                f"Unable to load embedding model '{EMBEDDING_MODEL}': {e}"
            )

        self.embedding_dimension = (
            self.model.get_embedding_dimension()
        )

        logger.info(f"Embedding Model : {EMBEDDING_MODEL}")
        logger.info(f"Embedding Dimension : {self.embedding_dimension}")
        logger.info("Embedding Model Loaded Successfully.")

    # =====================================================
    # Clean Text
    # =====================================================

    @staticmethod
    def clean_text(text):

        if not text:
            return ""

        return " ".join(str(text).split())

    # =====================================================
    # Batch Embeddings
    # =====================================================

    def encode(self, texts):

        if isinstance(texts, str):
            texts = [texts]

        cleaned_texts = []

        for text in texts:

            cleaned = self.clean_text(text)

            if cleaned:
                cleaned_texts.append(cleaned)

        texts = cleaned_texts

        if not texts:

            return np.empty(
                (0, self.embedding_dimension),
                dtype=np.float32
            )

        try:

            embeddings = self.model.encode_document(

                texts,

                batch_size=EMBEDDING_BATCH_SIZE,

                convert_to_numpy=True,

                normalize_embeddings=NORMALIZE_EMBEDDINGS,

                show_progress_bar=False

            )

            return embeddings.astype(np.float32)

        except Exception:

            logger.exception("Embedding generation failed")

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

            embedding = self.model.encode_query(

                query,

                convert_to_numpy=True,

                normalize_embeddings=NORMALIZE_EMBEDDINGS,

                show_progress_bar=False

            )

            return embedding.astype(np.float32)

        except Exception:

            logger.exception("Query embedding generation failed")

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

            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return float(
                np.dot(vec1, vec2) / (norm1 * norm2)
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