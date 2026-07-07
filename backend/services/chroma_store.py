import uuid
import chromadb

from backend.config import CHROMA_DIR


class ChromaStore:

    COLLECTION_NAME = "multi_pdf_collection"

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        self.collection = self.client.get_or_create_collection(
            name=self.COLLECTION_NAME
        )

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

    def clear(self):

        try:

            data = self.collection.get()

            ids = data.get("ids", [])

            if ids:

                self.collection.delete(
                    ids=ids
                )

        except Exception:

            pass

    def add_documents(

        self,

        chunks,

        embeddings,

        metadata_list

    ):

        if len(chunks) == 0:

            return

        ids = [

            str(uuid.uuid4())

            for _ in chunks

        ]

        self.collection.add(

            ids=ids,

            documents=chunks,

            embeddings=embeddings.tolist(),

            metadatas=metadata_list

        )

    def search(

        self,

        embedding,

        top_k=10

    ):

        result = self.collection.query(

            query_embeddings=[embedding.tolist()],

            n_results=top_k,

            include=[

                "documents",

                "metadatas",

                "distances"

            ]

        )

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

        for doc, meta, distance in zip(

            documents,

            metadatas,

            distances

        ):

            similarity = max(

                0.0,

                round(

                    1 - float(distance),

                    4

                )

            )

            retrieved.append(

                {

                    "text": doc,

                    "source": meta.get(

                        "source",

                        "Unknown"

                    ),

                    "chunk": meta.get(

                        "chunk",

                        0

                    ),

                    "page": meta.get(

                        "page",

                        "-"

                    ),

                    "score": similarity

                }

            )

        return retrieved

    def get_all_documents(self):

        return self.collection.get()

    def document_count(self):

        return self.collection.count()