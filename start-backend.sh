#!/bin/bash
# Start Backend Server Script

echo "🚀 Starting Third-Eye Backend (REAL MODE)..."
echo ""

# Go to project root
cd /Users/sanu.chaudhary/Desktop/Finhack/third-eye-project

# Activate virtual environment
source venv/bin/activate

# Go to backend and start REAL version
cd backend
python3 app_real.py
