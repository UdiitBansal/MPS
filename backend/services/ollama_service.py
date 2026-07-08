import requests

from backend.config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    TEMPERATURE,
    TOP_P,
    TOP_K,
    REPEAT_PENALTY,
    MAX_CONTEXT_CHARACTERS,
    SUMMARY_MAX_TOKENS,
    COMPARE_MAX_TOKENS,
    QA_MAX_TOKENS
)


class OllamaService:

    def __init__(self):

        self.url = f"{OLLAMA_HOST}/api/generate"

    def generate(self, question, context):

        question = question.strip()
        q = question.lower()

        # ---------------------------------------------------
        # Limit Context Size
        # ---------------------------------------------------

        if len(context) > MAX_CONTEXT_CHARACTERS:

            context = context[:MAX_CONTEXT_CHARACTERS]

        # ---------------------------------------------------
        # Detect Query Type
        # ---------------------------------------------------

        summary = any(word in q for word in [

            "summary",
            "summarize",
            "summarise",
            "overall summary",
            "executive summary",
            "research report",
            "all pdf",
            "all pdfs",
            "all documents"

        ])

        compare = any(word in q for word in [

            "compare",
            "comparison",
            "difference",
            "differences",
            "similarity",
            "similarities",
            "contrast",
            "common",
            "versus",
            "vs"

        ])

        # ---------------------------------------------------
        # Summary + Compare
        # ---------------------------------------------------

        if summary and compare:

            num_predict = SUMMARY_MAX_TOKENS

            instructions = """
Generate a complete research report.

Format:

# Executive Summary

# Document-wise Summary

For every uploaded PDF provide:

- Document Name
- Purpose
- Main Topics
- Important Points

# Similarities

# Differences

# Key Findings

# Conclusion

Rules:

- Use ONLY the supplied context.
- Never invent information.
- Remove duplicate information.
- Use markdown headings.
- Keep the report concise and professional.
"""

        # ---------------------------------------------------
        # Summary
        # ---------------------------------------------------

        elif summary:

            num_predict = SUMMARY_MAX_TOKENS

            instructions = """
Generate a professional research summary.

Format:

# Executive Summary

# Document-wise Summary

For every uploaded PDF include:

- Document Name
- Purpose
- Main Topics
- Important Points

# Overall Findings

# Conclusion

Rules:

- Use ONLY the supplied context.
- Never invent information.
- Remove duplicate information.
- Use markdown headings.
"""

        # ---------------------------------------------------
        # Comparison
        # ---------------------------------------------------

        elif compare:

            num_predict = COMPARE_MAX_TOKENS

            instructions = """
Compare all uploaded PDFs.

Include:

# Documents Compared

# Similarities

# Differences

# Comparison Table

# Conclusion

Rules:

- Use ONLY the supplied context.
- Never invent information.
- Remove duplicate information.
- Use markdown.
"""

        # ---------------------------------------------------
        # Question Answering
        # ---------------------------------------------------

        else:

            num_predict = QA_MAX_TOKENS

            instructions = """
Answer ONLY from the supplied context.

Rules:

- Give the answer first.
- Explain briefly.
- Use bullet points where appropriate.
- Never mention chunk numbers, scores or metadata.
- Never invent information.

If the answer cannot be found reply exactly:

I could not find the answer in the uploaded documents.
"""

        # ---------------------------------------------------
        # Prompt
        # ---------------------------------------------------

        prompt = f"""
You are an AI Research Assistant.

Answer ONLY from the supplied context.

If the answer is unavailable reply exactly:

I could not find the answer in the uploaded documents.

========================
CONTEXT
========================

{context}

========================
QUESTION
========================

{question}

========================
TASK
========================

{instructions}

========================
ANSWER
========================
"""

        try:

            response = requests.post(

                self.url,

                json={

                    "model": OLLAMA_MODEL,

                    "prompt": prompt,

                    "stream": False,

                    "keep_alive": "30m",

                    "options": {

                        "temperature": TEMPERATURE,

                        "top_p": TOP_P,

                        "top_k": TOP_K,

                        "repeat_penalty": REPEAT_PENALTY,

                        "num_predict": num_predict,

                        "stop": [

                            "QUESTION",
                            "CONTEXT",
                            "TASK"

                        ]

                    }

                },

                timeout=OLLAMA_TIMEOUT

            )

            response.raise_for_status()

            answer = response.json().get(

                "response",
                ""

            ).strip()

            if not answer:

                return "I could not find the answer in the uploaded documents."

            return answer

        except requests.exceptions.RequestException as e:

            return f"Ollama connection error: {str(e)}"

        except Exception as e:

            return f"Unexpected error: {str(e)}"