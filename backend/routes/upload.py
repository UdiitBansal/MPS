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

    # ---------------------------------------
    # Validation
    # ---------------------------------------

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

    # ---------------------------------------
    # Remove Previous PDFs
    # ---------------------------------------

    for pdf in upload_path.glob("*.pdf"):

        try:

            pdf.unlink()

        except Exception:

            pass

    uploaded_files = []

    total_size = 0

    used_names = set()

    # ---------------------------------------
    # Save PDFs
    # ---------------------------------------

    for file in files:

        if not file.filename:

            raise HTTPException(

                status_code=400,

                detail="Invalid filename."

            )

        filename = Path(file.filename).name.strip()

        extension = Path(filename).suffix.lower()

        if extension not in SUPPORTED_FILE_TYPES:

            raise HTTPException(

                status_code=400,

                detail=f"{filename} is not a supported PDF."

            )

        # Prevent duplicate names

        original_name = Path(filename).stem

        counter = 1

        while filename in used_names:

            filename = f"{original_name}_{counter}.pdf"

            counter += 1

        used_names.add(filename)

        destination = upload_path / filename

        try:

            with open(destination, "wb") as buffer:

                shutil.copyfileobj(

                    file.file,

                    buffer

                )

        finally:

            file.file.close()

        if not destination.exists():

            raise HTTPException(

                status_code=500,

                detail=f"Failed to save {filename}."

            )

        size = destination.stat().st_size

        if size == 0:

            destination.unlink(missing_ok=True)

            raise HTTPException(

                status_code=400,

                detail=f"{filename} is empty."

            )

        if size > MAX_FILE_SIZE_MB * 1024 * 1024:

            destination.unlink(missing_ok=True)

            raise HTTPException(

                status_code=400,

                detail=f"{filename} exceeds {MAX_FILE_SIZE_MB} MB."

            )

        uploaded_files.append(filename)

        total_size += size

    # ---------------------------------------
    # Response
    # ---------------------------------------

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