from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time
import fitz

from backend.config import (
    UPLOAD_DIR,
    MAX_WORKERS
)

from backend.services.pdf_reader import PDFReader
from backend.services.chunker import Chunker
from backend.services.embeddings import EmbeddingModel
from backend.services.chroma_store import ChromaStore
from backend.services.bm25_store import BM25Store


class DocumentIndex:

    def __init__(self):

        self.embedder = EmbeddingModel()

        self.chroma = ChromaStore()

        self.bm25 = BM25Store()

        self.all_chunks = []

        self.metadata = []

    def process_pdf(self, pdf):

        print(f"\nReading : {pdf.name}")

        text = PDFReader.read_pdf(str(pdf))

        if not text:

            return [], [], 0

        # Get actual page count
        with fitz.open(str(pdf)) as doc:

            actual_pages = len(doc)

        chunks = Chunker.split(text)

        pdf_chunks = []

        pdf_metadata = []

        for i, chunk in enumerate(chunks, start=1):

            chunk = chunk.strip()

            if not chunk:
                continue

            pdf_chunks.append(chunk)

            pdf_metadata.append(

                {

                    "source": pdf.name,

                    "page": "-",

                    "chunk": i

                }

            )

        return (

            pdf_chunks,

            pdf_metadata,

            actual_pages

        )

    def build(self):

        start_time = time.time()

        self.all_chunks.clear()

        self.metadata.clear()

        pdf_files = sorted(

            Path(UPLOAD_DIR).glob("*.pdf")

        )

        if len(pdf_files) == 0:

            return {

                "status": "error",

                "message": "No PDF files found."

            }

        total_pages = 0

        print("\nProcessing PDFs in Parallel...\n")

        with ThreadPoolExecutor(

            max_workers=MAX_WORKERS

        ) as executor:

            results = list(

                executor.map(

                    self.process_pdf,

                    pdf_files

                )

            )

        for chunks, metadata, pages in results:

            self.all_chunks.extend(chunks)

            self.metadata.extend(metadata)

            total_pages += pages

        if len(self.all_chunks) == 0:

            return {

                "status": "error",

                "message": "No text extracted."

            }

        print("\nGenerating Embeddings...")

        embeddings = self.embedder.encode(

            self.all_chunks

        )

        print("Resetting ChromaDB...")

        self.chroma.reset_collection()

        print("Saving Embeddings...")

        self.chroma.add_documents(

            self.all_chunks,

            embeddings,

            self.metadata

        )

        print("Building BM25...")

        self.bm25.build_index(

            self.all_chunks,

            self.metadata

        )

        processing_time = round(

            time.time() - start_time,

            2

        )

        return {

            "status": "success",

            "message": "Documents processed successfully.",

            "documents": len(pdf_files),

            "pages": total_pages,

            "chunks": len(self.all_chunks),

            "embedding_dimension": self.embedder.dimension(),

            "processing_time": processing_time

        }


index = DocumentIndex()