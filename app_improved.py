"""
Improved Streamlit Web App for Odoo 18.0 Certification RAG Chatbot
Modern chat interface with persistent history and auto-scroll
"""

import streamlit as st
import os
from pathlib import Path
from rag_system import OdooRAGSystem
import time
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Odoo 18.0 Certification Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for full-screen chat interface
st.markdown("""
<style>
/* Full-screen chat layout */
.main-chat-area {
    height: 100vh;
    display: flex;
    flex-direction: column;
    background: white;
    position: relative;
}

.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 1rem 2rem;
    background: white;
    scroll-behavior: smooth;
}

.chat-input-container {
    position: sticky;
    bottom: 0;
    background: white;
    border-top: 1px solid #e0e0e0;
    padding: 1rem 2rem;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

/* User message (right side) */
.user-message {
    display: flex;
    justify-content: flex-end;
    margin: 1rem 0;
}

.user-bubble {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    padding: 1rem 1.25rem;
    border-radius: 20px 20px 5px 20px;
    max-width: 75%;
    word-wrap: break-word;
    box-shadow: 0 2px 10px rgba(0, 123, 255, 0.3);
    font-size: 0.95rem;
    line-height: 1.4;
}

/* Assistant message (left side) */
.assistant-message {
    display: flex;
    justify-content: flex-start;
    margin: 1rem 0;
}

.assistant-bubble {
    background: white;
    color: #333;
    padding: 1rem 1.25rem;
    border-radius: 20px 20px 20px 5px;
    max-width: 75%;
    word-wrap: break-word;
    border: 1px solid #e0e0e0;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    font-size: 0.95rem;
    line-height: 1.4;
}

/* History sidebar scrollable area */
.history-container {
    max-height: 500px;
    overflow-y: auto;
    padding-right: 8px;
}

/* History item styles */
.history-item {
    padding: 0.5rem;
    border-radius: 8px;
    margin: 0.25rem 0;
    cursor: pointer;
    transition: background-color 0.2s;
    border-left: 3px solid #007bff;
    background: #f8f9fa;
}

.history-item:hover {
    background-color: #e9ecef;
}

.history-question {
    font-weight: 500;
    color: #007bff;
    font-size: 0.9rem;
}

.history-time {
    font-size: 0.75rem;
    color: #6c757d;
    margin-top: 0.25rem;
}

/* Style for Streamlit buttons in history */
.stButton > button {
    width: 100% !important;
    text-align: left !important;
    white-space: pre-wrap !important;
    height: auto !important;
    padding: 0.5rem !important;
    font-size: 0.85rem !important;
    border-left: 3px solid #007bff !important;
}

/* Modern input styling */
.chat-input-container .stTextInput > div > div > input {
    border-radius: 25px;
    padding: 1rem 1.5rem;
    font-size: 1rem;
    border: 2px solid #e0e0e0;
    transition: all 0.3s ease;
    width: 100%;
    background: #f8f9fa;
}

.chat-input-container .stTextInput > div > div > input:focus {
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
    background: white;
}

/* Modern send button */
.chat-input-container .stButton > button {
    border-radius: 25px;
    padding: 1rem 2rem;
    font-weight: 600;
    border: none;
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    transition: all 0.3s ease;
}

.chat-input-container .stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

/* Custom scrollbar for chat messages */
.chat-messages::-webkit-scrollbar {
    width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
    background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
}

/* Hide Streamlit default elements for cleaner look */
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 0;
    max-width: none;
}

/* Full screen adjustments */
.stApp > header {
    display: none;
}

/* Remove default padding */
.css-1d391kg {
    padding: 0;
}

/* Ensure full width for chat */
.main-chat-area {
    width: 100%;
    margin: 0;
}

/* Welcome message for empty chat */
.welcome-message {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 50vh;
    text-align: center;
    color: #666;
}

.welcome-message h2 {
    color: #007bff;
    margin-bottom: 1rem;
}

.welcome-message p {
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
}

/* Custom metrics */
.metric-container {
    background: linear-gradient(90deg, #007bff, #0056b3);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

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

def save_chat_history(messages):
    """Save chat history to file"""
    history_file = Path("chat_history.json")
    try:
        with open(history_file, 'w') as f:
            json.dump(messages, f, indent=2, default=str)
    except Exception as e:
        st.error(f"Error saving chat history: {e}")

def load_chat_history():
    """Load chat history from file"""
    history_file = Path("chat_history.json")
    try:
        if history_file.exists():
            with open(history_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
    return []

def render_chat_message(message, is_user=True):
    """Render a single chat message"""
    # Clean content but preserve text formatting - don't escape HTML since we're rendering with unsafe_allow_html
    content = message['content'] if isinstance(message['content'], str) else str(message['content'])
    # Replace any potential problematic characters that could break HTML structure
    content = content.replace('<script', '&lt;script').replace('</script>', '&lt;/script&gt;')
    
    if is_user:
        return f"""
        <div class="user-message">
            <div class="user-bubble">
                {content}
            </div>
        </div>
        """
    else:
        return f"""
        <div class="assistant-message">
            <div class="assistant-bubble">
                {content}
            </div>
        </div>
        """

def main():
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = load_chat_history()
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""
    if 'selected_history_item' not in st.session_state:
        st.session_state.selected_history_item = None
    
    # Sidebar with title, settings and history
    with st.sidebar:
        st.title("🚀 Odoo 18.0 Certification Assistant")
        st.markdown("*Your AI-powered study companion for Odoo 18.0 certification*")
        st.markdown("---")
        
        st.header("⚙️ Settings")
        cert_mode = st.checkbox("🎯 Certification Mode", value=True, help="Optimized for fast, concise answers during timed exams")
        
        st.header("📝 Question History")
        
        def detect_module(question, sources):
            """Detect Odoo module from question content and sources"""
            question_lower = question.lower()
            
            # Priority keywords for common modules
            module_keywords = {
                'Inventory': ['inventory', 'stock', 'warehouse', 'product', 'barcode', 'lot', 'serial'],
                'Sales': ['sale', 'sales', 'quotation', 'order', 'customer', 'crm', 'lead'],
                'Purchase': ['purchase', 'vendor', 'supplier', 'rfq', 'po'],
                'Accounting': ['account', 'invoice', 'bill', 'payment', 'journal', 'tax', 'reconcile'],
                'Manufacturing': ['manufacturing', 'mrp', 'bom', 'production', 'work order'],
                'HR': ['hr', 'employee', 'payroll', 'timesheet', 'expense', 'recruitment'],
                'Project': ['project', 'task', 'milestone', 'planning'],
                'Website': ['website', 'ecommerce', 'blog', 'seo', 'portal'],
                'Security': ['security', 'user', 'group', 'permission', 'access', 'rights'],
                'Configuration': ['config', 'setup', 'installation', 'settings', 'company'],
                'Development': ['module', 'model', 'field', 'view', 'xml', 'python', 'custom'],
                'Reports': ['report', 'dashboard', 'analytics', 'qweb'],
                'Email': ['email', 'mail', 'notification', 'template']
            }
            
            # Check question content first
            for module, keywords in module_keywords.items():
                if any(keyword in question_lower for keyword in keywords):
                    return module
            
            # Check sources paths if available
            if sources:
                for source in sources[:3]:  # Check top 3 sources
                    path = source.get('path', '').lower()
                    if 'finance' in path or 'accounting' in path:
                        return 'Accounting'
                    elif 'sales' in path or 'crm' in path:
                        return 'Sales'
                    elif 'purchase' in path:
                        return 'Purchase'
                    elif 'stock' in path or 'inventory' in path:
                        return 'Inventory'
                    elif 'manufacturing' in path or 'mrp' in path:
                        return 'Manufacturing'
                    elif 'hr' in path:
                        return 'HR'
                    elif 'project' in path:
                        return 'Project'
                    elif 'website' in path:
                        return 'Website'
            
            # Default fallback
            return 'General'
        
        # Extract unique questions from messages
        questions = []
        for i in range(0, len(st.session_state.messages), 2):
            if i + 1 < len(st.session_state.messages):
                user_msg = st.session_state.messages[i]
                assistant_msg = st.session_state.messages[i + 1]
                if user_msg.get('role') == 'user' and assistant_msg.get('role') == 'assistant':
                    module = detect_module(user_msg['content'], assistant_msg.get('sources', []))
                    questions.append({
                        'question': user_msg['content'][:60] + "..." if len(user_msg['content']) > 60 else user_msg['content'],
                        'full_question': user_msg['content'],
                        'answer': assistant_msg['content'],
                        'timestamp': assistant_msg.get('timestamp', 'Unknown time'),
                        'sources': assistant_msg.get('sources', []),
                        'response_time': assistant_msg.get('response_time', 0),
                        'module': module
                    })
        
        # Show ALL questions with improved labeling in a scrollable container
        if questions:
            st.markdown('<div class="history-container">', unsafe_allow_html=True)
            for i, q in enumerate(questions):
                question_label = f"Question {i+1} - {q['module']}"
                question_preview = q['question']
                
                if st.button(
                    f"{question_label}\n{question_preview}", 
                    key=f"hist_{i}", 
                    help=f"Module: {q['module']} | Asked: {q['timestamp']}",
                    use_container_width=True
                ):
                    st.session_state.selected_history_item = q
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("*No questions asked yet. Start by asking your first Odoo question below!*")
        
        # Clear history button
        if st.button("🗑️ Clear History"):
            st.session_state.messages = []
            st.session_state.selected_history_item = None
            save_chat_history([])
            st.rerun()
        
        st.markdown("---")
        
        # System Information in sidebar
        st.header("📊 System Information")
        
        # Load RAG system first
        rag_system = load_rag_system()
        if rag_system is not None:
            stats = rag_system.get_system_stats()
            st.metric("Document Chunks", stats['vector_database']['total_chunks'])
            st.metric("Unique Documents", stats['vector_database']['unique_documents']) 
            st.metric("Embedding Dimensions", stats['vector_database']['embedding_dimension'])
        else:
            st.error("System not loaded")
            st.stop()
    
    # Full-screen chat interface - no containers or frames
    st.markdown('<div class="main-chat-area">', unsafe_allow_html=True)
    
    # Chat messages area - full height, no borders
    chat_messages_html = '<div class="chat-messages" id="chat-messages">'
    
    # Show selected history item or current conversation
    if st.session_state.selected_history_item:
        item = st.session_state.selected_history_item
        chat_messages_html += render_chat_message({'content': item['full_question']}, is_user=True)
        chat_messages_html += render_chat_message({'content': item['answer']}, is_user=False)
        
        # Show sources inline
        if item['sources']:
            sources_html = '<div style="margin: 1rem 0; padding: 1rem; background: #f0f2f6; border-radius: 8px; border-left: 4px solid #007bff; max-width: 75%;">'
            sources_html += f'<strong>📖 Sources ({len(item["sources"])} found):</strong><br><br>'
            for i, source in enumerate(item['sources']):
                sources_html += f'{i+1}. <strong>{source["title"]}</strong> (similarity: {source["similarity"]:.3f})<br>'
                sources_html += f'   Path: <code>{source["path"]}</code><br>'
                sources_html += f'   <a href="{source["url"]}" target="_blank">View Original</a><br><br>'
            sources_html += '</div>'
            chat_messages_html += sources_html
    else:
        # Show current conversation or welcome message
        if not st.session_state.messages:
            # Welcome message for empty chat
            chat_messages_html += '''
            <div class="welcome-message">
                <h2>🚀 Welcome to your Odoo 18.0 Certification Assistant!</h2>
                <p>Ask me anything about Odoo 18.0 to help with your certification preparation.</p>
                <p>I have access to <strong>6,465 document chunks</strong> covering all Odoo modules.</p>
                <br>
                <p><strong>Try asking:</strong></p>
                <p>• "How do I create a custom module in Odoo?"</p>
                <p>• "What are security groups and access rights?"</p>
                <p>• "How do I configure multi-company setup?"</p>
                <p>• "What's the difference between kanban and list views?"</p>
            </div>
            '''
        else:
            for i, message in enumerate(st.session_state.messages):
                if message["role"] == "user":
                    chat_messages_html += render_chat_message(message, is_user=True)
                elif message["role"] == "assistant":
                    chat_messages_html += render_chat_message(message, is_user=False)
                    
                    # Add sources inline after each assistant message
                    if 'sources' in message and message['sources']:
                        sources_html = '<div style="margin: 1rem 0; padding: 1rem; background: #f0f2f6; border-radius: 8px; border-left: 4px solid #007bff; max-width: 75%;">'
                        sources_html += f'<strong>📖 Sources ({len(message["sources"])} found):</strong><br><br>'
                        for j, source in enumerate(message['sources']):
                            sources_html += f'{j+1}. <strong>{source["title"]}</strong> (similarity: {source["similarity"]:.3f})<br>'
                            sources_html += f'   <a href="{source["url"]}" target="_blank">View Original</a><br><br>'
                        sources_html += '</div>'
                        chat_messages_html += sources_html
    
    chat_messages_html += '</div>'
    st.markdown(chat_messages_html, unsafe_allow_html=True)
    
    # Fixed input area at bottom
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    
    # Show back button if viewing history
    if st.session_state.selected_history_item:
        if st.button("⬅️ Back to Live Chat", type="secondary"):
            st.session_state.selected_history_item = None
            st.rerun()
    
    # Question input with modern styling and Enter key support
    question_input = st.text_input(
        "",
        value=st.session_state.current_question,
        placeholder="Ask your Odoo question here...",
        key="question_input",
        label_visibility="collapsed",
        on_change=None
    )
    
    # Add JavaScript for Enter key functionality
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const input = document.querySelector('input[aria-label=""]');
        if (input) {
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const sendBtn = document.querySelector('[data-testid="baseButton-primary"]');
                    if (sendBtn) sendBtn.click();
                }
            });
        }
    });
    </script>
    """, unsafe_allow_html=True)
    
    col_btn1, col_btn2 = st.columns([1, 8])
    with col_btn1:
        ask_button = st.button("✈️", type="primary", use_container_width=True, help="Send message (or press Enter)")
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close input container
    st.markdown('</div>', unsafe_allow_html=True)  # Close main chat area
    
    # Auto-scroll to bottom after new messages
    st.markdown("""
    <script>
    function scrollToBottom() {
        var chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    setTimeout(scrollToBottom, 100);
    </script>
    """, unsafe_allow_html=True)
    # Process question
    if ask_button and question_input:
        # Clear history selection
        st.session_state.selected_history_item = None
        
        # Clear the text input by updating current_question
        st.session_state.current_question = ""
        
        # Add user message
        user_msg = {
            "role": "user",
            "content": question_input,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.messages.append(user_msg)
        
        # Get answer from RAG system
        with st.spinner("Generating answer..."):
            start_time = time.time()
            result = rag_system.ask(question_input, top_k=3)
            response_time = time.time() - start_time
        
        # Add assistant response
        assistant_msg = {
            "role": "assistant",
            "content": result['answer'],
            "sources": result['sources'],
            "response_time": response_time,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.messages.append(assistant_msg)
        
        # Save history
        save_chat_history(st.session_state.messages)
        
        # Clear current question and refresh
        st.session_state.current_question = ""
        st.rerun()

if __name__ == "__main__":
    main()