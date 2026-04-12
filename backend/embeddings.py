from sentence_transformers import SentenceTransformer
from typing import List
import logging

logger = logging.getLogger(__name__)

# Load model once (IMPORTANT for performance)
try:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    logger.info("Embedding model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load embedding model: {e}")
    raise


def create_embeddings(chunks: List[str]) -> List[list]:
    """
    Converts text chunks into vector embeddings.
    
    Args:
        chunks: List of text chunks to embed
        
    Returns:
        List of embedding vectors (384-dimensional)
        
    Raises:
        ValueError: If chunks list is empty
        RuntimeError: If embedding fails
    """
    if not chunks:
        raise ValueError("Cannot create embeddings from empty chunk list")
    
    if len(chunks) > 1000:
        logger.warning(f"Large batch of {len(chunks)} chunks - this may take a while")
    
    try:
        embeddings = model.encode(chunks, convert_to_numpy=True)
        logger.info(f"Created {len(embeddings)} embeddings")
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Failed to create embeddings: {e}")
        raise RuntimeError(f"Embedding generation failed: {str(e)}")
