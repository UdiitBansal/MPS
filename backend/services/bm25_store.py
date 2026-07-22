import re

from rank_bm25 import BM25Okapi


class BM25Store:

    def __init__(self):

        self.documents = []

        self.metadata = []

        self.tokenized_docs = []

        self.bm25 = None

    # =====================================================
    # Tokenizer
    # =====================================================

    @staticmethod
    def tokenize(text):

        if not text:

            return []

        text = text.lower()

        return re.findall(

            r"\b[a-zA-Z0-9]+\b",

            text

        )

    # =====================================================
    # Build BM25 Index
    # =====================================================

    def build_index(

        self,

        chunks,

        metadata_list=None

    ):

        self.clear()

        if not chunks:

            return

        cleaned_docs = []

        cleaned_metadata = []

        for i, chunk in enumerate(chunks):

            chunk = chunk.strip()

            if not chunk:

                continue

            cleaned_docs.append(chunk)

            if metadata_list:

                cleaned_metadata.append(

                    metadata_list[i]

                )

            else:

                cleaned_metadata.append({

                    "source": "Unknown",

                    "page": "-",

                    "chunk": i + 1

                })

        self.documents = cleaned_docs

        self.metadata = cleaned_metadata

        self.tokenized_docs = [

            self.tokenize(doc)

            for doc in self.documents

        ]

        if self.tokenized_docs:

            self.bm25 = BM25Okapi(

                self.tokenized_docs

            )

    # =====================================================
    # Search
    # =====================================================

    def search(

        self,

        query,

        top_k=10

    ):

        if self.bm25 is None:

            return []

        query = query.lower().strip()

        if not query:

            return []

        query_tokens = self.tokenize(

            query

        )

        if not query_tokens:

            return []

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

        if not ranked:

            return []

        max_score = max(

            scores

        ) if len(scores) else 1

        if max_score <= 0:

            max_score = 1

        results = []

        seen = set()

        for doc, meta, score in ranked:

            if score <= 0:

                continue

            key = (

                meta.get("source"),

                meta.get("page"),

                meta.get("chunk")

            )

            if key in seen:

                continue

            seen.add(key)

            confidence = round(

                float(score) / max_score,

                4

            )

            results.append({

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

                "score": confidence

            })

            if len(results) >= top_k:

                break

        return results

    # =====================================================
    # Utilities
    # =====================================================

    def get_all_documents(self):

        return self.documents

    def document_count(self):

        return len(self.documents)

    def clear(self):

        self.documents = []

        self.metadata = []

        self.tokenized_docs = []

        self.bm25 = None