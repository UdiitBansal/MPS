from rank_bm25 import BM25Okapi


class BM25Store:

    def __init__(self):

        self.documents = []

        self.tokenized_docs = []

        self.bm25 = None

    def build_index(self, chunks):

        self.documents = chunks

        self.tokenized_docs = [
            chunk.lower().split()
            for chunk in chunks
            if chunk.strip()
        ]

        if len(self.tokenized_docs) == 0:
            self.bm25 = None
            return

        self.bm25 = BM25Okapi(
            self.tokenized_docs
        )

    def search(self, query, top_k=10):

        if self.bm25 is None:
            return []

        query_tokens = query.lower().split()

        scores = self.bm25.get_scores(
            query_tokens
        )

        ranked = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked[:top_k]

    def get_all_documents(self):

        return self.documents

    def document_count(self):

        return len(self.documents)

    def clear(self):

        self.documents = []

        self.tokenized_docs = []

        self.bm25 = None