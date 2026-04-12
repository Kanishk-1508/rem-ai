#!/bin/bash

# rem.ai Quick Start Script for macOS/Linux

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              rem.ai - Quick Start Script                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Install it using: brew install python (macOS) or apt install python3 (Linux)"
    exit 1
fi

# Check if Node is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Install it from: https://nodejs.org"
    exit 1
fi

# Check if Ollama is available
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Warning: Ollama not found"
    echo "Download from: https://ollama.ai"
fi

echo "✓ Prerequisites check passed!"
echo ""
echo "Starting rem.ai services..."
echo ""

# Start backend
echo "[1/3] Starting Backend Server (FastAPI)..."
cd backend
python3 -m venv venv 2>/dev/null
source venv/bin/activate
pip install -r requirements.txt -q
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

sleep 2

# Start Ollama
echo "[2/3] Checking Ollama..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Ollama not running. Starting Ollama..."
    ollama serve &
    OLLAMA_PID=$!
    sleep 2
    # Pull model if not present
    ollama pull llama2
else
    echo "✓ Ollama already running"
fi

# Start frontend
echo "[3/3] Starting Frontend (React + Vite)..."
cd frontend
npm install > /dev/null 2>&1
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Services Starting... Please Wait                  ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  📱 Frontend:  http://localhost:5173                        ║"
echo "║  🔧 Backend:   http://localhost:8000                        ║"
echo "║  🤖 Ollama:    http://localhost:11434                       ║"
echo "║                                                              ║"
echo "║  First-time setup may take 2-3 minutes...                  ║"
echo "║                                                              ║"
echo "║  🌐 Open http://localhost:5173 in your browser             ║"
echo "║                                                              ║"
echo "║  To stop, press Ctrl+C                                      ║"
echo "║                                                              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Wait for all processes
wait
