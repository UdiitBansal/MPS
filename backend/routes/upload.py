from pathlib import Path
import shutil

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile
)

from backend.config import (
    MAX_PDFS,
    MAX_FILE_SIZE_MB,
    SUPPORTED_FILE_TYPES,
    UPLOAD_DIR
)

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/")
async def upload_pdfs(
    files: list[UploadFile] = File(...)
):

    if not files:

        raise HTTPException(

            status_code=400,

            detail="Please upload at least one PDF."

        )

    if len(files) > MAX_PDFS:

        raise HTTPException(

            status_code=400,

            detail=f"Maximum {MAX_PDFS} PDF files are allowed."

        )

    upload_path = Path(UPLOAD_DIR)

    upload_path.mkdir(

        parents=True,

        exist_ok=True

    )

    # Remove previous PDFs
    for pdf in upload_path.glob("*.pdf"):

        try:

            pdf.unlink()

        except Exception:

            pass

    uploaded_files = []

    total_size = 0

    for file in files:

        filename = Path(file.filename).name

        extension = Path(filename).suffix.lower()

        if extension not in SUPPORTED_FILE_TYPES:

            raise HTTPException(

                status_code=400,

                detail=f"{filename} is not a supported PDF."

            )

        destination = upload_path / filename

        with open(destination, "wb") as buffer:

            shutil.copyfileobj(

                file.file,

                buffer

            )

        size = destination.stat().st_size

        if size > MAX_FILE_SIZE_MB * 1024 * 1024:

            destination.unlink(missing_ok=True)

            raise HTTPException(

                status_code=400,

                detail=f"{filename} exceeds {MAX_FILE_SIZE_MB} MB."

            )

        uploaded_files.append(filename)

        total_size += size

    return {

        "status": "success",

        "message": "PDFs uploaded successfully.",

        "uploaded_files": uploaded_files,

        "total_files": len(uploaded_files),

        "total_size_bytes": total_size,

        "total_size_mb": round(

            total_size / (1024 * 1024),

            2

        )

    }