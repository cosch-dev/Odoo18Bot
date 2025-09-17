#!/bin/bash

echo "🚀 Launching Simple ChatGPT-Style Interface"
echo "=========================================="
echo "✨ Features:"
echo "   - Clean ChatGPT-style layout"
echo "   - AI messages on left (🤖)"
echo "   - User messages on right (👤)"
echo "   - Auto-scrolling chat"
echo "   - Enter key to send"
echo "   - Typing indicator"
echo "   - Clean message bubbles"
echo ""

# Kill any existing streamlit processes
pkill -f streamlit 2>/dev/null
sleep 2

# Activate environment and launch
source odoo_rag_env/bin/activate
streamlit run app_simple_chat.py --server.headless true

echo "Simple chat interface stopped."