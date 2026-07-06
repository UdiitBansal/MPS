from pathlib import Path
import time

from backend.config import UPLOAD_DIR
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

    def build(self):

        start_time = time.time()

        self.all_chunks.clear()

        pdfs = sorted(Path(UPLOAD_DIR).glob("*.pdf"))

        if not pdfs:

            return {
                "status": "error",
                "message": "No PDF files found."
            }

        total_pages = 0

        for pdf in pdfs:

            print(f"\nReading : {pdf.name}")

            text = PDFReader.read_pdf(str(pdf))

            if not text:
                continue

            total_pages += text.count("\n") + 1

            chunks = Chunker.split(text)

            for chunk in chunks:

                chunk = chunk.strip()

                if chunk:

                    self.all_chunks.append(chunk)

        if len(self.all_chunks) == 0:

            return {
                "status": "error",
                "message": "No text extracted from uploaded PDFs."
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
            embeddings
        )

        print("Building BM25 Index...")

        self.bm25.build_index(
            self.all_chunks
        )

        end_time = time.time()

        processing_time = round(
            end_time - start_time,
            2
        )

        return {

            "status": "success",

            "message": "Documents processed successfully.",

            "documents": len(pdfs),

            "pages": total_pages,

            "chunks": len(self.all_chunks),

            "embedding_dimension": len(embeddings[0]),

            "processing_time": processing_time

        }


index = DocumentIndex()