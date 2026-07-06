class PromptBuilder:

    @staticmethod
    def build(contexts, question):

        context = "\n\n".join(contexts)

        prompt = f"""
You are an AI Research Assistant.

Answer ONLY using the provided context.

If the answer is not present, reply:
"I could not find the answer in the uploaded documents."

=========================
Context

{context}

=========================

Question:
{question}

Answer:
"""

        return prompt