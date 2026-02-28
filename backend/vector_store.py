import faiss
import numpy as np
import os
import pickle
from typing import List, Dict, Any


INDEX_FILE = "faiss_index.bin"
METADATA_FILE = "faiss_metadata.pkl"


class VectorStore:
    def __init__(self, dimension: int):
        self.dimension = dimension

        if os.path.exists(INDEX_FILE) and os.path.exists(METADATA_FILE):
            print("Loading existing FAISS index...")
            self.index = faiss.read_index(INDEX_FILE)

            with open(METADATA_FILE, "rb") as f:
                self.metadata: List[Dict[str, Any]] = pickle.load(f)
        else:
            print("Creating new FAISS index...")
            self.index = faiss.IndexFlatL2(dimension)
            self.metadata: List[Dict[str, Any]] = []

    def add(self, embeddings: List[list], metadata_list: List[Dict[str, Any]]):
        vectors = np.array(embeddings).astype("float32")

        if len(vectors) != len(metadata_list):
            raise ValueError("Embeddings and metadata length mismatch")

        self.index.add(vectors)
        self.metadata.extend(metadata_list)

        self._save()

    def search(self, query_embedding: list, top_k: int = 3) -> List[Dict[str, Any]]:
        if self.index.ntotal == 0:
            return []

        query_vector = np.array([query_embedding]).astype("float32")

        distances, indices = self.index.search(query_vector, top_k)

        results = []

        for score, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                chunk_data = self.metadata[idx].copy()
                chunk_data["score"] = float(score)
                results.append(chunk_data)

        return results

    def _save(self):
        faiss.write_index(self.index, INDEX_FILE)

        with open(METADATA_FILE, "wb") as f:
            pickle.dump(self.metadata, f)