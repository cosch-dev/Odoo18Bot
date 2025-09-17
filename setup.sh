#!/bin/bash

echo "🚀 Setting up Odoo 18.0 Certification RAG Chatbot"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "odoo_rag_env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv odoo_rag_env
fi

# Activate virtual environment and install dependencies
echo "Activating environment and installing dependencies..."
source odoo_rag_env/bin/activate && pip install -r requirements.txt

# Check if processed docs exist
if [ ! -f "processed_docs/processed_odoo_docs.json" ]; then
    echo ""
    echo "📥 Processing Odoo documentation..."
    echo "This will download and process documentation from 1,364 URLs."
    read -p "Process sample (50 docs) or all docs? [s/all]: " choice
    
    if [ "$choice" = "all" ]; then
        echo "Processing all 1,364 documents... This may take 30+ minutes."
        source odoo_rag_env/bin/activate && python -c "
from data_processor import OdooDocProcessor
processor = OdooDocProcessor('odoo_docs_links.csv')
processor.process_all_docs(max_docs=None, delay=1.5)
processor.save_processed_docs()
"
    else
        echo "Processing sample of 50 documents..."
        source odoo_rag_env/bin/activate && python data_processor.py
    fi
fi

# Check if embeddings exist
if [ ! -f "embeddings/odoo_embeddings.pkl" ]; then
    echo ""
    echo "🧠 Generating embeddings using Gemini API..."
    echo "This will create embeddings for semantic search."
    source odoo_rag_env/bin/activate && python embedding_system.py
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 To run the web application:"
echo "   source odoo_rag_env/bin/activate && streamlit run app.py"
echo ""
echo "🧪 To test the RAG system:"
echo "   source odoo_rag_env/bin/activate && python rag_system.py"
echo ""
echo "📊 Your chatbot is ready for Odoo 18.0 certification prep!"