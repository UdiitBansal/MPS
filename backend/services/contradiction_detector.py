from itertools import combinations

from sentence_transformers import util


class ContradictionDetector:

    """
    Detects possible contradictions between
    different PDF documents.

    NOTE:
    This is semantic contradiction detection.
    Final verification is performed by the LLM.
    """

    def __init__(self, embedder):

        self.embedder = embedder

    # =====================================================
    # Detect Contradictions
    # =====================================================

    def detect(

        self,

        documents,

        similarity_threshold=0.40

    ):

        if not documents:

            return []

        texts = [

            doc["text"]

            for doc in documents

        ]

        embeddings = self.embedder.encode(

            texts

        )

        contradictions = []

        for i, j in combinations(

            range(len(documents)),

            2

        ):

            doc1 = documents[i]

            doc2 = documents[j]

            # Skip same PDF

            if doc1["source"] == doc2["source"]:

                continue

            similarity = util.cos_sim(

                embeddings[i],

                embeddings[j]

            ).item()

            # Low semantic similarity
            # means possible contradiction

            if similarity <= similarity_threshold:

                contradictions.append(

                    {

                        "document_a": doc1["source"],

                        "page_a": doc1.get(

                            "page",

                            "-"

                        ),

                        "statement_a": doc1["text"],

                        "document_b": doc2["source"],

                        "page_b": doc2.get(

                            "page",

                            "-"

                        ),

                        "statement_b": doc2["text"],

                        "similarity": round(

                            similarity,

                            4

                        )

                    }

                )

        return contradictions

    # =====================================================
    # Markdown
    # =====================================================

    def to_markdown(

        self,

        contradictions

    ):

        md = "# Contradiction Report\n\n"

        if not contradictions:

            md += "No contradictions detected."

            return md

        for i, item in enumerate(

            contradictions,

            start=1

        ):

            md += f"## Contradiction {i}\n\n"

            md += (

                f"### {item['document_a']}\n\n"

            )

            md += (

                f"Page : {item['page_a']}\n\n"

            )

            md += (

                item["statement_a"]

            )

            md += "\n\n"

            md += (

                f"### {item['document_b']}\n\n"

            )

            md += (

                f"Page : {item['page_b']}\n\n"

            )

            md += (

                item["statement_b"]

            )

            md += "\n\n"

            md += (

                f"Similarity : "

                f"{item['similarity']}\n\n"

            )

            md += "---\n\n"

        return md

    # =====================================================
    # Summary
    # =====================================================

    def summary(

        self,

        contradictions

    ):

        return {

            "total": len(

                contradictions

            ),

            "items": contradictions

        }