from collections import defaultdict


class HybridRetriever:

    def __init__(self, chroma, bm25, embedder):

        self.chroma = chroma

        self.bm25 = bm25

        self.embedder = embedder

    def retrieve(self, query, top_k=10):

        query = query.strip()

        if not query:

            return []

        # ---------------- Query Embedding ----------------

        query_embedding = self.embedder.encode_query(
            query
        )

        # ---------------- Semantic Search ----------------

        semantic_results = self.chroma.search(
            query_embedding,
            top_k * 2
        )

        # ---------------- Keyword Search ----------------

        keyword_results = self.bm25.search(
            query,
            top_k * 2
        )

        scores = defaultdict(float)

        documents = {}

        # ==================================================
        # Chroma Score (Higher Weight)
        # ==================================================

        for rank, item in enumerate(semantic_results):

            text = item["text"]

            documents[text] = item

            semantic_score = 1 / (rank + 1)

            scores[text] += semantic_score * 0.75

        # ==================================================
        # BM25 Score
        # ==================================================

        for rank, item in enumerate(keyword_results):

            text = item["text"]

            documents[text] = item

            keyword_rank = 1 / (rank + 1)

            scores[text] += keyword_rank * 0.25

            scores[text] += item["score"] * 0.015

        # ==================================================
        # Final Ranking
        # ==================================================

        ranked = sorted(

            scores.items(),

            key=lambda x: x[1],

            reverse=True

        )

        final_results = []

        seen = set()

        for text, score in ranked:

            normalized = " ".join(text.split())

            if normalized in seen:

                continue

            seen.add(normalized)

            doc = documents[text]

            doc["score"] = round(score, 4)

            final_results.append(doc)

            if len(final_results) >= top_k:

                break

        return final_results