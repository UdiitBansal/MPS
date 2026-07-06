import ollama

from backend.config import OLLAMA_MODEL


class OllamaClient:

    def __init__(self):
        self.model = OLLAMA_MODEL

    def ask(self, prompt):

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]