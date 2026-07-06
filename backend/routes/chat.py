from pydantic import BaseModel
from fastapi import APIRouter

from backend.services.retriever import Retriever
from backend.services.ollama_service import OllamaService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

retriever = Retriever()
ollama = OllamaService()


class ChatRequest(BaseModel):
    question: str


@router.post("/")
def chat(request: ChatRequest):

    question = request.question.strip()

    if question == "":
        return {
            "status": "error",
            "question": "",
            "answer": "Please enter a question.",
            "sources": []
        }

    chunks = retriever.search(question)

    if len(chunks) == 0:
        return {
            "status": "error",
            "question": question,
            "answer": "I could not find the answer in the uploaded documents.",
            "sources": []
        }

    context = ""

    for index, chunk in enumerate(chunks, start=1):

        context += f"""

==============================
Context {index}
==============================

{chunk}

"""

    answer = ollama.generate(
        question,
        context
    )

    return {
        "status": "success",
        "question": question,
        "answer": answer,
        "sources": chunks,
        "total_sources": len(chunks)
    }