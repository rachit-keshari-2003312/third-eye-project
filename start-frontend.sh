#!/bin/bash

# Third-Eye Frontend Startup Script

echo "🟢 Starting Third-Eye Angular Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

# Install Angular CLI globally if not installed
if ! command -v ng &> /dev/null; then
    echo "📦 Installing Angular CLI globally..."
    npm install -g @angular/cli
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📥 Installing Node.js dependencies..."
    npm install
else
    echo "📦 Node.js dependencies already installed"
fi

# Disable Angular analytics to avoid prompts
echo "⚙️ Configuring Angular settings..."
ng analytics disable

# Optional: Install MCP servers (commented out to avoid startup delays)
# Uncomment the following lines if you want to install MCP servers automatically
# echo "🔗 Installing MCP servers (this may take a while)..."
# npm install -g @modelcontextprotocol/server-filesystem 2>/dev/null || echo "⚠️ Filesystem MCP server installation failed"
# npm install -g @modelcontextprotocol/server-git 2>/dev/null || echo "⚠️ Git MCP server installation failed"
# npm install -g @modelcontextprotocol/server-sqlite 2>/dev/null || echo "⚠️ SQLite MCP server installation failed"

# Check if port 4200 is already in use
if lsof -Pi :4200 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Port 4200 is already in use. Attempting to kill existing process..."
    lsof -ti:4200 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Start the Angular development server
echo "🚀 Starting Angular development server on http://localhost:4200"
echo "📝 Note: The server will automatically open in your browser"
echo ""

# Start with proper error handling
if ng serve --host 0.0.0.0 --port 4200 --open; then
    echo "✅ Frontend server started successfully!"
else
    echo "❌ Failed to start frontend server"
    echo "💡 Try running: ng serve --port 4200 --host 0.0.0.0"
    exit 1
fi

echo "🌐 Application URL: http://localhost:4200"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"