from backend.indexes.document_index import index
from backend.services.hybrid_retriever import HybridRetriever

from backend.config import (
    DEFAULT_TOP_K,
    SUMMARY_TOP_K,
    COMPARE_TOP_K,
    DETAIL_TOP_K
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
            "unique",
            "versus",
            "vs"

        }

        self.claim_keywords = {

            "claim",
            "claims",
            "key claim",
            "key claims",
            "main claim",
            "important claim"

        }

        self.theme_keywords = {

            "theme",
            "themes",
            "topic",
            "topics",
            "cluster",
            "clustering"

        }

        self.contradiction_keywords = {

            "contradiction",
            "contradict",
            "conflict",
            "conflicts",
            "opposite",
            "disagree"

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
    # Decide Retrieval Size
    # =====================================================

    def detect_top_k(self, question):

        q = " ".join(question.lower().split())

        if any(k in q for k in self.summary_keywords):

            return SUMMARY_TOP_K

        if any(k in q for k in self.compare_keywords):

            return COMPARE_TOP_K

        if any(k in q for k in self.claim_keywords):

            return max(COMPARE_TOP_K, 25)

        if any(k in q for k in self.theme_keywords):

            return max(COMPARE_TOP_K, 25)

        if any(k in q for k in self.contradiction_keywords):

            return max(COMPARE_TOP_K, 25)

        if any(k in q for k in self.detail_keywords):

            return DETAIL_TOP_K

        return DEFAULT_TOP_K

    # =====================================================
    # Search
    # =====================================================

    def search(self, question):

        question = " ".join(question.strip().split())

        if not question:

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

        unique_results = []

        seen = set()

        used_documents = set()

        for item in results:

            source = item.get("source", "Unknown")

            page = item.get("page", "-")

            chunk = item.get("chunk", "-")

            key = (source, page, chunk)

            if key in seen:

                continue

            seen.add(key)

            unique_results.append(item)

            used_documents.add(source)

        unique_results.sort(

            key=lambda x: x.get("score", 0),

            reverse=True

        )

        print(

            f"Retriever -> {len(unique_results)} chunks from {len(used_documents)} documents"

        )

        return unique_results