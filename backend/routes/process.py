from time import perf_counter

from fastapi import APIRouter

from backend.indexes.document_index import index
from backend.config import OLLAMA_MODEL

router = APIRouter(
    prefix="/process",
    tags=["Processing"]
)


@router.post("/")
def process_documents():

    start = perf_counter()

    result = index.build()

    end = perf_counter()

    processing_time = round(end - start, 2)

    result["processing_time"] = processing_time

    result["model"] = OLLAMA_MODEL

    if result.get("status") == "success":

        result["message"] = "Documents processed successfully."

    print(result)

    return result