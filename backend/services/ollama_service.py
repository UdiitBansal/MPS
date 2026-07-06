import requests

from backend.config import OLLAMA_MODEL


class OllamaService:

    def __init__(self):

        self.url = "http://localhost:11434/api/generate"

    def generate(self, question, context):

        question_lower = question.lower()

        if any(keyword in question_lower for keyword in [

            "summary",
            "summarize",
            "summarise",
            "summary of all",
            "all pdf",
            "all pdfs",
            "all documents",
            "overall summary",
            "complete",
            "entire",
            "whole",
            "full",
            "research report"

        ]):

            instructions = """
You are an AI Research Assistant.

Answer ONLY using the provided context.

Rules:

1. Generate a document-wise summary.
2. Create a heading for each document.
3. Summarize each document in bullet points.
4. Do NOT mix information from different documents.
5. Ignore duplicate information.
6. End with an Overall Summary.
7. Never invent information.
8. Never use outside knowledge.
9. If information is unavailable, say so.
"""

        elif any(keyword in question_lower for keyword in [

            "compare",
            "comparison",
            "difference",
            "differences",
            "common",
            "similar",
            "contrast"

        ]):

            instructions = """
You are an AI Research Assistant.

Answer ONLY using the provided context.

Rules:

1. Compare the uploaded documents.
2. Show similarities.
3. Show differences.
4. Mention document names whenever possible.
5. Use headings and bullet points.
6. Do NOT invent information.
7. Ignore unrelated context.
"""

        else:

            instructions = """
You are an AI Research Assistant.

Answer ONLY using the provided context.

Rules:

1. First give a direct answer.
2. Then explain the answer.
3. Use headings.
4. Use bullet points whenever useful.
5. Keep the answer concise and readable.
6. Do not repeat sentences.
7. Do not use outside knowledge.
8. If the answer is not found in the uploaded documents, reply:

'I could not find the answer in the uploaded documents.'
"""

        prompt = f"""
{instructions}

==========================================
CONTEXT
==========================================

{context}

==========================================
QUESTION
==========================================

{question}

==========================================
ANSWER
==========================================
"""

        response = requests.post(

            self.url,

            json={

                "model": OLLAMA_MODEL,

                "prompt": prompt,

                "stream": False,

                "options": {

                    "temperature": 0.1,

                    "top_p": 0.9,

                    "top_k": 40,

                    "repeat_penalty": 1.15,

                    "num_predict": 1024

                }

            },

            timeout=300

        )

        response.raise_for_status()

        answer = response.json()["response"].strip()

        return answer