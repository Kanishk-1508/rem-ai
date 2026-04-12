# rem.ai — Retrieval-Augmented AI Chatbot

**A modern full-stack AI chatbot that allows users to upload documents (PDF/TXT) and ask context-aware questions using semantic search and local LLMs.**

---

## 🚀 Features

- 📄 **Multi-format Upload** - Support for PDF and text documents
- ✂️ **Automatic Text Parsing** - Intelligent text extraction and preprocessing
- 🧠 **Semantic Search** - AI-powered vector embeddings for finding relevant content
- 📦 **FAISS Vector Database** - Lightning-fast similarity search
- 🤖 **Local LLM** - LLaMA 2/3 via Ollama (no cloud dependency)
- 💬 **Beautiful Chat UI** - Modern React interface with markdown support
- 🎨 **Theme Switcher** - Three handcrafted visual themes with persistent selection
- 📊 **Source Attribution** - See exactly which documents informed each response
- 🧠 **Conversation Memory** - Follow-up answers keep session context across refreshes
- 🧹 **Clear Chat** - One-click reset for UI, browser storage, and backend session memory
- ⚡ **Fast & Responsive** - Real-time feedback and smooth animations
- 🔒 **Private** - All processing happens locally on your machine

---

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **FAISS** - Facebook's vector similarity search library
- **Sentence Transformers** - State-of-the-art text embeddings (384-dim)
- **Ollama** - Local LLM inference (LLaMA 2/3)
- **PyPDF** - PDF text extraction
- **Pydantic** - Data validation

### Frontend
- **React 19** - Latest React with modern features
- **Vite** - Ultra-fast build tool
- **React Markdown** - Format AI responses with markdown
- **CSS3** - Modern styling with gradients and animation

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js (LTS)
- Ollama (download from [ollama.ai](https://ollama.ai))

### Quick Start

#### 1. Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 2. Ollama (in another terminal)
```bash
ollama pull llama3.2:3b
ollama serve
```

#### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```

#### 4. Open Application
Navigate to `http://localhost:5173` (or `http://localhost:5174` if Vite auto-switches port)

**For detailed setup guide, see [SETUP_GUIDE.md](./SETUP_GUIDE.md)**

---

## 🔄 How It Works (RAG Pipeline)

1. **Document Upload** → Text is extracted from PDF/TXT
2. **Text Chunking** → Content split into 500-char overlapping chunks
3. **Embedding** → Each chunk converted to 384-dim vector
4. **Storage** → Vectors indexed in FAISS for fast retrieval
5. **Question Processing** → User query embedded and matched with documents
6. **Context Retrieval** → Top 6 matches retrieved, deduplicated, and trimmed to strongest chunks
7. **Response Generation** → LLaMA 3 generates grounded answer
8. **Conversation Continuity** → Recent turns and session memory are included for follow-ups
9. **Source Attribution** → Original document sections shown

---

## 📸 Screenshots

### Upload Interface
- Drag-and-drop zone for easy file upload
- Progress indicators and success feedback
- List of uploaded files with chunk counts

### Chat Interface  
- Clean, modern chat bubbles
- Real-time typing indicators
- Markdown-formatted responses
- Source attribution below each answer
- Enter key support for quick sending
- Session memory across refreshes
- Clear Chat button to start a fresh conversation
- Theme switcher with 3 persistent palettes

---

## 🎮 Usage

1. **Upload** a document (PDF or TXT, up to 100MB)
2. **Type** your question in the chat box
3. **Press Enter** or click Send
4. **View** the AI response with source citations
5. **Ask follow-ups** to dive deeper into the content

---

## 📁 Project Structure

```
Rem_ai/
├── backend/               # FastAPI backend
│   ├── main.py           # Main app & routes (300+ lines)
│   ├── parser.py         # PDF/TXT parsing with error handling
│   ├── chunker.py        # Intelligent text chunking
│   ├── embeddings.py     # Sentence Transformer integration
│   ├── vector_store.py   # FAISS vector database
│   ├── generator.py      # Ollama LLM integration
│   └── requirements.txt  # Dependencies
│
├── frontend/             # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx       # Main component
│   │   ├── Chat.jsx      # Chat component (auto-scroll, sources)
│   │   ├── FileUpload.jsx # Upload with drag-drop
│   │   └── *.css         # Modern styling
│   └── package.json
│
├── SETUP_GUIDE.md       # Comprehensive setup & API docs
└── readme.md            # This file
```

---

## 🔌 API Endpoints

### `GET /`
Health check - confirms backend is running

### `GET /health`
Detailed health status with vector store info

### `POST /upload`
Upload and index a document
- Required: `file` (PDF or TXT, max 100MB)
- Returns: `upload_id`, `total_chunks`, confirmation

### `POST /chat`
Ask a question about uploaded documents
- Required: `question` (string)
- Optional: `session_id`, `history`
- Returns: `answer`, `sources`, `status`, `session_id`

Example payload:
```json
{
	"question": "Summarize the main points",
	"session_id": "optional-session-id",
	"history": [
		{"role": "user", "text": "What is this document about?"},
		{"role": "assistant", "text": "It discusses..."}
	]
}
```

### `DELETE /chat/session/{session_id}`
Clear backend conversation memory for a session
- Returns: `status`, `session_id`, `cleared`

---

## ✨ Recent Improvements

✅ **Enhanced Error Handling** - Comprehensive try-catch with logging
✅ **Modern UI/UX** - Gradient backgrounds, animations, smooth transitions  
✅ **Drag-and-Drop Upload** - User-friendly file selection
✅ **Better Feedback** - Status messages, loading states, source attribution
✅ **Enter Key Support** - Send messages with Enter key
✅ **Source Citations** - See which document chunks informed answers
✅ **Input Validation** - File size limits, file type validation
✅ **Logging System** - Backend logging for debugging
✅ **Responsive Design** - Works on mobile and desktop
✅ **Loading Indicators** - Animated typing indicators while processing
✅ **Session Persistence** - Chat context persists across browser refreshes
✅ **Clear Chat Workflow** - Resets client + server session memory
✅ **Theme System** - Aqua Orange, Forest Cream, Midnight Copper
✅ **Retrieval Quality Upgrade** - Deduplicated context and deeper retrieval

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | `pip install -r requirements.txt` |
| Ollama connection error | Run `ollama serve` in another terminal |
| Frontend can't connect to backend | Ensure backend is running on `http://localhost:8000` |
| File upload fails | Check file size (max 100MB) and format (PDF/TXT only) |
| No response from AI | Start Ollama: `ollama pull llama3.2:3b && ollama serve` |
| Backend fails with paging file error | Run without `--reload` and avoid duplicate backend processes |

**For more help, see [SETUP_GUIDE.md](./SETUP_GUIDE.md)**

---

## 🚀 Performance

- **First Query**: ~3-5 seconds (model loading)
- **Subsequent Queries**: ~1-2 seconds
- **File Upload**: ~1-5 seconds (depends on file size)
- **Vector Search**: <100ms (FAISS optimized)

---

## 🔐 Privacy

✅ All processing is local - no data sent to external services
✅ Uploaded files stored on your machine
✅ Ollama runs locally
✅ No tracking or analytics

---

## 📝 License

Open source - MIT License

---

## 🙏 Acknowledgments

- OpenAI for embeddings research
- Facebook for FAISS
- Ollama team for local LLM inference
- React community for modern tooling

---

**Made with ❤️ for intelligent document interaction**

Questions? Check [SETUP_GUIDE.md](./SETUP_GUIDE.md) or review the [API documentation](#-api-endpoints).

Last Updated: April 2026
