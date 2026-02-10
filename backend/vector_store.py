import faiss
import numpy as np
from typing import List


class VectorStore:
    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatL2(dimension)
        self.text_chunks: List[str] = []

    def add(self, embeddings: List[list], chunks: List[str]):
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.text_chunks.extend(chunks)

    def search(self, query_embedding: list, top_k: int = 3) -> List[str]:
        query_vector = np.array([query_embedding]).astype("float32")
        _, indices = self.index.search(query_vector, top_k)
        return [self.text_chunks[i] for i in indices[0]]
