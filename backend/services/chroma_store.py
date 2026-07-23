import uuid
import chromadb
import logging

from backend.config import CHROMA_DIR
logger = logging.getLogger(__name__)

class ChromaStore:

    COLLECTION_NAME = "multi_pdf_collection"

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME
        )

    # =====================================================
    # Reset Collection
    # =====================================================

    def reset_collection(self):

        try:

            self.client.delete_collection(
                self.COLLECTION_NAME
            )

        except Exception:

            pass

        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME
        )

    # =====================================================
    # Clear Collection
    # =====================================================

    def clear(self):

        try:

            data = self.collection.get()

            ids = data.get("ids", [])

            if ids:

                self.collection.delete(ids=ids)

        except Exception:

            pass

    # =====================================================
    # Add Documents
    # =====================================================

    def add_documents(
        self,
        chunks,
        embeddings,
        metadata_list
    ):

        if not chunks:

            return
        if not (len(chunks) == len(embeddings) == len(metadata_list)):
            raise ValueError(
                "Chunks, embeddings and metadata counts do not match."
            )

        ids = [

            str(uuid.uuid4())

            for _ in chunks

        ]

        try:
            self.collection.add(
                ids=ids,
                documents=chunks,
                embeddings=embeddings.tolist(),
                metadatas=metadata_list
            )
            

        except Exception as e:
            logger.exception("Failed to add documents to ChromaDB")
            raise RuntimeError(f"ChromaDB insert failed: {e}")
    # =====================================================
    # Search
    # =====================================================

    def search(
        self,
        embedding,
        top_k=10
    ):
        
        try:
            result = self.collection.query(
                query_embeddings=[embedding.tolist()],
                n_results=top_k,
                include=[
                    "documents",
                    "metadatas",
                    "distances"
                ]
            )
        except Exception as e:
            logger.exception("Chroma search failed")
            return []
        documents = result.get(

            "documents",

            [[]]

        )[0]

        metadatas = result.get(

            "metadatas",

            [[]]

        )[0]

        distances = result.get(

            "distances",

            [[]]

        )[0]

        retrieved = []

        seen = set()

        for doc, meta, distance in zip(

            documents,

            metadatas,

            distances

        ):

            if not doc:

                continue

            normalized = " ".join(

                doc.split()

            )

            if normalized in seen:
                 continue
            seen.add(normalized)
            meta = meta or {}
            similarity = max(

                0.0,

                min(

                    1.0,

                    1 - float(distance)

                )

            )

            retrieved.append(

                {

                    "text": doc,

                    "source": meta.get(

                        "source",

                        "Unknown"

                    ),

                    "page": meta.get(

                        "page",

                        meta.get(

                            "page_number",

                            "-"

                        )

                    ),

                    "chunk": meta.get(

                        "chunk",

                        "-"

                    ),

                    "score": round(

                        similarity,

                        4

                    ),

                    "distance": round(

                        float(distance),

                        4

                    )

                }

            )

        retrieved.sort(

            key=lambda x: x["score"],

            reverse=True

        )

        return retrieved[:top_k]

    # =====================================================
    # Get All
    # =====================================================

    def get_all_documents(self):

        return self.collection.get()

    # =====================================================
    # Count
    # =====================================================

    def document_count(self):

        return self.collection.count()

    # =====================================================
    # Collection Info
    # =====================================================

    def stats(self):

        return {

            "collection": self.COLLECTION_NAME,

            "documents": self.document_count()

        }