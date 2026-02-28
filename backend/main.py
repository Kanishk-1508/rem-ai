from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import os
import shutil
import uuid
import time
from fastapi.middleware.cors import CORSMiddleware

from parser import parse_pdf_file, parse_text_file
from chunker import chunk_text
from embeddings import create_embeddings
from vector_store import VectorStore
from generator import generate_answer


# ------------------ APP INIT ------------------
app = FastAPI(title="rem.ai Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize FAISS vector store ONCE (global)
vector_store = VectorStore(dimension=384)
# ------------------------------------------------


# ------------------ MODELS ------------------
class ChatRequest(BaseModel):
    question: str
# ------------------------------------------------


# ------------------ ROUTES ------------------
@app.get("/")
def root():
    return {"message": "rem.ai backend is running"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    # Validate file type
    if file.content_type not in ["application/pdf", "text/plain"]:
        raise HTTPException(status_code=400, detail="Only PDF or text files allowed")

    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse document
    if file.content_type == "application/pdf":
        extracted_text = parse_pdf_file(file_path)
    else:
        extracted_text = parse_text_file(file_path)

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="No readable text found in document")

    # Generate upload session ID
    upload_id = str(uuid.uuid4())
    timestamp = time.time()

    # Chunk text
    chunks = chunk_text(extracted_text)

    # Create embeddings
    embeddings = create_embeddings(chunks)

    # Build metadata list (v2.0 structure)
    metadata_list = []

    for i, chunk in enumerate(chunks):
        metadata = {
            "chunk_id": str(uuid.uuid4()),
            "text": chunk,
            "source_file": file.filename,
            "page_number": None,  # Can upgrade later for PDF page tracking
            "chunk_index": i,
            "upload_id": upload_id,
            "timestamp": timestamp
        }
        metadata_list.append(metadata)

    # Store in FAISS (v2.0)
    vector_store.add(embeddings, metadata_list)

    return {
        "filename": file.filename,
        "upload_id": upload_id,
        "total_chunks": len(chunks),
        "message": "Document uploaded and indexed successfully"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    # Embed query
    query_embedding = create_embeddings([question])[0]

    # Retrieve relevant metadata objects
    retrieved_results = vector_store.search(query_embedding, top_k=3)

    if not retrieved_results:
        return {
            "question": question,
            "answer": "No relevant information found in uploaded documents.",
            "sources": []
        }

    # Build context from retrieved chunks
    context_chunks = [result["text"] for result in retrieved_results]

    # Generate grounded answer
    answer = generate_answer(question, context_chunks)

    # Build source attribution
    sources = [
        {
            "source_file": result["source_file"],
            "chunk_index": result["chunk_index"],
            "score": result["score"]
        }
        for result in retrieved_results
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }
# ------------------------------------------------