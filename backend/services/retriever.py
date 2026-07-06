from backend.services.hybrid_retriever import HybridRetriever
from backend.indexes.document_index import index


class Retriever:

    def __init__(self):

        self.retriever = HybridRetriever(
            chroma=index.chroma,
            bm25=index.bm25,
            embedder=index.embedder
        )

    def search(self, question):

        question = question.strip()

        if not question:
            return []

        q = question.lower()

        summary_keywords = [

            "summary",
            "summarize",
            "summarise",
            "executive summary",
            "overall summary",
            "complete summary",
            "summary of all",
            "all pdf",
            "all pdfs",
            "all documents",
            "research report",
            "report"

        ]

        compare_keywords = [

            "compare",
            "comparison",
            "difference",
            "differences",
            "similarity",
            "similarities",
            "common",
            "common topics",
            "same",
            "unique",
            "contrast"

        ]

        detailed_keywords = [

            "architecture",
            "design",
            "workflow",
            "implementation",
            "methodology",
            "algorithm",
            "framework",
            "system",
            "pipeline",
            "component"

        ]

        if any(keyword in q for keyword in summary_keywords):

            top_k = 35

        elif any(keyword in q for keyword in compare_keywords):

            top_k = 30

        elif any(keyword in q for keyword in detailed_keywords):

            top_k = 20

        else:

            top_k = 10

        return self.retriever.retrieve(
            question,
            top_k=top_k
        )