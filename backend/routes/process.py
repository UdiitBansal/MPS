from time import perf_counter
import logging

from fastapi import APIRouter, HTTPException

from backend.indexes.document_index import index
from backend.config import (
    OLLAMA_MODEL,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/process",
    tags=["Processing"]
)


@router.post("/")
def process_documents():

    start = perf_counter()

    try:
        result = index.build()

        processing_time = round(perf_counter() - start, 2)

        if not isinstance(result, dict):
            raise ValueError("Invalid response received from document index.")

        result["processing_time"] = processing_time

        result.setdefault("model", OLLAMA_MODEL)
        result.setdefault("embedding_model", EMBEDDING_MODEL)
        result.setdefault("chunk_size", CHUNK_SIZE)
        result.setdefault("chunk_overlap", CHUNK_OVERLAP)

        result.setdefault("index_type", "Hybrid Retrieval")
        result.setdefault("vector_database", "ChromaDB")
        result.setdefault("keyword_search", "BM25")

        if result.get("status") == "success":
            result["message"] = "Documents processed successfully."
            result["ready_for_chat"] = True
        else:
            result["ready_for_chat"] = False

        logger.info(result)

        return result

    except Exception as e:

        logger.exception("Document processing failed")

        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": str(e),
                "ready_for_chat": False
            }
        )


@router.get("/stats")
def processing_stats():

    executive_summary = getattr(index, "executive_summary", None)
    document_summaries = getattr(index, "document_summaries", [])

    return {

        "status": "success",

        "documents": len({
            doc["source"]
            for doc in index.documents
        }),

        "chunks": len(index.all_chunks),

        "embedding_model": EMBEDDING_MODEL,
        "llm": OLLAMA_MODEL,

        "retrieval": "Hybrid",
        "vector_database": "ChromaDB",
        "keyword_search": "BM25",

        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,

        "executive_summary_ready": executive_summary is not None,

        "document_summaries": len(document_summaries),
    }