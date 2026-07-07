import fitz
import easyocr
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from backend.config import OCR_DPI, MAX_WORKERS


class PDFReader:

    print("Loading EasyOCR Model...")

    reader = easyocr.Reader(
        ["en"],
        gpu=False
    )

    print("EasyOCR Ready.\n")

    @staticmethod
    def process_page(page_data):

        page_number, page = page_data

        text = page.get_text("text").strip()

        if text:

            print(
                f"✓ Page {page_number} : Text Extracted ({len(text)} chars)"
            )

            return page_number, text

        print(
            f"Page {page_number} : Running OCR..."
        )

        pix = page.get_pixmap(
            dpi=OCR_DPI
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
            f"✓ Page {page_number} : OCR ({len(ocr_text)} chars)"
        )

        return page_number, ocr_text

    @staticmethod
    def read_pdf(pdf_path):

        print(f"\nOpening PDF : {pdf_path}")

        document = fitz.open(pdf_path)

        total_pages = len(document)

        print(f"Total Pages : {total_pages}")

        pages = [

            (i + 1, document.load_page(i))

            for i in range(total_pages)

        ]

        with ThreadPoolExecutor(
            max_workers=MAX_WORKERS
        ) as executor:

            results = list(
                executor.map(
                    PDFReader.process_page,
                    pages
                )
            )

        document.close()

        results.sort(
            key=lambda x: x[0]
        )

        final_text = "\n\n".join(

            text

            for _, text in results

            if text.strip()

        )

        print(
            f"\nTotal Characters Extracted : {len(final_text)}"
        )

        return final_text.strip()