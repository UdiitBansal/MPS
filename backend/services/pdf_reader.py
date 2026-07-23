import logging
from concurrent.futures import ThreadPoolExecutor

import easyocr
import fitz
import numpy as np

from backend.config import OCR_DPI, MAX_WORKERS

logger = logging.getLogger(__name__)


class PDFReader:

    logger.info("Loading EasyOCR Model...")

    try:

        reader = easyocr.Reader(
            ["en"],
            gpu=False
        )

        logger.info("EasyOCR Ready.")

    except Exception as e:

        logger.exception("Failed to initialize EasyOCR")

        raise RuntimeError(
            f"Failed to initialize EasyOCR: {e}"
        )

    @staticmethod
    def process_page(page_data):

        page_number, page = page_data

        try:

            text = page.get_text("text").strip()

            # -----------------------------
            # Normal PDF Text
            # -----------------------------

            if text:

                logger.info(
                    f"Page {page_number}: Text Extracted ({len(text)} chars)"
                )

                return {
                    "page": page_number,
                    "text": text
                }

            # -----------------------------
            # OCR
            # -----------------------------

            logger.info(
                f"Page {page_number}: Running OCR..."
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

            if image.size == 0:

                return {
                    "page": page_number,
                    "text": ""
                }

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

            logger.info(
                f"Page {page_number}: OCR ({len(ocr_text)} chars)"
            )

            return {
                "page": page_number,
                "text": ocr_text
            }

        except Exception:

            logger.exception(
                f"Failed to process page {page_number}"
            )

            return {
                "page": page_number,
                "text": ""
            }

    @staticmethod
    def read_pdf(pdf_path):

        logger.info(f"Opening PDF: {pdf_path}")

        try:

            with fitz.open(pdf_path) as document:

                total_pages = len(document)

                logger.info(f"Total Pages: {total_pages}")

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

        except Exception:

            logger.exception(
                f"Error opening PDF: {pdf_path}"
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

        logger.info(
            f"Total Characters Extracted: {total_chars}"
        )

        return {

            "text": final_text,

            "pages": page_data,

            "total_pages": total_pages

        }