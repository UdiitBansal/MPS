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

    def detect_top_k(self, question):

        q = question.lower()

        if any(keyword in q for keyword in self.summary_keywords):

            return SUMMARY_TOP_K

        if any(keyword in q for keyword in self.compare_keywords):

            return COMPARE_TOP_K

        if any(keyword in q for keyword in self.detail_keywords):

            return 20

        return DEFAULT_TOP_K

    def search(self, question):

        question = question.strip()

        if not question:

            return []

        top_k = self.detect_top_k(question)

        return self.hybrid.retrieve(

            question,

            top_k=top_k

        )