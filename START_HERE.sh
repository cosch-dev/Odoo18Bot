#!/bin/bash

# Odoo 18.0 Certification Assistant - One-Click Startup Script
# Just double-click this file or run: ./START_HERE.sh

echo "🚀 Starting Odoo 18.0 Certification Assistant..."
echo "============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 from https://python.org"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "odoo_rag_env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv odoo_rag_env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source odoo_rag_env/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --quiet -r requirements.txt

# Check if .env file exists, if not create it with the API key
if [ ! -f ".env" ]; then
    echo "🔑 Setting up API key..."
    # Replace this with your actual API key
    echo "GEMINI_API_KEY=AIzaSyAH8x4nfOVBGkZx-YqQv8gPqhC_r0mfkdI" > .env
fi

# Load environment variables
export $(cat .env | xargs)

echo ""
echo "✅ Setup complete!"
echo "🌐 Starting Flask server..."
echo "📱 Your browser will open automatically to http://localhost:5000"
echo ""
echo "⚡ Features available:"
echo "   - Text questions with RAG from 6,465 Odoo docs"
echo "   - Image paste support (Ctrl+V)"
echo "   - Multi-question formatting"
echo "   - Source references"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the Flask app
python app_flask.py