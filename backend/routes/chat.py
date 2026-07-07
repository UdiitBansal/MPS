from fastapi import APIRouter
from pydantic import BaseModel

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

    if not question:

        return {
            "status": "error",
            "question": "",
            "answer": "Please enter a question.",
            "sources": [],
            "retrieved_chunks": 0,
            "total_sources": 0
        }

    retrieved_chunks = retriever.search(question)

    if not retrieved_chunks:

        return {
            "status": "error",
            "question": question,
            "answer": "I could not find the answer in the uploaded documents.",
            "sources": [],
            "retrieved_chunks": 0,
            "total_sources": 0
        }

    context_parts = []

    source_list = []

    for i, item in enumerate(retrieved_chunks, start=1):

        if isinstance(item, dict):

            pdf = item.get("source", "Unknown")

            page = item.get("page", "-")

            chunk = item.get("chunk", "-")

            score = item.get("score", 0)

            text = item.get("text", "").strip()

            context_parts.append(
                f"""
==================================================
DOCUMENT {i}
==================================================

PDF: {pdf}
Page: {page}
Chunk: {chunk}

{text}
"""
            )

            source_list.append({

                "source": pdf,

                "page": page,

                "chunk": chunk,

                "score": score

            })

        else:

            text = str(item).strip()

            context_parts.append(
                f"""
==================================================
DOCUMENT {i}
==================================================

{text}
"""
            )

            source_list.append({

                "source": "Unknown",

                "page": "-",

                "chunk": i,

                "score": 0

            })

    context = "\n".join(context_parts)

    answer = ollama.generate(
        question,
        context
    )

    return {

        "status": "success",

        "question": question,

        "answer": answer,

        "sources": source_list,

        "retrieved_chunks": len(retrieved_chunks),

        "total_sources": len(source_list)

    }