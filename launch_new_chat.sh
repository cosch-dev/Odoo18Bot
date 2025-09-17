#!/bin/bash

echo "🚀 Launching New Full-Window Chat Interface"
echo "=========================================="
echo "✨ Features:"
echo "   - Full-window chat like iMessage/WhatsApp"
echo "   - Title & system info in sidebar"
echo "   - Sources shown inline with messages"
echo "   - Modern chat bubbles with shadows"
echo "   - Auto-scroll to bottom"
echo "   - Question history with module detection"
echo ""

# Kill any existing streamlit processes
pkill -f streamlit 2>/dev/null
sleep 2

# Activate environment and launch
source odoo_rag_env/bin/activate
streamlit run app_improved.py --server.headless true

echo "Chat interface stopped."