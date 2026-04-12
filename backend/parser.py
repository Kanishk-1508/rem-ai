from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)


def parse_text_file(file_path: str) -> str:
    """
    Parse text file with proper encoding handling.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Extracted text content
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        logger.info(f"Successfully parsed text file: {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"Error parsing text file: {e}")
        raise


def parse_pdf_file(file_path: str) -> str:
    """
    Parse PDF file and extract text from all pages.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        page_count = len(reader.pages)
        
        logger.info(f"Processing PDF with {page_count} pages")

        for page_num, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num}: {e}")
                continue

        if not text:
            logger.warning("No text could be extracted from PDF")
            return ""
        
        logger.info(f"Successfully parsed PDF: {len(text)} characters from {page_count} pages")
        return text

    except Exception as e:
        logger.error(f"Error parsing PDF file: {e}")
        raise
