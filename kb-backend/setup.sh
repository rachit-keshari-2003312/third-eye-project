#!/bin/bash
echo "🚀 Setting up Knowledge Base API Service..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "🔧 Next steps:"
echo "1. Make sure your AWS credentials are configured:"
echo "   aws configure --profile kb-profile"
echo ""
echo "2. Start the service:"
echo "   ./start-backend.sh"
echo ""
echo "3. Test the API:"
echo "   curl http://localhost:8000/health"
