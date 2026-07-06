from pathlib import Path
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.config import MAX_PDFS, UPLOAD_DIR

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/")
async def upload_pdfs(
    files: list[UploadFile] = File(...)
):

    if len(files) == 0:

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

    # Remove previously uploaded PDFs
    for old_pdf in upload_path.glob("*.pdf"):

        try:
            old_pdf.unlink()
        except Exception:
            pass

    uploaded_files = []

    total_size = 0

    for file in files:

        if not file.filename.lower().endswith(".pdf"):

            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} is not a PDF file."
            )

        destination = upload_path / file.filename

        with open(destination, "wb") as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        uploaded_files.append(file.filename)

        total_size += destination.stat().st_size

    return {

        "status": "success",

        "message": "PDF files uploaded successfully.",

        "uploaded_files": uploaded_files,

        "total_files": len(uploaded_files),

        "total_size": total_size

    }