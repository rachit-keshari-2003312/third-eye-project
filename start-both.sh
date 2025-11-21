#!/bin/bash

# Third-Eye Complete System Startup Script

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

echo "🚀 Starting Third-Eye Agentic AI Platform..."
echo "================================================"
echo "📂 Working directory: $(pwd)"

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    echo "🔄 Killing process on port $port..."
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Check and clean up ports
if check_port 8000; then
    echo "⚠️  Port 8000 (Backend) is in use"
    kill_port 8000
fi

if check_port 4200; then
    echo "⚠️  Port 4200 (Frontend) is in use"
    kill_port 4200
fi

echo ""
echo "🔵 Step 1: Starting Backend Server..."
echo "======================================"

# Start backend in background
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install minimal required dependencies
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "📥 Installing backend dependencies..."
    python3 -m pip install fastapi uvicorn boto3 httpx python-multipart
fi

# Start backend
echo "🚀 Starting FastAPI backend..."
(cd backend && python3 app.py) &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend started successfully
if check_port 8000; then
    echo "✅ Backend started successfully on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "🟢 Step 2: Starting Frontend Server..."
echo "======================================"

# Ensure we're back in the script directory
cd "$SCRIPT_DIR"
echo "📂 Frontend working directory: $(pwd)"

# Disable Angular analytics
ng analytics disable &>/dev/null || true

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    npm install
fi

# Start frontend
echo "🚀 Starting Angular frontend..."
ng serve --host 0.0.0.0 --port 4200 --open &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to initialize..."
sleep 10

# Check if frontend started successfully
if check_port 4200; then
    echo "✅ Frontend started successfully on http://localhost:4200"
else
    echo "❌ Frontend failed to start"
    kill $FRONTEND_PID 2>/dev/null || true
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "🎉 Third-Eye Platform Started Successfully!"
echo "=========================================="
echo "🌐 Frontend:     http://localhost:4200"
echo "🔧 Backend API:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
echo "🩺 Health Check: http://localhost:8000/health"
echo ""
echo "📝 Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down Third-Eye Platform..."
    kill $FRONTEND_PID 2>/dev/null || true
    kill $BACKEND_PID 2>/dev/null || true
    echo "✅ Cleanup complete"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
