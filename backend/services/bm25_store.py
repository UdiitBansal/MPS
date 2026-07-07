from rank_bm25 import BM25Okapi


class BM25Store:

    def __init__(self):

        self.documents = []

        self.metadata = []

        self.tokenized_docs = []

        self.bm25 = None

    def build_index(self, chunks, metadata_list=None):

        self.clear()

        if not chunks:
            return

        self.documents = chunks

        if metadata_list is None:

            metadata_list = [

                {

                    "source": "Unknown",

                    "chunk": i + 1,

                    "page": "-"

                }

                for i in range(len(chunks))

            ]

        self.metadata = metadata_list

        self.tokenized_docs = [

            doc.lower().split()

            for doc in self.documents

        ]

        self.bm25 = BM25Okapi(
            self.tokenized_docs
        )

    def search(self, query, top_k=10):

        if self.bm25 is None:

            return []

        query = query.strip().lower()

        if not query:

            return []

        query_tokens = query.split()

        scores = self.bm25.get_scores(
            query_tokens
        )

        ranked = sorted(

            zip(

                self.documents,

                self.metadata,

                scores

            ),

            key=lambda x: x[2],

            reverse=True

        )

        results = []

        for doc, meta, score in ranked[:top_k]:

            results.append(

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

                    "score": round(

                        float(score),

                        4

                    )

                }

            )

        return results

    def get_all_documents(self):

        return self.documents

    def document_count(self):

        return len(self.documents)

    def clear(self):

        self.documents = []

        self.metadata = []

        self.tokenized_docs = []

        self.bm25 = None