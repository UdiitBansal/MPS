from backend.services.embeddings import EmbeddingModel

chunks = [
    "Artificial Intelligence is transforming healthcare.",
    "Machine Learning is a subset of AI.",
    "Deep Learning uses neural networks."
]

model = EmbeddingModel()

vectors = model.encode(chunks)

print("Number of vectors :", len(vectors))
print("Dimension :", len(vectors[0]))