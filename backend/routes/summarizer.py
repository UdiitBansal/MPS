from collections import OrderedDict
from typing import Dict, List

from backend.services.ollama_service import OllamaService


class Summarizer:
    """
    Generates:
        1. Individual document summaries
        2. Executive summary across all documents
    """

    def __init__(self):
        self.ollama = OllamaService()

    # =====================================================
    # GROUP DOCUMENTS
    # =====================================================

    @staticmethod
    def group_documents(documents: List[Dict]) -> Dict[str, List[Dict]]:

        grouped = OrderedDict()

        for doc in documents:

            source = doc.get("source", "Unknown")

            grouped.setdefault(source, []).append(doc)

        return grouped

    # =====================================================
    # REMOVE DUPLICATE BULLETS
    # =====================================================

    @staticmethod
    def remove_duplicates(text: str) -> str:

        lines = []

        seen = set()

        for line in text.splitlines():

            cleaned = " ".join(
                line.strip().split()
            ).lower()

            if not cleaned:
                continue

            if cleaned in seen:
                continue

            seen.add(cleaned)

            lines.append(line.rstrip())

        return "\n".join(lines)

    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    @staticmethod
    def build_context(chunks: List[Dict]) -> str:

        context = []

        for chunk in chunks:

            context.append(
                f"""
==================================================
PDF : {chunk.get("source")}
Page : {chunk.get("page")}
==================================================

{chunk.get("text")}
"""
            )

        return "\n".join(context)

    # =====================================================
    # SINGLE DOCUMENT SUMMARY
    # =====================================================

    def summarize_document(
        self,
        source: str,
        chunks: List[Dict]
    ) -> str:

        context = self.build_context(chunks)

        prompt = (
            f"Generate a detailed summary of the document '{source}'. "
            "Include purpose, important topics, key findings and conclusion."
        )

        summary = self.ollama.generate(
            question=prompt,
            context=context
        )

        summary = self.remove_duplicates(summary)

        return summary

    # =====================================================
    # DOCUMENT-WISE SUMMARY
    # =====================================================

    def document_summaries(
        self,
        documents: List[Dict]
    ) -> Dict[str, str]:

        grouped = self.group_documents(documents)

        summaries = {}

        for source, chunks in grouped.items():

            summaries[source] = self.summarize_document(
                source,
                chunks
            )

        return summaries

    # =====================================================
    # EXECUTIVE SUMMARY
    # =====================================================

    def executive_summary(
        self,
        document_summaries: Dict[str, str]
    ) -> str:

        merged = []

        for source, summary in document_summaries.items():

            merged.append(
                f"""
# {source}

{summary}
"""
            )

        context = "\n\n".join(merged)

        prompt = """
Generate a professional Executive Summary.

Format:

# Executive Summary

## Overall Purpose

## Main Topics

## Key Findings

## Common Themes

## Important Conclusions

Rules:

- Use every document.
- Remove duplicate information.
- Mention differences only if important.
- Do not hallucinate.
"""

        summary = self.ollama.generate(
            question=prompt,
            context=context
        )

        return self.remove_duplicates(summary)

    # =====================================================
    # COMPLETE SUMMARY
    # =====================================================

    def generate_summary(
        self,
        documents: List[Dict]
    ) -> Dict:

        document_summaries = self.document_summaries(
            documents
        )

        executive = self.executive_summary(
            document_summaries
        )

        return {

            "executive_summary": executive,

            "document_summaries": document_summaries

        }