import requests

from backend.config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    TEMPERATURE,
    TOP_P,
    TOP_K,
    REPEAT_PENALTY,
    MAX_TOKENS
)


class OllamaService:

    def __init__(self):

        self.url = f"{OLLAMA_HOST}/api/generate"

    def generate(self, question, context):

        q = question.lower()

        # ---------------- SUMMARY ----------------

        if any(word in q for word in [

            "summary",
            "summarize",
            "summarise",
            "overall summary",
            "executive summary",
            "all pdf",
            "all documents",
            "research report"

        ]):

            instructions = """
Generate a document-wise summary.

Rules:

- Treat every PDF separately.
- Use the PDF name as the heading.
- Summarize only that PDF.
- Never mix documents.
- Use concise bullet points.
- Remove duplicate information.
- End with a short Overall Summary.
- Use ONLY the supplied context.
"""

        # ---------------- COMPARISON ----------------

        elif any(word in q for word in [

            "compare",
            "comparison",
            "difference",
            "differences",
            "similarity",
            "common",
            "contrast"

        ]):

            instructions = """
Compare the uploaded documents.

Rules:

- Mention every PDF separately.
- Show similarities.
- Show differences.
- Use a markdown table whenever appropriate.
- End with a conclusion.
- Use ONLY the supplied context.
"""

        # ---------------- NORMAL QA ----------------

        else:

            instructions = """
Answer ONLY from the supplied context.

Rules:

- Give the answer first.
- Then explain briefly.
- Use headings and bullets.
- Combine information naturally.
- Do not repeat sentences.
- Ignore duplicate chunks.
- Do NOT mention:
    - Chunk number
    - Relevance score
    - Context number
- Never invent information.
- If the answer is unavailable reply exactly:

I could not find the answer in the uploaded documents.
"""

        prompt = f"""
You are an AI Research Assistant.

You MUST answer ONLY from the supplied context.

Never use outside knowledge.

Never hallucinate.

Never mention chunk numbers,
document numbers,
retrieval scores,
or internal metadata.

==========================
CONTEXT
==========================

{context}

==========================
QUESTION
==========================

{question}

==========================
INSTRUCTIONS
==========================

{instructions}

==========================
ANSWER
==========================
"""

        response = requests.post(

            self.url,

            json={

                "model": OLLAMA_MODEL,

                "prompt": prompt,

                "stream": False,

                "options": {

                    "temperature": TEMPERATURE,

                    "top_p": TOP_P,

                    "top_k": TOP_K,

                    "repeat_penalty": REPEAT_PENALTY,

                    "num_predict": MAX_TOKENS

                }

            },

            timeout=OLLAMA_TIMEOUT

        )

        response.raise_for_status()

        return response.json()["response"].strip()