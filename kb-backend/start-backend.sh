#!/bin/bash
echo "🚀 Starting Knowledge Base API Service..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Set environment variables
export KNOWLEDGE_BASE_ID="BERDQ7EHF4"
export DATA_SOURCE_ID="0UR6Z3A5HY"
export AWS_PROFILE="kb-profile"
export AWS_REGION="eu-north-1"
export AWS_DEFAULT_REGION="eu-north-1"
export STRANDS_KNOWLEDGE_BASE_ID="BERDQ7EHF4"
export BYPASS_TOOL_CONSENT="true"
export HOST="0.0.0.0"
export PORT="8000"

echo "🔧 Environment variables set"

# Check if AWS credentials are configured
if ! aws sts get-caller-identity --profile kb-profile &>/dev/null; then
    echo "❌ AWS credentials not found for profile 'kb-profile'"
    echo "Please configure AWS credentials first:"
    echo "aws configure --profile kb-profile"
    exit 1
fi

echo "✅ AWS credentials verified"

# Start the FastAPI server
echo "🌐 Starting FastAPI server on http://$HOST:$PORT"
echo "📖 API documentation available at http://$HOST:$PORT/docs"
echo "🏥 Health check at http://$HOST:$PORT/health"
echo ""
echo "Press Ctrl+C to stop the server"

python3 main.py
