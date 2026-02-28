import faiss
import numpy as np
import os
import pickle
from typing import List


INDEX_FILE = "faiss_index.bin"
METADATA_FILE = "faiss_metadata.pkl"


class VectorStore:
    def __init__(self, dimension: int):
        self.dimension = dimension

        # If index exists, load it
        if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
            print("Loading existing FAISS index...")
            self.index = faiss.read_index(INDEX_FILE)

            with open(METADATA_FILE, "rb") as f:
                self.text_chunks = pickle.load(f)
        else:
            print("Creating new FAISS index...")
            self.index = faiss.IndexFlatL2(dimension)
            self.text_chunks: List[str] = []

    def add(self, embeddings: List[list], chunks: List[str]):
        vectors = np.array(embeddings).astype("float32")
        self.index.add(vectors)
        self.text_chunks.extend(chunks)

        # Save after adding
        self._save()

    def search(self, query_embedding: list, top_k: int = 3) -> List[str]:
        if self.index.ntotal == 0:
            return []

        query_vector = np.array([query_embedding]).astype("float32")
        _, indices = self.index.search(query_vector, top_k)

        return [
            self.text_chunks[i]
            for i in indices[0]
            if i < len(self.text_chunks)
        ]

    def _save(self):
        # Save FAISS index
        faiss.write_index(self.index, INDEX_FILE)

        # Save metadata (text chunks)
        with open(METADATA_FILE, "wb") as f:
            pickle.dump(self.text_chunks, f)