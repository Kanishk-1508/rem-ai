@echo off
REM rem.ai Quick Start Script for Windows

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║              rem.ai - Quick Start Script                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

setlocal enabledelayedexpansion

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org
    pause
    exit /b 1
)

REM Check if Node is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Node.js is not installed or not in PATH
    echo Please install Node.js LTS from https://nodejs.org
    pause
    exit /b 1
)

REM Check if Ollama is available
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Ollama not found. You'll need to start it separately.
    echo Download from: https://ollama.ai
)

echo ✓ Prerequisites check passed!
echo.
echo Starting rem.ai services...
echo.

REM Start backend
echo [1/3] Starting Backend Server (FastAPI)...
start "rem.ai Backend" cmd /k "cd backend && python -m venv venv 2>nul & call venv\Scripts\activate.bat & pip install -r requirements.txt -q & uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak

REM Start Ollama (if not running)
echo [2/3] Checking Ollama...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo ⚠️  Ollama not running. Starting Ollama...
    start "rem.ai Ollama" ollama serve
) else (
    echo ✓ Ollama already running
)

timeout /t 3 /nobreak

REM Start frontend
echo [3/3] Starting Frontend (React + Vite)...
start "rem.ai Frontend" cmd /k "cd frontend && npm install & npm run dev"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║           Services Starting... Please Wait                  ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║                                                              ║
echo ║  📱 Frontend:  http://localhost:5173                        ║
echo ║  🔧 Backend:   http://localhost:8000                        ║
echo ║  🤖 Ollama:    http://localhost:11434                       ║
echo ║                                                              ║
echo ║  First-time setup may take 2-3 minutes...                  ║
echo ║  Check windows for progress updates                         ║
echo ║                                                              ║
echo ║  🌐 Open http://localhost:5173 in your browser             ║
echo ║                                                              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo Press any key to minimize this window...
pause >nul

REM Minimize current window
if defined TERM_PROGRAM (
    exit
) else (
    start "" nircmd.exe win minimize
)

exit /b 0
