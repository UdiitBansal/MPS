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

        q = query.lower()

        if any(keyword in q for keyword in [
            "summary",
            "summarize",
            "summarise",
            "all pdf",
            "all documents",
            "overall summary",
            "compare",
            "comparison",
            "difference",
            "differences",
            "common",
            "similar",
            "research report"
        ]):

            top_k = 30

        query_embedding = self.embedder.encode(
            [query]
        )[0]

        chroma_results = self.chroma.search(
            query_embedding,
            top_k
        )

        bm25_results = self.bm25.search(
            query,
            top_k
        )

        scores = defaultdict(float)

        for rank, doc in enumerate(chroma_results):

            scores[doc] += 1 / (rank + 60)

        for rank, (doc, score) in enumerate(bm25_results):

            scores[doc] += (1 / (rank + 60)) + (score * 0.01)

        ranked = sorted(
            scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        results = []
        seen = set()

        for doc, score in ranked:

            doc = doc.strip()

            if not doc:
                continue

            if doc in seen:
                continue

            seen.add(doc)

            results.append(doc)

            if len(results) >= top_k:
                break

        return results