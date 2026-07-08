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

    q = question.lower()

    # ------------------------------------------
    # Decide number of chunks
    # ------------------------------------------

    if any(word in q for word in [

        "summary",
        "summarize",
        "summarise",
        "overall summary",
        "executive summary",
        "research report",
        "all pdf",
        "all documents"

    ]):

        max_chunks = 20

    elif any(word in q for word in [

        "compare",
        "comparison",
        "difference",
        "differences",
        "similarity",
        "similarities",
        "contrast",
        "common"

    ]):

        max_chunks = 15

    else:

        max_chunks = 8

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

    seen = set()

    for item in retrieved_chunks:

        if len(context_parts) >= max_chunks:
            break

        if not isinstance(item, dict):

            item = {
                "source": "Unknown",
                "page": "-",
                "chunk": "-",
                "score": 0,
                "text": str(item)
            }

        text = item.get("text", "").strip()

        if not text:
            continue

        # Stable duplicate detection
        key = " ".join(text.split())

        if key in seen:
            continue

        seen.add(key)

        context_parts.append(
            f"""
==============================
PDF : {item.get('source', 'Unknown')}
Page : {item.get('page', '-')}
Chunk : {item.get('chunk', '-')}
==============================

{text}
"""
        )

        source_list.append({

            "source": item.get("source", "Unknown"),

            "page": item.get("page", "-"),

            "chunk": item.get("chunk", "-"),

            "score": round(float(item.get("score", 0)), 4),

            "text": text[:700]

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

        "retrieved_chunks": len(context_parts),

        "total_sources": len(source_list)

    }