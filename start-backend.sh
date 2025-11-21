#!/bin/bash
# Start Backend Server Script

echo "🚀 Starting Third-Eye Backend (REAL MODE)..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Go to project root
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Go to backend and start REAL version
cd backend
python3 app_real.py
