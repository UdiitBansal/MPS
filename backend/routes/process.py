from time import perf_counter

from fastapi import APIRouter

from backend.indexes.document_index import index

router = APIRouter(
    prefix="/process",
    tags=["Processing"]
)


@router.post("/")
def process_documents():

    start = perf_counter()

    result = index.build()

    end = perf_counter()

    if result.get("status") == "success":

        result["processing_time"] = round(
            end - start,
            2
        )

        result["message"] = "Documents processed successfully."

    else:

        result["processing_time"] = round(
            end - start,
            2
        )

    print(result)

    return result