# rem.ai - AI-Powered Document Chatbot

**A full-stack RAG (Retrieval-Augmented Generation) chatbot that lets you upload documents and ask questions about their content.**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Status](https://img.shields.io/badge/status-active-green)

---

## 🎯 Overview

rem.ai is a modern full-stack application that uses AI and semantic search to help you interact with your documents. Upload a PDF or text file, and ask context-aware questions. The system retrieves relevant content and generates accurate answers grounded in your documents.

### Key Features

- 📄 **Multi-format Support**: Upload PDF and text files
- 🔍 **Semantic Search**: Uses AI embeddings to find relevant document sections  
- 🧠 **AI-Powered Responses**: Generates accurate answers using Ollama with model fallback
- 💾 **Persistent Storage**: Vector embeddings stored in FAISS for fast retrieval
- 🎨 **Modern UI**: Beautiful, responsive React interface with real-time feedback
- 🎛️ **Theme Switcher**: Aqua Orange, Forest Cream, Midnight Copper
- 📊 **Source Attribution**: See exactly which document sections informed each answer
- 🧠 **Session Memory**: Follow-up questions retain conversational context
- 🧹 **Clear Chat**: Resets local chat and backend session memory
- ⚡ **Fast Processing**: Efficient chunking and embedding pipeline

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **FAISS** - Facebook AI Similarity Search (vector database)
- **Sentence Transformers** - State-of-the-art text embeddings (384-dimensional vectors)
- **Ollama** - Local LLM inference engine (LLaMA 3)
- **PyPDF** - PDF text extraction
- **Pydantic** - Data validation and serialization

### Frontend
- **React 19** - Modern UI framework
- **Vite** - Lightning-fast build tool and dev server
- **React Markdown** - Render formatted responses
- **CSS3** - Modern styling with gradients and animations

---

## 📋 Prerequisites

### Required
- **Python 3.9+**
- **Node.js 18+** (LTS recommended)
- **Ollama** - Download from [ollama.ai](https://ollama.ai)

### Verify Installation
```bash
python --version        # Should be 3.9 or higher
node --version          # Should be 18 or higher
ollama --version        # Should be installed
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

**Check health**: Visit `http://localhost:8000/health` in your browser

### 2. Ollama Setup (Required for AI responses)

```bash
# Download and start Ollama
ollama pull llama3.2:3b
ollama serve
```

Ollama will run on `http://localhost:11434`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173` (or `http://localhost:5174` if auto-switched)

### 4. Open the Application

Open your browser and navigate to: **`http://localhost:5173`**

---

## 📖 How It Works

### The RAG Pipeline

1. **Upload Document**
   - User selects a PDF or text file
   - File is uploaded to backend and saved

2. **Text Extraction**
   - Content is extracted from the document
   - Encoding is handled automatically

3. **Chunking**
   - Text is split into overlapping chunks (500 characters with 100-char overlap)
   - Chunks are sized for optimal embedding quality

4. **Embedding**
   - Each chunk is converted to a 384-dimensional vector using Sentence Transformers
   - Embeddings capture semantic meaning

5. **Storage**
   - Vectors are stored in FAISS index for fast similarity search
   - Metadata (source file, chunk index) is preserved

6. **Question Processing**
   - User question is embedded using the same model
   - Top 6 most similar chunks are retrieved
   - Duplicate chunks are removed
   - Best chunks become the context for the LLM

7. **Response Generation**
   - Context, question, and recent conversation turns are passed to Ollama
   - LLM generates an answer grounded in the context
   - Answer, sources, and session ID are returned to user

---

## 🎮 Usage Guide

### Uploading Documents

1. Click the drop zone or select "Choose File"
2. Select a **PDF** or **TXT** file (up to 100MB)
3. Click "Upload"
4. Wait for success confirmation
5. View uploaded files in the list below

### Asking Questions

1. Ensure at least one document is uploaded
2. Type your question in the chat input field
3. Press **Enter** or click **Send**
4. Wait for AI to process and respond
5. View sources cited for the answer

### Tips for Best Results

- Ask **specific questions** about document content
- Use **quotations** for exact phrase searches
- Ask for **summaries** of key topics
- Request **comparisons** between sections
- Ask **follow-up questions** for clarification

---

## 📁 Project Structure

```
Rem_ai/
├── backend/
│   ├── main.py              # FastAPI application and routes
│   ├── parser.py            # PDF and text file parsing
│   ├── chunker.py           # Text chunking logic
│   ├── embeddings.py        # Sentence Transformer embeddings
│   ├── vector_store.py      # FAISS vector database management
│   ├── generator.py         # LLM response generation
│   ├── requirements.txt     # Python dependencies
│   ├── venv/                # Python virtual environment
│   ├── uploads/             # Uploaded documents
│   ├── faiss_index.bin      # FAISS vector index (auto-created)
│   └── faiss_metadata.pkl   # Vector metadata (auto-created)
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx         # React entry point
│   │   ├── App.jsx          # Main app component
│   │   ├── Chat.jsx         # Chat interface component
│   │   ├── FileUpload.jsx   # File upload component
│   │   ├── App.css          # App styling
│   │   ├── Chat.css         # Chat styling
│   │   ├── FileUpload.css   # Upload styling
│   │   └── index.css        # Global styles
│   ├── package.json         # Node dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── index.html           # HTML entry point
│   └── node_modules/        # Node dependencies
│
└── readme.md                # This file
```

---

## 🔧 API Documentation

### Health Check
```http
GET /health
```
Returns vector store status and system health.

### Upload Document
```http
POST /upload
Content-Type: multipart/form-data

file: <binary PDF or TXT file>
```

**Response** (200 OK):
```json
{
  "status": "success",
  "filename": "document.pdf",
  "upload_id": "uuid",
  "total_chunks": 45,
  "message": "Document uploaded and indexed successfully"
}
```

### Chat / Ask Question
```http
POST /chat
Content-Type: application/json

{
   "question": "What is the main topic of this document?",
   "session_id": "optional-session-id",
   "history": [
      {"role": "user", "text": "Summarize this"},
      {"role": "assistant", "text": "..."}
   ]
}
```

**Response** (200 OK):
```json
{
  "status": "success",
   "session_id": "uuid",
  "question": "What is the main topic?",
  "answer": "The document primarily focuses on...",
  "sources": [
    {
      "source_file": "document.pdf",
      "chunk_index": 5,
      "score": 0.234
    }
  ]
}
```

### Clear Session Memory
```http
DELETE /chat/session/{session_id}
```

**Response** (200 OK):
```json
{
   "status": "success",
   "session_id": "uuid",
   "cleared": true
}
```

---

## ⚙️ Configuration

### Backend Configuration (main.py)

```python
# CORS Origins (add your origins here)
allow_origins=["http://localhost:5173", "http://localhost:3000"]

# Upload Directory
UPLOAD_DIR = "uploads"

# Vector Store Dimension
dimension=384  # Must match Sentence Transformers output
```

### Text Chunking (chunker.py)

```python
chunk_size=500      # Characters per chunk
overlap=100         # Overlap between chunks
```

### Vector Search (vector_store.py)

```python
top_k=6  # Number of initial chunks to retrieve before dedup/filtering
```

---

## 🐛 Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Install dependencies
cd backend
pip install -r requirements.txt
```

**Error**: `[Errno 2] No such file or directory: 'uploads'`
```bash
# Solution: Create uploads directory
mkdir uploads
```

### Ollama Connection Error

**Error**: `Failed to connect to Ollama at http://localhost:11434`
```bash
# Solution: Start Ollama server
ollama serve

# In another terminal, download the model
ollama pull llama2
```

### FileUpload Not Working

**Error**: `429: Too many requests` or `timeout`
```bash
# Solution: 
# 1. Check file size (max 100MB)
# 2. Ensure backend is running
# 3. Check network connection
```

### Slow Response Times

**Causes & Solutions**:
- Large documents → Split into smaller documents
- First query → Model is loading embeddings (normal)
- Many uploaded documents → Search is faster with fewer documents
- Ollama inference → Local LLM is slower than cloud APIs

---

## 📊 Performance Tips

1. **Optimize Documents**
   - Use clear, well-structured documents
   - Remove images and formatting if possible
   - Split very large documents

2. **Optimize Queries**
   - Use specific, detailed questions
   - Provide context when asking follow-ups
   - Rephrase if you don't get good results

3. **Backend Optimization**
   - Use GPU if available for embeddings
   - Adjust chunk_size for your use case
   - Monitor /health endpoint

---

## 🔐 Security Considerations

- Uploaded files are stored locally
- No files are sent to external services
- All processing happens on your machine
- Ollama runs locally (no external API calls)

**Note**: For production, implement:
- File size limits (already at 100MB)
- Input validation (partially implemented)
- Rate limiting
- Authentication
- HTTPS/SSL

---

## 🚀 Future Enhancements

- [ ] Support for more file formats (.docx, .ppt, images)
- [ ] Multi-language support
- [ ] Document management UI (delete, organize)
- [ ] Conversation history
- [ ] User accounts and authentication  
- [ ] Batch processing
- [ ] Custom model selection
- [ ] GPU acceleration settings
- [ ] Advanced search filters
- [ ] Export chat as PDF

---

## 📝 License

This project is open-source and available under the MIT License.

---

## 💬 Support & Contribution

For issues, questions, or contributions:

1. **Report Issues**: Create a detailed bug report
2. **Suggest Features**: Share your ideas
3. **Contribute Code**: Fork and submit pull requests

---

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net)

---

**Built with ❤️ for document intelligence**

Last Updated: April 2026
