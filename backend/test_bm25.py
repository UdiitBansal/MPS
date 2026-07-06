from backend.services.bm25_store import BM25Store

chunks = [
    "Artificial Intelligence is transforming healthcare.",
    "Machine Learning is a subset of AI.",
    "Deep Learning uses neural networks.",
    "Python is used in Data Science.",
    "BM25 is a lexical search algorithm."
]

bm25 = BM25Store()

bm25.build_index(chunks)

results = bm25.search("AI")

for doc, score in results:
    print(score, "->", doc)