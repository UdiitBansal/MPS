from collections import defaultdict


class ResearchBriefGenerator:

    """
    Generates a professional research brief
    from retrieved document chunks.
    """

    # =====================================================
    # Build Research Brief
    # =====================================================

    def generate(

        self,

        summaries="",

        claims=None,

        themes=None,

        contradictions=None

    ):

        if claims is None:

            claims = {}

        if themes is None:

            themes = []

        if contradictions is None:

            contradictions = []

        md = "# Research Brief\n\n"

        # =================================================
        # Executive Summary
        # =================================================

        md += "## Executive Summary\n\n"

        if summaries:

            md += summaries.strip()

        else:

            md += "No summary available."

        md += "\n\n"

        # =================================================
        # Documents
        # =================================================

        md += "## Documents Analysed\n\n"

        for pdf in claims.keys():

            md += f"- {pdf}\n"

        if not claims:

            md += "No documents.\n"

        md += "\n"

        # =================================================
        # Key Claims
        # =================================================

        md += "## Key Claims\n\n"

        if claims:

            for pdf, items in claims.items():

                md += f"### {pdf}\n\n"

                for item in items:

                    md += (

                        f"- {item['claim']}\n"

                    )

                md += "\n"

        else:

            md += "No claims extracted.\n\n"

        # =================================================
        # Themes
        # =================================================

        md += "## Cross Document Themes\n\n"

        if themes:

            for i, theme in enumerate(

                themes,

                start=1

            ):

                md += (

                    f"### Theme {i}\n\n"

                )

                md += (

                    "**Documents**\n"

                )

                for doc in theme["documents"]:

                    md += f"- {doc}\n"

                md += "\n"

                md += (

                    "**Discussion**\n\n"

                )

                md += (

                    theme["theme"]

                )

                md += "\n\n"

        else:

            md += "No common themes detected.\n\n"

        # =================================================
        # Contradictions
        # =================================================

        md += "## Contradictions\n\n"

        if contradictions:

            for item in contradictions:

                md += (

                    f"### {item['document_a']} ↔ {item['document_b']}\n\n"

                )

                md += (

                    f"Similarity : {item['similarity']}\n\n"

                )

                md += "**Statement A**\n\n"

                md += (

                    item["statement_a"]

                )

                md += "\n\n"

                md += "**Statement B**\n\n"

                md += (

                    item["statement_b"]

                )

                md += "\n\n---\n\n"

        else:

            md += "No contradictions detected.\n\n"

        # =================================================
        # Research Gaps
        # =================================================

        md += "## Research Gaps\n\n"

        md += (
            "- Some topics may require additional documents.\n"
            "- Some claims may require verification using external sources.\n"
            "- Contradictory information should be manually reviewed.\n\n"
        )

        # =================================================
        # Conclusion
        # =================================================

        md += "## Final Conclusion\n\n"

        md += (
            "This research brief was generated automatically "
            "using Hybrid Retrieval, ChromaDB, BM25, "
            "Sentence Transformers and Ollama."
        )

        return md

    # =====================================================
    # Save Markdown
    # =====================================================

    def save(

        self,

        markdown,

        filepath

    ):

        with open(

            filepath,

            "w",

            encoding="utf-8"

        ) as f:

            f.write(markdown)

        return filepath