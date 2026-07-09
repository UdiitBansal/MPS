from collections import defaultdict
from sentence_transformers import util


class ThemeExtractor:

    def __init__(self, embedder):

        self.embedder = embedder

    # =====================================================
    # Extract Themes
    # =====================================================

    def extract(self, documents, similarity_threshold=0.70):

        """
        documents = [
            {
                "source": "...",
                "text": "...",
                "page": ...
            }
        ]
        """

        if not documents:

            return []

        texts = [

            doc["text"]

            for doc in documents

        ]

        embeddings = self.embedder.encode(texts)

        similarity = util.cos_sim(

            embeddings,

            embeddings

        ).cpu().numpy()

        visited = set()

        themes = []

        for i in range(len(documents)):

            if i in visited:

                continue

            cluster = []

            for j in range(len(documents)):

                if similarity[i][j] >= similarity_threshold:

                    cluster.append(

                        documents[j]

                    )

                    visited.add(j)

            if cluster:

                themes.append(

                    self.build_theme(cluster)

                )

        return themes

    # =====================================================
    # Build Theme
    # =====================================================

    def build_theme(self, cluster):

        sources = sorted(

            {

                item["source"]

                for item in cluster

            }

        )

        combined = "\n".join(

            item["text"]

            for item in cluster

        )

        preview = combined[:600]

        return {

            "theme": preview,

            "documents": sources,

            "count": len(cluster),

            "text": combined

        }

    # =====================================================
    # Markdown
    # =====================================================

    def to_markdown(self, themes):

        md = "# Cross Document Themes\n\n"

        if not themes:

            md += "No common themes detected."

            return md

        for i, theme in enumerate(themes, start=1):

            md += f"## Theme {i}\n\n"

            md += "**Documents**\n\n"

            for doc in theme["documents"]:

                md += f"- {doc}\n"

            md += "\n"

            md += "**Discussion**\n\n"

            md += theme["theme"]

            md += "\n\n---\n\n"

        return md