#!/bin/bash

# Third-Eye Backend Startup Script

echo "🔵 Starting Third-Eye Backend Server..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Check if basic dependencies are installed
if ! python -c "import fastapi" &> /dev/null; then
    echo "📥 Installing essential Python dependencies..."
    pip install fastapi uvicorn boto3 httpx python-multipart
else
    echo "📦 Essential dependencies already installed"
fi

# Create necessary directories
mkdir -p logs
mkdir -p data

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Port 8000 is already in use. Attempting to kill existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Start the backend server
echo "🚀 Starting FastAPI server on http://localhost:8000"
echo "📝 Note: Server will start with auto-reload enabled"
echo ""

# Start with proper error handling
if cd backend && python app.py; then
    echo "✅ Backend server started successfully!"
else
    echo "❌ Failed to start backend server"
    echo "💡 Check the error messages above for troubleshooting"
    exit 1
fi

echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo "🌐 Frontend: http://localhost:4200"