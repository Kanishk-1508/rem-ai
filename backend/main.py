from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
import os
import shutil
import uuid
import time
import logging
from threading import Lock
from fastapi.middleware.cors import CORSMiddleware

from parser import parse_pdf_file, parse_text_file
from chunker import chunk_text
from embeddings import create_embeddings
from vector_store import VectorStore
from generator import generate_answer


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ------------------ APP INIT ------------------
app = FastAPI(title="rem.ai Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize FAISS vector store ONCE (global)
try:
    vector_store = VectorStore(dimension=384)
    logger.info("Vector store initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize vector store: {e}")
    raise

# ------------------------------------------------


# ------------------ MODELS ------------------
class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None
    history: list[dict] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the main topic of this document?",
                "session_id": "b14d98f7-8ea9-40e0-8f98-c2f4f2f85739",
                "history": [
                    {"role": "user", "text": "Summarize the first section"},
                    {"role": "assistant", "text": "The first section discusses..."}
                ]
            }
        }

# ------------------------------------------------

# ------------------ SESSION MEMORY ------------------
SESSION_HISTORY: dict[str, list[dict]] = {}
SESSION_LOCK = Lock()
MAX_SESSION_TURNS = 16
# ------------------------------------------------


# ------------------ ROUTES ------------------
@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "rem.ai backend is running",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "vector_store_size": vector_store.index.ntotal,
        "timestamp": time.time()
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    
    try:
        # Validate file type
        if file.content_type not in ["application/pdf", "text/plain"]:
            logger.warning(f"Invalid file type: {file.content_type}")
            raise HTTPException(
                status_code=400,
                detail="Only PDF or text files allowed. Supported types: application/pdf, text/plain"
            )

        # Validate file size (100MB limit)
        file_size = 0
        chunk_size_bytes = 1024 * 1024
        file_chunks = []

        while True:
            data = await file.read(chunk_size_bytes)
            if not data:
                break
            file_chunks.append(data)
            file_size += len(data)
            if file_size > 100 * 1024 * 1024:
                logger.warning(f"File too large: {file_size} bytes")
                raise HTTPException(
                    status_code=413,
                    detail="File too large. Maximum size: 100MB"
                )

        # Save file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        try:
            with open(file_path, "wb") as buffer:
                for chunk in file_chunks:
                    buffer.write(chunk)
            logger.info(f"File saved: {file.filename} ({file_size} bytes)")
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise HTTPException(status_code=500, detail="Failed to save file")

        # Parse document
        try:
            if file.content_type == "application/pdf":
                extracted_text = parse_pdf_file(file_path)
            else:
                extracted_text = parse_text_file(file_path)
        except Exception as e:
            logger.error(f"Failed to parse document: {e}")
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse document: {str(e)}"
            )

        if not extracted_text.strip():
            logger.warning("No readable text found in document")
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail="No readable text found in document"
            )

        # Generate upload session ID
        upload_id = str(uuid.uuid4())
        timestamp = time.time()

        # Chunk text
        try:
            chunks = chunk_text(extracted_text)
            logger.info(f"Document chunked into {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Failed to chunk text: {e}")
            raise HTTPException(status_code=500, detail="Failed to process document")

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Document resulted in no chunks after processing"
            )

        # Create embeddings
        try:
            embeddings = create_embeddings(chunks)
            logger.info(f"Created {len(embeddings)} embeddings")
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            raise HTTPException(status_code=500, detail="Failed to create embeddings")

        # Build metadata list
        metadata_list = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "chunk_id": str(uuid.uuid4()),
                "text": chunk,
                "source_file": file.filename,
                "page_number": None,
                "chunk_index": i,
                "upload_id": upload_id,
                "timestamp": timestamp
            }
            metadata_list.append(metadata)

        # Store in FAISS
        try:
            vector_store.add(embeddings, metadata_list)
            logger.info(f"Successfully indexed document: {file.filename}")
        except Exception as e:
            logger.error(f"Failed to store in vector database: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to index document in database"
            )

        return {
            "status": "success",
            "filename": file.filename,
            "upload_id": upload_id,
            "total_chunks": len(chunks),
            "message": "Document uploaded and indexed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during upload: {e}")
        raise HTTPException(status_code=500, detail="Unexpected server error")


@app.post("/chat")
def chat(request: ChatRequest):
    """Chat with the AI about uploaded documents"""
    
    try:
        question = request.question.strip()

        if not question:
            raise HTTPException(
                status_code=400,
                detail="Question cannot be empty"
            )

        if len(question) > 1000:
            raise HTTPException(
                status_code=400,
                detail="Question too long. Maximum 1000 characters"
            )

        logger.info(f"Processing question: {question[:50]}...")

        session_id = (request.session_id or "").strip()
        if not session_id:
            session_id = str(uuid.uuid4())

        # Keep recent conversation turns for better follow-up answers.
        cleaned_history = []
        for item in request.history[-8:]:
            if not isinstance(item, dict):
                continue

            role = str(item.get("role", "")).strip().lower()
            text = str(item.get("text", "")).strip()

            if role in {"ai", "assistant"}:
                role = "assistant"
            elif role == "user":
                role = "user"
            else:
                continue

            if not text:
                continue

            cleaned_history.append({"role": role, "text": text})

        with SESSION_LOCK:
            stored_history = SESSION_HISTORY.get(session_id, []).copy()

        merged_history = (stored_history + cleaned_history)[-MAX_SESSION_TURNS:]

        # Embed query
        try:
            query_embedding = create_embeddings([question])[0]
        except Exception as e:
            logger.error(f"Failed to embed query: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to process question"
            )

        # Retrieve relevant metadata objects
        try:
            retrieved_results = vector_store.search(query_embedding, top_k=6)
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error searching documents"
            )

        if not retrieved_results:
            logger.info("No relevant results found")
            return {
                "status": "success",
                "question": question,
                "answer": "I couldn't find relevant information in the uploaded documents. Please upload documents and try a different question.",
                "sources": []
            }

        # Build context from retrieved chunks (de-duplicate repeated chunks)
        context_chunks = []
        seen_texts = set()
        for result in retrieved_results:
            text = result["text"].strip()
            if not text:
                continue
            if text in seen_texts:
                continue
            seen_texts.add(text)
            context_chunks.append(text)

        # Keep top relevant chunks only
        context_chunks = context_chunks[:4]

        # Generate grounded answer
        try:
            answer = generate_answer(question, context_chunks, merged_history)
            logger.info("Answer generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate answer"
            )

        # Build source attribution
        sources = [
            {
                "source_file": result["source_file"],
                "chunk_index": result["chunk_index"],
                "score": result["score"]
            }
            for result in retrieved_results
        ]

        updated_history = (
            merged_history
            + [{"role": "user", "text": question}, {"role": "assistant", "text": answer}]
        )[-MAX_SESSION_TURNS:]

        with SESSION_LOCK:
            SESSION_HISTORY[session_id] = updated_history

        return {
            "status": "success",
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "sources": sources
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during chat: {e}")
        raise HTTPException(status_code=500, detail="Unexpected server error")


@app.delete("/chat/session/{session_id}")
def clear_session_memory(session_id: str):
    """Clear conversation memory for a given session ID."""
    cleaned_session_id = session_id.strip()

    if not cleaned_session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    with SESSION_LOCK:
        removed = SESSION_HISTORY.pop(cleaned_session_id, None)

    return {
        "status": "success",
        "session_id": cleaned_session_id,
        "cleared": removed is not None,
    }

# ------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """Log startup"""
    logger.info("rem.ai Backend started")

@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown"""
    logger.info("rem.ai Backend shutdown")