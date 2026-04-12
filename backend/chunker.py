from typing import List
import logging

logger = logging.getLogger(__name__)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Splits text into overlapping chunks for embedding.
    
    Args:
        text: The text to split
        chunk_size: Size of each chunk in characters (default: 500)
        overlap: Overlap between chunks in characters (default: 100)
    
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        logger.warning("Attempting to chunk empty text")
        return []
    
    if chunk_size <= 0 or overlap < 0:
        raise ValueError("chunk_size must be positive and overlap must be non-negative")
    
    if overlap >= chunk_size:
        logger.warning("Overlap is >= chunk_size, reducing overlap")
        overlap = max(0, chunk_size - 1)

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()
        
        # Only add non-empty chunks
        if chunk:
            chunks.append(chunk)

        # Stop when we have consumed the final slice.
        if end >= text_length:
            break
        
        start = end - overlap

        if start < 0:
            start = 0
        
        # Prevent infinite loop
        if start >= text_length:
            break

    logger.info(f"Created {len(chunks)} chunks from text of {text_length} characters")
    return chunks
