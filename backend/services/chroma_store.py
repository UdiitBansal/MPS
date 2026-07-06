import uuid
import chromadb

from backend.config import CHROMA_DIR


class ChromaStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        self.collection = self.client.get_or_create_collection(
            name="multi_pdf_collection"
        )

    def reset_collection(self):

        try:
            self.client.delete_collection(
                "multi_pdf_collection"
            )
        except Exception:
            pass

        self.collection = self.client.get_or_create_collection(
            name="multi_pdf_collection"
        )

    def clear(self):

        try:

            ids = self.collection.get()["ids"]

            if ids:
                self.collection.delete(ids=ids)

        except Exception:
            pass

    def add_documents(self, chunks, embeddings):

        ids = [
            str(uuid.uuid4())
            for _ in chunks
        ]

        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings.tolist()
        )

    def search(self, embedding, top_k=10):

        result = self.collection.query(
            query_embeddings=[embedding.tolist()],
            n_results=top_k
        )

        documents = result.get("documents", [[]])

        if len(documents) == 0:
            return []

        return documents[0]

    def get_all_documents(self):

        result = self.collection.get()

        return result.get("documents", [])