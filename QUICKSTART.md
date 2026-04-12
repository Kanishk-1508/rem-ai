# Quick Start Guide - rem.ai

Get your document chat app running in a few minutes.

---

## Fastest Start

### Windows
```bash
start.bat
```

### macOS/Linux
```bash
chmod +x start.sh
./start.sh
```

Open: `http://localhost:5173` (or `http://localhost:5174` if 5173 is busy)

---

## Manual Start (Recommended)

### 1. Backend
```bash
cd backend
conda activate remai
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Ollama (new terminal)
```bash
ollama pull llama3.2:3b
ollama serve
```

### 3. Frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```

---

## Use the App

1. Upload a PDF/TXT file.
2. Ask a question in chat.
3. Ask follow-up questions (session memory is enabled).
4. Click **Clear Chat** to reset local + backend session memory.
5. Pick a theme from the theme pills in the header.

---

## Health Checks

### Backend
```bash
curl http://localhost:8000/health
```

### Ollama
```bash
ollama list
```

### Frontend
Open `http://localhost:5173` (or `http://localhost:5174`).

---

## Common Issues

### Backend startup fails with paging file error
Run backend **without** reload:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Port 8000 already in use
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

### Ollama not responding
```bash
ollama serve
ollama pull llama3.2:3b
```

### Upload feels slow
- Upload progress is shown in UI.
- After upload reaches high %, server may still be indexing chunks/embeddings.
- Very large documents take longer.

---

## What is New

- Session-based conversation memory.
- Clear Chat button (client + server reset).
- Multi-theme UI switcher with persistent selection.
- Better retrieval quality (dedup + deeper search).
- Improved upload/status feedback.

---

Last Updated: April 2026
