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

        try:

            text = page.get_text("text").strip()

            # -----------------------------
            # Normal PDF Text
            # -----------------------------

            if text:

                print(
                    f"✓ Page {page_number} : Text Extracted ({len(text)} chars)"
                )

                return {

                    "page": page_number,

                    "text": text

                }

            # -----------------------------
            # OCR
            # -----------------------------

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

            # Convert grayscale to RGB

            if pix.n == 1:

                image = np.stack(
                    [image] * 3,
                    axis=-1
                )

            # Remove alpha channel

            elif pix.n == 4:

                image = image[:, :, :3]

            result = PDFReader.reader.readtext(

                image,

                detail=0,

                paragraph=True

            )

            ocr_text = "\n".join(result).strip()

            print(
                f"✓ Page {page_number} : OCR ({len(ocr_text)} chars)"
            )

            return {

                "page": page_number,

                "text": ocr_text

            }

        except Exception as e:

            print(

                f"✗ Page {page_number} : {e}"

            )

            return {

                "page": page_number,

                "text": ""

            }

    @staticmethod
    def read_pdf(pdf_path):

        print(f"\nOpening PDF : {pdf_path}")

        try:

            with fitz.open(pdf_path) as document:

                total_pages = len(document)

                print(f"Total Pages : {total_pages}")

                pages = [

                    (

                        i + 1,

                        document.load_page(i)

                    )

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

        except Exception as e:

            print(

                f"Error opening PDF : {e}"

            )

            return {

                "text": "",

                "pages": [],

                "total_pages": 0

            }

        # ---------------------------------
        # Sort by Page Number
        # ---------------------------------

        results.sort(

            key=lambda x: x["page"]

        )

        page_data = []

        all_text = []

        total_chars = 0

        for item in results:

            page_text = item["text"].strip()

            if not page_text:

                continue

            page_data.append({

                "page": item["page"],

                "text": page_text

            })

            all_text.append(page_text)

            total_chars += len(page_text)

        final_text = "\n\n".join(all_text)

        print(

            f"\nTotal Characters Extracted : {total_chars}"

        )

        return {

            "text": final_text,

            "pages": page_data,

            "total_pages": total_pages

        }