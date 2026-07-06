import fitz
import easyocr
import numpy as np


class PDFReader:

    print("Loading EasyOCR Model...")

    reader = easyocr.Reader(
        ["en"],
        gpu=False
    )

    print("EasyOCR Ready.\n")

    @staticmethod
    def read_pdf(pdf_path):

        print(f"\nOpening PDF : {pdf_path}")

        document = fitz.open(pdf_path)

        extracted_text = []

        total_pages = len(document)

        print(f"Total Pages : {total_pages}")

        for page_number, page in enumerate(document, start=1):

            print(f"Reading Page {page_number}...")

            text = page.get_text("text")

            if text.strip():

                print(
                    f"✓ Text Extracted ({len(text)} characters)"
                )

                extracted_text.append(text)

                continue

            print("No selectable text found. Running OCR...")

            pix = page.get_pixmap(
                dpi=300
            )

            image = np.frombuffer(
                pix.samples,
                dtype=np.uint8
            ).reshape(
                pix.height,
                pix.width,
                pix.n
            )

            result = PDFReader.reader.readtext(
                image,
                detail=0,
                paragraph=True
            )

            ocr_text = "\n".join(result)

            print(
                f"✓ OCR Extracted ({len(ocr_text)} characters)"
            )

            extracted_text.append(ocr_text)

        document.close()

        final_text = "\n\n".join(extracted_text).strip()

        print(
            f"\nTotal Characters Extracted : {len(final_text)}"
        )

        return final_text