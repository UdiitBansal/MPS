from backend.indexes.document_index import index
from backend.services.retriever import Retriever

# Build indexes first
print(index.build())

retriever = Retriever()

question = "What is Artificial Intelligence?"

results = retriever.search(question)

for i, chunk in enumerate(results, start=1):
    print(f"\nChunk {i}\n")
    print(chunk)