from collections import defaultdict


class ClaimExtractor:

    """
    Extracts important claims from retrieved
    document chunks.

    This is used before sending data to the LLM
    for Research Brief generation.
    """

    def __init__(self):

        pass

    # =====================================================
    # Extract Claims
    # =====================================================

    def extract(self, documents):

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

            return {}

        grouped = defaultdict(list)

        for item in documents:

            source = item.get(

                "source",

                "Unknown"

            )

            text = item.get(

                "text",

                ""

            ).strip()

            page = item.get(

                "page",

                "-"

            )

            if not text:

                continue

            grouped[source].append(

                {

                    "page": page,

                    "claim": text

                }

            )

        claims = {}

        for source, values in grouped.items():

            unique = []

            seen = set()

            for item in values:

                normalized = " ".join(

                    item["claim"].split()

                ).lower()

                if normalized in seen:

                    continue

                seen.add(normalized)

                unique.append(item)

            claims[source] = unique

        return claims

    # =====================================================
    # Markdown
    # =====================================================

    def to_markdown(self, claims):

        md = "# Key Claims\n\n"

        if not claims:

            md += "No claims detected."

            return md

        for pdf, items in claims.items():

            md += f"## {pdf}\n\n"

            for i, item in enumerate(

                items,

                start=1

            ):

                md += (

                    f"{i}. "

                    f"{item['claim']}\n"

                )

                md += (

                    f"   - Page: "

                    f"{item['page']}\n"

                )

            md += "\n"

        return md

    # =====================================================
    # Flat List
    # =====================================================

    def get_all_claims(self, claims):

        output = []

        for pdf, items in claims.items():

            for item in items:

                output.append(

                    {

                        "source": pdf,

                        "page": item["page"],

                        "claim": item["claim"]

                    }

                )

        return output