from collections import defaultdict


class HybridRetriever:

    def __init__(self, chroma, bm25, embedder):

        self.chroma = chroma
        self.bm25 = bm25
        self.embedder = embedder

    # =====================================================
    # Hybrid Retrieval
    # =====================================================
    def retrieve(self, query, top_k=10):
        query = " ".join(query.strip().split())
        q = query.lower()
        if any(word in q for word in [
            "highest",
            "lowest",
            "top",
            "maximum",
            "minimum",
            "marks",
            "score",
            "percentage",
            "rank"
        ]):
             query = query + " student total marks score percentage result highest lowest"
             if not query:
                 return []

        try:

            query_embedding = self.embedder.encode_query(query)

        except Exception as e:

            print(f"Embedding Error : {e}")

            return []

        search_k = max(top_k * 5, 50)

        # -------------------------------------------------
        # Chroma Semantic Search
        # -------------------------------------------------

        try:

            semantic_results = self.chroma.search(

                query_embedding,

                search_k

            )

        except Exception as e:

            print(f"Chroma Error : {e}")

            semantic_results = []

        # -------------------------------------------------
        # BM25 Search
        # -------------------------------------------------

        try:

            keyword_results = self.bm25.search(

                query,

                search_k

            )

        except Exception as e:

            print(f"BM25 Error : {e}")

            keyword_results = []

        scores = defaultdict(float)

        documents = {}

        # =================================================
        # Semantic Score (Higher Weight)
        # =================================================

        for rank, item in enumerate(semantic_results):

            text = item.get("text", "").strip()

            if not text:

                continue

            documents[text] = item

            semantic_score = 1 / (rank + 1)

            scores[text] += semantic_score * 0.75

        # =================================================
        # BM25 Score
        # =================================================

        for rank, item in enumerate(keyword_results):

            if item.get("score", 0) <= 0:

                continue

            text = item.get("text", "").strip()

            if not text:

                continue

            documents[text] = item

            keyword_rank = 1 / (rank + 1)

            scores[text] += keyword_rank * 0.25

            scores[text] += item.get("score", 0) * 0.015

        # =================================================
        # Final Ranking
        # =================================================

        ranked = sorted(

            scores.items(),

            key=lambda x: x[1],

            reverse=True

        )

        final_results = []

        seen = set()

        max_score = max(ranked[0][1], 1e-6) if ranked else 1.0

        for text, score in ranked:

            normalized = " ".join(text.split())

            if normalized in seen:

                continue

            seen.add(normalized)

            doc = documents[text].copy()

            # ----------------------------------------------
            # Confidence (0 - 1)
            # ----------------------------------------------

            confidence = round(min(score / max_score, 1.0), 4)

            doc["score"] = round(confidence, 4)

            final_results.append(doc)

            if len(final_results) >= top_k:

                break

        return final_results