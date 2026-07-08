from backend.indexes.document_index import index
from backend.services.hybrid_retriever import HybridRetriever

from backend.config import (
    DEFAULT_TOP_K,
    SUMMARY_TOP_K,
    COMPARE_TOP_K
)


class Retriever:

    def __init__(self):

        self.hybrid = HybridRetriever(

            chroma=index.chroma,

            bm25=index.bm25,

            embedder=index.embedder

        )

        self.summary_keywords = {

            "summary",
            "summarize",
            "summarise",
            "executive summary",
            "overall summary",
            "complete summary",
            "summary of all",
            "research report",
            "report",
            "all pdf",
            "all pdfs",
            "all documents"

        }

        self.compare_keywords = {

            "compare",
            "comparison",
            "difference",
            "differences",
            "similarity",
            "similarities",
            "contrast",
            "common",
            "common topics",
            "same",
            "unique"

        }

        self.detail_keywords = {

            "architecture",
            "design",
            "workflow",
            "implementation",
            "methodology",
            "algorithm",
            "framework",
            "pipeline",
            "system",
            "component",
            "technology",
            "modules",
            "model",
            "retrieval",
            "embedding"

        }

    # =====================================================
    # Decide how many chunks to retrieve
    # =====================================================

    def detect_top_k(self, question):

        q = " ".join(question.lower().split())

        is_summary = any(
            keyword in q
            for keyword in self.summary_keywords
        )

        is_compare = any(
            keyword in q
            for keyword in self.compare_keywords
        )

        is_detail = any(
            keyword in q
            for keyword in self.detail_keywords
        )

        if is_summary and is_compare:

            return max(
                SUMMARY_TOP_K,
                COMPARE_TOP_K
            )

        if is_summary:

            return SUMMARY_TOP_K

        if is_compare:

            return COMPARE_TOP_K

        if is_detail:

            return max(
                DEFAULT_TOP_K,
                15
            )

        return DEFAULT_TOP_K

    # =====================================================
    # Search
    # =====================================================

    def search(self, question):

        question = " ".join(

            question.strip().lower().split()

        )

        if len(question) < 2:

            return []

        top_k = self.detect_top_k(question)

        try:

            results = self.hybrid.retrieve(

                question,

                top_k=top_k

            )

        except Exception as e:

            print(f"Retriever Error : {e}")

            return []

        # =================================================
        # Remove Duplicate Chunks
        # =================================================

        unique_results = []

        seen = set()

        for item in results:

            key = (

                item.get("source", ""),

                item.get("page", "-"),

                item.get("chunk", "-")

            )

            if key in seen:

                continue

            seen.add(key)

            unique_results.append(item)

        # =================================================
        # Sort by Score
        # =================================================

        unique_results.sort(

            key=lambda x: x.get("score", 0),

            reverse=True

        )

        return unique_results