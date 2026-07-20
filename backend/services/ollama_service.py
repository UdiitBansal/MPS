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
    QA_MAX_TOKENS,
    CLAIM_MAX_TOKENS,
    THEME_MAX_TOKENS,
    CONTRADICTION_MAX_TOKENS,
    RESEARCH_BRIEF_MAX_TOKENS
)


class OllamaService:

    def __init__(self):

        self.url = f"{OLLAMA_HOST}/api/generate"

    # ======================================================
    # Detect Query Type
    # ======================================================

    @staticmethod
    def detect_query(question: str):

        q = question.lower().strip()

        summary = any(word in q for word in [

            "summary",
            "summarize",
            "summarise",
            "overall summary",
            "executive summary",
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
            "vs",
            "versus"

        ])

        claims = any(word in q for word in [

            "claim",
            "claims",
            "key claim",
            "key claims",
            "important claims",
            "main claims"

        ])

        themes = any(word in q for word in [

            "theme",
            "themes",
            "topic",
            "topics",
            "cluster",
            "clustering"

        ])

        contradictions = any(word in q for word in [

            "contradiction",
            "contradict",
            "conflict",
            "opposite",
            "disagree"

        ])

        report = any(word in q for word in [

            "research brief",
            "research report",
            "full report",
            "complete report"

        ])

        return {

            "summary": summary,

            "compare": compare,

            "claims": claims,

            "themes": themes,

            "contradictions": contradictions,

            "report": report

        }

    # ======================================================
    # Context Limiter
    # ======================================================

    @staticmethod
    def trim_context(context):

        if len(context) <= MAX_CONTEXT_CHARACTERS:

            return context

        return context[:MAX_CONTEXT_CHARACTERS]

    # ======================================================
    # Prompt Builder
    # ======================================================

    @staticmethod
    def build_prompt(question, context, instructions):

        return f"""
You are an AI Research Assistant.

You MUST answer ONLY from the supplied context.

Never use outside knowledge.

Never hallucinate.

Never fabricate facts.

Never mention:

- Chunk Number
- Retrieval Score
- Metadata
- Internal IDs

If information is unavailable reply exactly:

I could not find the answer in the uploaded documents.

==================================================
CONTEXT
==================================================

{context}

==================================================
QUESTION
==================================================

{question}

==================================================
TASK
==================================================

{instructions}

==================================================
ANSWER
==================================================
"""
    # ======================================================
    # Prompt Selector
    # ======================================================

    def get_prompt(self, question):

        flags = self.detect_query(question)

        # --------------------------------------------------
        # Research Brief
        # --------------------------------------------------

        if flags["report"]:

            return (
                RESEARCH_BRIEF_MAX_TOKENS,
                """
Generate a professional Research Brief.

Format:

# Executive Summary

# Documents Analysed

# Main Themes

# Key Claims

# Similarities

# Differences

# Contradictions

# Research Gaps

# Final Conclusion

Rules:

- Use ONLY the supplied context.
- Never invent information.
- Merge duplicate information.
- Use markdown headings.
- Use bullet points.
- Mention PDF names whenever possible.
"""
            )

        # --------------------------------------------------
        # Summary + Comparison
        # --------------------------------------------------

        if flags["summary"] and flags["compare"]:

            return (
                RESEARCH_BRIEF_MAX_TOKENS,
                """
Generate a complete research report.

Format:

# Executive Summary

# Document-wise Summary

# Similarities

# Differences

# Key Findings

# Conclusion

Rules:

- Use ONLY supplied context.
- Never hallucinate.
- Remove duplicate information.
- Mention every PDF.
"""
            )

        # --------------------------------------------------
        # Summary
        # --------------------------------------------------

        if flags["summary"]:

            return (
                SUMMARY_MAX_TOKENS,
                """
Generate a document-wise summary.

Format:

# Executive Summary

For EACH PDF include

## PDF Name

Purpose

Main Topics

Important Points

Key Findings

Finish with

# Overall Summary

Rules

- Never mix documents.
- Never invent information.
- Use markdown headings.
"""
            )

        # --------------------------------------------------
        # Comparison
        # --------------------------------------------------

        if flags["compare"]:

            return (
                COMPARE_MAX_TOKENS,
                """
Compare all uploaded PDFs.

Format

# Documents Compared

# Similarities

# Differences

# Comparison Table

# Conclusion

Rules

- Mention every PDF.
- Use markdown table.
- Never invent information.
- Do NOT say
'I could not find the answer'
if documents exist.
"""
            )

        # --------------------------------------------------
        # Key Claims
        # --------------------------------------------------

        if flags["claims"]:

            return (
                CLAIM_MAX_TOKENS,
                """
Extract the important claims.

For every PDF provide

# PDF Name

## Key Claims

• Claim 1

• Claim 2

• Claim 3

Mention supporting evidence when available.

Never invent claims.
Only use supplied context.
"""
            )

        # --------------------------------------------------
        # Themes
        # --------------------------------------------------

        if flags["themes"]:

            return (
                THEME_MAX_TOKENS,
                """
Identify cross-document themes.

Format

# Theme 1

Documents

Key Discussion

----------------

# Theme 2

Documents

Key Discussion

----------------

# Overall Themes

Rules

- Group similar topics.
- Mention PDF names.
- Never invent information.
"""
            )

        # --------------------------------------------------
        # Contradictions
        # --------------------------------------------------

        if flags["contradictions"]:

            return (
                CONTRADICTION_MAX_TOKENS,
                """
Find contradictory information.

Format

# Contradictions

PDF A

Statement

PDF B

Statement

Reason

If no contradiction exists say

"No contradictions were found."

Never invent contradictions.
"""
            )

        # --------------------------------------------------
        # Default QA
        # --------------------------------------------------

        return (
            QA_MAX_TOKENS,
            """
Answer ONLY from the supplied context.

Rules

- Give answer first.
- Explain briefly.
- Use bullets.
- Never mention metadata.
- Never hallucinate.

If unavailable reply exactly

I could not find the answer in the uploaded documents.
"""
        )

    # ======================================================
    # Generate Response
    # ======================================================

    def generate(self, question, context):

        question = question.strip()

        if not question:

            return "Please enter a question."

        context = self.trim_context(context)

        num_predict, instructions = self.get_prompt(question)

        prompt = self.build_prompt(

            question,

            context,

            instructions

        )

        payload = {

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

                    "TASK",

                    "ANSWER"

                ]

            }

        }

        try:

            response = requests.post(

                self.url,

                json=payload,

                timeout=OLLAMA_TIMEOUT

            )

            response.raise_for_status()

            data = response.json()
            print("\n========== OLLAMA RESPONSE ==========")
            print(data)
            print("=====================================")

            answer = data.get(

                "response",

                ""

            ).strip()

            if not answer:

                return "I could not find the answer in the uploaded documents."

            # ------------------------------------------
            # Cleanup
            # ------------------------------------------

            answer = answer.replace(

                "Answer:",

                ""

            ).replace(

                "ANSWER:",

                ""

            ).strip()

            while "\n\n\n" in answer:

                answer = answer.replace(

                    "\n\n\n",

                    "\n\n"

                )

            if len(answer) > 5:

                return answer

            return "I could not find the answer in the uploaded documents."

        except requests.exceptions.Timeout:

            return (

                "The language model took too long to respond. "

                "Please try again."

            )

        except requests.exceptions.ConnectionError:

            return (

                "Unable to connect to Ollama. "

                "Please make sure Ollama is running."

            )

        except requests.exceptions.HTTPError as e:

            return f"Ollama HTTP Error: {e}"

        except requests.exceptions.RequestException as e:

            return f"Request Error: {e}"

        except Exception as e:

            return f"Unexpected Error: {e}"