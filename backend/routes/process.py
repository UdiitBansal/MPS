from time import perf_counter

from fastapi import APIRouter

from backend.indexes.document_index import index

from backend.config import (
    OLLAMA_MODEL,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)

router = APIRouter(
    prefix="/process",
    tags=["Processing"]
)


@router.post("/")
def process_documents():

    start = perf_counter()

    result = index.build()

    end = perf_counter()

    processing_time = round(
        end - start,
        2
    )

    result["processing_time"] = processing_time

    result["model"] = OLLAMA_MODEL

    result["embedding_model"] = EMBEDDING_MODEL

    result["chunk_size"] = CHUNK_SIZE

    result["chunk_overlap"] = CHUNK_OVERLAP

    result["index_type"] = "Hybrid Retrieval"

    result["vector_database"] = "ChromaDB"

    result["keyword_search"] = "BM25"

    if result.get("status") == "success":

        result["message"] = "Documents processed successfully."

        result["ready_for_chat"] = True

    else:

        result["ready_for_chat"] = False

    print(result)

    return result


@router.get("/stats")
def processing_stats():

    return {

        "status": "success",

        "documents": len(index.metadata),

        "chunks": len(index.all_chunks),

        "embedding_model": EMBEDDING_MODEL,

        "llm": OLLAMA_MODEL,

        "retrieval": "Hybrid",

        "vector_database": "ChromaDB",

        "keyword_search": "BM25",

        "chunk_size": CHUNK_SIZE,

        "chunk_overlap": CHUNK_OVERLAP

    }