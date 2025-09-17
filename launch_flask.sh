#!/bin/bash

echo "🚀 Launching Flask Chat Interface"
echo "=================================="
echo "✨ Features:"
echo "   - Clean, professional design"
echo "   - No sidebar issues!"
echo "   - AI messages on left (🤖)"
echo "   - User messages on right (👤)"
echo "   - Auto-clearing inputs"
echo "   - Perfect mobile support"
echo "   - Same RAG system (6,465 chunks)"
echo ""

# Kill any existing processes
pkill -f "python app_flask.py" 2>/dev/null
pkill -f streamlit 2>/dev/null
sleep 2

# Activate environment and launch Flask
cd /home/odoo/Desktop/HopeDocs
source odoo_rag_env/bin/activate
python app_flask.py

echo "Flask chat interface stopped."