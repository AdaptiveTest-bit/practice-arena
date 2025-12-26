#!/bin/bash
# Setup and run script for CBSE Class 5 Mathematics Question Generator

set -e

echo "🎓 CBSE Class 5 Mathematics Question Generator"
echo "================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start the web interface:"
echo "  python app.py"
echo ""
echo "Then open: http://127.0.0.1:5001"
echo ""
echo "To generate questions in terminal:"
echo "  python question_generator.py"
echo ""
echo "For more help, read:"
echo "  - README.md (Full documentation)"
echo "  - QUICK_START.md (Quick reference)"
echo "  - CLI_GUIDE.md (Command-line usage)"
echo ""

# Optional: Ask to start server now
read -p "Start the web server now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python app.py
fi
