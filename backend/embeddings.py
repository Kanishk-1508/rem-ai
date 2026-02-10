from sentence_transformers import SentenceTransformer
from typing import List

# Load model once (IMPORTANT for performance)
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(chunks: List[str]) -> List[list]:
    """
    Converts text chunks into vector embeddings.
    """
    embeddings = model.encode(chunks, convert_to_numpy=True)
    return embeddings.tolist()
