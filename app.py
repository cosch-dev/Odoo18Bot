"""
Streamlit Web App for Odoo 18.0 Certification RAG Chatbot
Interactive interface for asking questions about Odoo documentation
"""

import streamlit as st
import os
from pathlib import Path
from rag_system import OdooRAGSystem
import time

# Page configuration
st.set_page_config(
    page_title="Odoo 18.0 Certification Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_resource
def load_rag_system():
    """Load RAG system (cached to avoid reloading)"""
    try:
        embeddings_path = "embeddings/odoo_embeddings.pkl"
        if not Path(embeddings_path).exists():
            st.error(f"Embeddings file not found at {embeddings_path}")
            st.info("Please run the setup process first:\n1. python data_processor.py\n2. python embedding_system.py")
            return None
        
        with st.spinner("Loading RAG system... This may take a moment."):
            rag = OdooRAGSystem(embeddings_path)
        return rag
    except Exception as e:
        st.error(f"Error loading RAG system: {str(e)}")
        return None

def main():
    # Header
    st.title("🚀 Odoo 18.0 Certification Assistant")
    st.markdown("*Your AI-powered study companion for Odoo 18.0 certification*")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        cert_mode = st.checkbox("🎯 Certification Mode", value=True, help="Optimized for fast, concise answers during timed exams")
        
        st.header("📋 Quick Guide")
        if cert_mode:
            st.markdown("""
            **Certification Mode (Fast):**
            - Concise, direct answers
            - Optimized for timed exams
            - Focus on correct answers
            
            **For multiple choice questions:**
            Include the options in your question for best results
            """)
        else:
            st.markdown("""
            **Study Mode (Detailed):**
            - Comprehensive explanations
            - Best practices included
            - Learning-focused responses
            """)
        
        st.markdown("""
        **Tips:**
        - Be specific in your questions
        - Use Odoo terminology
        - Ask about specific modules or features
        """)
        
        st.header("📚 Example Questions")
        example_questions = [
            "How do I create a new module in Odoo?",
            "What are the main components of an Odoo model?",
            "How do I configure email settings?",
            "What is the difference between kanban and list views?",
            "How do I set up multi-company configuration?",
            "How do I create custom fields in Odoo?",
            "What are Odoo security groups and access rights?",
            "How do I customize Odoo reports?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"btn_{hash(question)}"):
                st.session_state.current_question = question
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""
    
    # Load RAG system
    rag_system = load_rag_system()
    if rag_system is None:
        st.stop()
    
    # Display system stats
    with st.expander("📊 System Information"):
        stats = rag_system.get_system_stats()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Document Chunks", stats['vector_database']['total_chunks'])
        with col2:
            st.metric("Unique Documents", stats['vector_database']['unique_documents'])
        with col3:
            st.metric("Embedding Dimension", stats['vector_database']['embedding_dimension'])
    
    # Main chat interface
    st.header("💬 Ask Your Question")
    
    # Input area
    question_input = st.text_input(
        "Enter your Odoo question:",
        value=st.session_state.current_question,
        placeholder="e.g., How do I create a custom module in Odoo 18?"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ask_button = st.button("Ask Question", type="primary")
    with col2:
        clear_button = st.button("Clear History")
    
    if clear_button:
        st.session_state.messages = []
        st.session_state.current_question = ""
        st.rerun()
    
    # Process question
    if ask_button and question_input:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": question_input})
        
        # Get answer from RAG system (optimized for certification speed)
        with st.spinner("Generating answer..."):
            start_time = time.time()
            result = rag_system.ask(question_input, top_k=3)  # Fewer sources = faster response
            response_time = time.time() - start_time
        
        # Add assistant response to history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": result['answer'],
            "sources": result['sources'],
            "response_time": response_time
        })
        
        # Clear current question
        st.session_state.current_question = ""
    
    # Display conversation history
    if st.session_state.messages:
        st.header("📜 Conversation History")
        
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            
            elif message["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    
                    # Display sources
                    if "sources" in message and message["sources"]:
                        with st.expander(f"📖 Sources ({len(message['sources'])} documents found)"):
                            for j, source in enumerate(message["sources"]):
                                st.markdown(f"""
                                **{j+1}. {source['title']}** 
                                - Path: `{source['path']}`
                                - Similarity: {source['similarity']:.3f}
                                - [View Original]({source['url']})
                                
                                *Preview:* {source['preview']}
                                """)
                    
                    # Show response time
                    if "response_time" in message:
                        st.caption(f"⏱️ Response generated in {message['response_time']:.2f} seconds")
    
    # Footer
    st.markdown("---")
    st.markdown("*Powered by Gemini 2.5 Pro and built for Odoo 18.0 certification preparation*")

if __name__ == "__main__":
    main()