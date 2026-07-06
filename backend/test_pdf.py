from pathlib import Path

from backend.config import UPLOAD_DIR
from backend.services.pdf_reader import PDFReader

pdfs = list(Path(UPLOAD_DIR).glob("*.pdf"))

if not pdfs:
    print("No PDF found.")
    exit()

print("Reading:", pdfs[0].name)

text = PDFReader.read_pdf(str(pdfs[0]))

print("\nLength:", len(text))
print("\nFirst 1000 characters:\n")
print(text[:1000])