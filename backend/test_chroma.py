from backend.services.embeddings import EmbeddingModel
from backend.services.chroma_store import ChromaStore

chunks = [
    "Artificial Intelligence is transforming healthcare.",
    "Machine Learning is a subset of AI.",
    "Deep Learning uses neural networks.",
    "Python is used in Data Science.",
    "BM25 is a lexical search algorithm."
]

embedder = EmbeddingModel()

vectors = embedder.encode(chunks)

db = ChromaStore()

db.add_documents(chunks, vectors)

query = "Explain AI"

query_vector = embedder.encode([query])[0]

result = db.search(query_vector)

print(result)