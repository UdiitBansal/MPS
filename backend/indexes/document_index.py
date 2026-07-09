from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time

from backend.config import (
    UPLOAD_DIR,
    MAX_WORKERS,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    EMBEDDING_MODEL,
    OLLAMA_MODEL
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

    # =====================================================
    # Process Single PDF
    # =====================================================

    def process_pdf(self, pdf):

        print(f"\nReading : {pdf.name}")

        result = PDFReader.read_pdf(str(pdf))

        page_data = result.get("pages", [])

        total_pages = result.get("total_pages", 0)

        if not page_data:

            return [], [], total_pages

        pdf_chunks = []

        pdf_metadata = []

        chunk_number = 1

        seen = set()

        for page in page_data:

            page_number = page["page"]

            page_text = page["text"].strip()

            if not page_text:

                continue

            chunks = Chunker.split(page_text)

            for chunk in chunks:

                chunk = chunk.strip()

                if not chunk:

                    continue

                key = chunk.lower()

                if key in seen:

                    continue

                seen.add(key)

                pdf_chunks.append(chunk)

                pdf_metadata.append(

                    {

                        "source": pdf.name,

                        "page": page_number,

                        "chunk": chunk_number

                    }

                )

                chunk_number += 1

        print(

            f"{pdf.name} -> {len(pdf_chunks)} chunks"

        )

        return (

            pdf_chunks,

            pdf_metadata,

            total_pages

        )

    # =====================================================
    # Build Index
    # =====================================================

    def build(self):

        start_time = time.time()

        self.all_chunks.clear()

        self.metadata.clear()

        pdf_files = sorted(

            Path(UPLOAD_DIR).glob("*.pdf")

        )

        if not pdf_files:

            return {

                "status": "error",

                "message": "No PDF files found."

            }

        total_pages = 0

        print("\n===================================")
        print("Processing PDFs")
        print("===================================\n")

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

        if not self.all_chunks:

            return {

                "status": "error",

                "message": "No text extracted."

            }

        print(f"\nTotal Chunks : {len(self.all_chunks)}")

        # =====================================================
        # Embeddings
        # =====================================================

        print("\nGenerating Embeddings...")

        embeddings = self.embedder.encode(

            self.all_chunks

        )

        if len(embeddings) == 0:

            return {

                "status": "error",

                "message": "Embedding generation failed."

            }

        # =====================================================
        # Chroma
        # =====================================================

        print("Resetting ChromaDB...")

        self.chroma.reset_collection()

        print("Saving Embeddings...")

        self.chroma.add_documents(

            self.all_chunks,

            embeddings,

            self.metadata

        )

        # =====================================================
        # BM25
        # =====================================================

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

            "processing_time": processing_time,

            "model": OLLAMA_MODEL,

            "embedding_model": EMBEDDING_MODEL,

            "chunk_size": CHUNK_SIZE,

            "chunk_overlap": CHUNK_OVERLAP,

            "index_type": "Hybrid Retrieval",

            "vector_database": "ChromaDB",

            "keyword_search": "BM25",

            "ready_for_chat": True

        }


index = DocumentIndex()