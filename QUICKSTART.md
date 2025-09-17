# 🚀 Quick Start Guide

## Option 1: Automatic Setup (Recommended)

```bash
./setup.sh
```

This will:
1. Create virtual environment
2. Install all dependencies  
3. Process documentation
4. Generate embeddings
5. Set up the complete system

## Option 2: Manual Setup

1. **Install dependencies:**
   ```bash
   python3 -m venv odoo_rag_env
   source odoo_rag_env/bin/activate
   pip install -r requirements.txt
   ```

2. **Process documentation:**
   ```bash
   source odoo_rag_env/bin/activate
   python data_processor.py  # For sample (50 docs)
   ```

3. **Generate embeddings:**
   ```bash
   source odoo_rag_env/bin/activate
   python embedding_system.py
   ```

4. **Run the web app:**
   ```bash
   source odoo_rag_env/bin/activate
   streamlit run app_improved.py
   ```

## 🌐 Using the Chatbot

1. Open your browser to `http://localhost:8501`
2. Ask questions about Odoo 18.0:
   - "How do I create a new module?"
   - "What are security groups?"
   - "How do I configure email settings?"
3. Review AI-generated answers with source references
4. Use example questions from the sidebar

## 📝 Example Questions

- **Module Development**: "How do I create a custom module in Odoo?"
- **Views**: "What's the difference between kanban and list views?"
- **Security**: "How do I set up user access rights?"
- **Configuration**: "How do I configure multi-company setup?"
- **Customization**: "How do I add custom fields to existing models?"

## 🔧 Customization

- **More documents**: Edit `data_processor.py` to remove the 50-doc limit
- **Better retrieval**: Adjust `top_k` in `rag_system.py`
- **UI changes**: Modify `app.py` for interface customization

## 🚨 Troubleshooting

**"Embeddings not found"**: Run `python embedding_system.py`
**"API key error"**: Check your `.env` file contains valid Gemini API key
**Slow responses**: Normal for first query, subsequent ones are faster

Happy studying! 🎓