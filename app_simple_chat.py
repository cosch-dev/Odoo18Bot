"""
🚀 Odoo 18.0 Certification RAG Chatbot - Simple Chat Interface
Clean, ChatGPT-style interface following the blueprint
"""
import streamlit as st
import json
import time
from pathlib import Path
from datetime import datetime
from rag_system import OdooRAGSystem

# Page config
st.set_page_config(
    page_title="Odoo 18.0 Certification Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ChatGPT-style interface
st.markdown("""
<style>
/* Hide default streamlit elements */
.stDeployButton {display: none;}
header[data-testid="stHeader"] {display: none;}
.stMainBlockContainer {padding-top: 0;}

/* Remove all scrollbars from main content */
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 0;
    max-width: 100%;
}

/* Hide main scrollbar */
.main {
    overflow: hidden;
}

/* Floating sidebar toggle button - only show when sidebar is hidden */
.sidebar-toggle-float {
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 999;
    background: #0e1117;
    color: white;
    border: 1px solid #262730;
    border-radius: 8px;
    padding: 8px 12px;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    font-size: 14px;
    font-weight: 500;
}

.sidebar-toggle-float:hover {
    background: #262730;
    transform: translateY(-1px);
    transition: all 0.2s ease;
}

/* Chat container - full screen without frame */
.chat-container {
    height: calc(100vh - 200px);
    overflow-y: auto;
    padding: 20px;
    background: transparent;
    margin-bottom: 20px;
    scroll-behavior: smooth;
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* IE/Edge */
}

.chat-container::-webkit-scrollbar {
    display: none; /* Chrome/Safari/Opera */
}

/* Message bubbles */
.message {
    display: flex;
    margin: 15px 0;
    animation: fadeIn 0.3s ease-in;
}

.message.user {
    justify-content: flex-end;
}

.message.ai {
    justify-content: flex-start;
}

.message-bubble {
    max-width: 70%;
    padding: 12px 16px;
    border-radius: 18px;
    word-wrap: break-word;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.message-bubble.user {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    margin-left: 20px;
}

.message-bubble.ai {
    background: white;
    color: #333;
    border: 1px solid #e0e0e0;
    margin-right: 20px;
}

.message-icon {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 8px;
    font-size: 16px;
}

.message-icon.user {
    background: #007bff;
    color: white;
}

.message-icon.ai {
    background: #f0f0f0;
    color: #333;
}

/* Typing indicator */
.typing {
    display: flex;
    align-items: center;
    gap: 4px;
    color: #666;
    padding: 8px;
}

.typing-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #666;
    animation: typing 1.4s infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-10px); }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Input area */
.input-container {
    position: fixed;
    bottom: 0;
    left: 20rem;
    right: 0;
    background: white;
    padding: 20px;
    border-top: 1px solid #e0e0e0;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
}

.input-row {
    display: flex;
    gap: 10px;
    align-items: center;
}

/* Sources */
.sources {
    margin-top: 10px;
    padding: 8px 12px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 3px solid #007bff;
    font-size: 0.85em;
    color: #666;
}

.source-link {
    color: #007bff;
    text-decoration: none;
    margin-right: 10px;
}

.source-link:hover {
    text-decoration: underline;
}

/* Sidebar styling */
.sidebar-content {
    padding: 1rem;
}

.system-info {
    background: linear-gradient(135deg, #007bff, #0056b3);
    color: white;
    padding: 15px;
    border-radius: 10px;
    margin: 15px 0;
    text-align: center;
}

.history-item {
    margin: 5px 0;
    padding: 8px;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
    background: white;
    cursor: pointer;
    transition: all 0.2s;
}

.history-item:hover {
    background: #f8f9fa;
    border-color: #007bff;
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
            st.info("Please run: python embedding_system.py")
            return None
        return OdooRAGSystem(embeddings_path)
    except Exception as e:
        st.error(f"Error loading RAG system: {e}")
        return None

def save_chat_history(messages):
    """Save chat history to JSON file"""
    try:
        with open("chat_history.json", "w") as f:
            json.dump(messages, f, indent=2)
    except Exception as e:
        st.error(f"Error saving chat history: {e}")

def load_chat_history():
    """Load chat history from JSON file"""
    try:
        if Path("chat_history.json").exists():
            with open("chat_history.json", "r") as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
    return []

def detect_module(question):
    """Simple module detection based on keywords"""
    question_lower = question.lower()
    
    modules = {
        'inventory': ['inventory', 'stock', 'warehouse', 'product', 'barcode'],
        'accounting': ['accounting', 'invoice', 'payment', 'tax', 'financial'],
        'sales': ['sales', 'quote', 'customer', 'crm', 'lead'],
        'purchase': ['purchase', 'vendor', 'supplier', 'rfq'],
        'hr': ['hr', 'employee', 'payroll', 'recruitment', 'attendance'],
        'manufacturing': ['manufacturing', 'mrp', 'bom', 'production'],
        'project': ['project', 'task', 'timesheet'],
        'website': ['website', 'ecommerce', 'blog'],
        'configuration': ['settings', 'configuration', 'setup', 'company', 'multi-company'],
        'security': ['security', 'permission', 'access', 'group', 'user'],
        'development': ['module', 'model', 'field', 'view', 'controller', 'api']
    }
    
    for module, keywords in modules.items():
        if any(keyword in question_lower for keyword in keywords):
            return module.title()
    
    return "General"

def render_message(message, is_user=True):
    """Render a single message bubble"""
    if is_user:
        return f"""
        <div class="message user">
            <div class="message-bubble user">
                {message['content']}
            </div>
            <div class="message-icon user">👤</div>
        </div>
        """
    else:
        # Check if this is a thinking message
        if message.get('thinking'):
            return show_typing_indicator()
        
        # Clean the content to remove any HTML artifacts while preserving meaningful content
        content = message['content']
        
        # Remove HTML artifacts that might be generated by AI
        import re
        # Remove complete HTML structure that might be in the AI response
        content = re.sub(r'<div[^>]*class="message[^"]*"[^>]*>.*?</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div[^>]*class="sources"[^>]*>.*?</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div[^>]*class="message-icon[^"]*"[^>]*>.*?</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div[^>]*class="message-bubble[^"]*"[^>]*>', '', content)  # Remove message bubble divs
        content = re.sub(r'<div[^>]*>', '', content)  # Remove any remaining opening div tags
        content = re.sub(r'</div>', '', content)     # Remove closing div tags
        content = re.sub(r'<a[^>]*href[^>]*>.*?</a>', '', content)  # Remove link artifacts
        
        # Clean up any HTML entities or fragments
        content = content.replace('&lt;', '').replace('&gt;', '').replace('&amp;', '&')
        content = content.replace('class="', '').replace('">', '')
        
        # Clean up extra whitespace and newlines
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Escape HTML characters for safe display
        import html
        content = html.escape(content)
        
        sources_html = ""
        
        # Add sources if available
        if 'sources' in message and message['sources']:
            sources_html = '<div class="sources">📚 Sources: '
            for i, source in enumerate(message['sources'][:3]):
                sources_html += f'<a href="{source["url"]}" target="_blank" class="source-link">{source["title"]}</a>'
            sources_html += '</div>'
        
        return f"""
        <div class="message ai">
            <div class="message-icon ai">🤖</div>
            <div class="message-bubble ai">
                {content}
                {sources_html}
            </div>
        </div>
        """

def show_typing_indicator():
    """Show typing indicator"""
    return """
    <div class="message ai">
        <div class="message-icon ai">🤖</div>
        <div class="message-bubble ai">
            <div class="typing">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <span style="margin-left: 8px;">AI is thinking...</span>
            </div>
        </div>
    </div>
    """

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

if "selected_history" not in st.session_state:
    st.session_state.selected_history = None

if "sidebar_hidden" not in st.session_state:
    st.session_state.sidebar_hidden = False

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# Sidebar
with st.sidebar:
    st.markdown("# 🚀 Odoo 18.0 Certification Assistant")
    
    # System Information
    st.markdown("""
    <div class="system-info">
        <h3>📊 System Information</h3>
        <p><strong>6,465</strong> document chunks</p>
        <p><strong>1,364</strong> Odoo documentation URLs</p>
        <p><strong>Gemini 2.5 Flash</strong> powered</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Settings
    st.markdown("### ⚙️ Settings")
    certification_mode = st.checkbox("🎓 Certification Mode", value=True, 
                                   help="Optimized for fast exam responses")
    
    # Question History
    st.markdown("### 📝 Question History")
    
    # Extract questions from chat history
    questions = []
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            # Find the corresponding AI response
            ai_response = None
            if i + 1 < len(st.session_state.messages):
                ai_response = st.session_state.messages[i + 1]
            
            module = detect_module(msg["content"])
            questions.append({
                'question': msg["content"],
                'module': module,
                'timestamp': msg.get('timestamp', 'Unknown'),
                'answer': ai_response['content'] if ai_response else "No response",
                'sources': ai_response.get('sources', []) if ai_response else []
            })
    
    if questions:
        for i, q in enumerate(questions):
            if st.button(f"Question {i+1} - {q['module']}", 
                        key=f"hist_{i}", 
                        help=f"Click to view: {q['question'][:50]}...",
                        use_container_width=True):
                st.session_state.selected_history = q
    else:
        st.markdown("*No questions asked yet*")
    
    # Clear history
    if st.button("🗑️ Clear History", type="secondary"):
        st.session_state.messages = []
        st.session_state.selected_history = None
        save_chat_history([])
        st.rerun()

# Main chat title with manual sidebar toggle as backup
col_title, col_sidebar = st.columns([10, 1])
with col_title:
    st.markdown("## 💬 Chat with your Odoo Assistant")
with col_sidebar:
    # Clear Streamlit's localStorage to force sidebar to show
    st.markdown("""
    <button onclick="
        // Clear Streamlit's sidebar state from localStorage
        Object.keys(localStorage).forEach(key => {
            if (key.includes('sidebar') || key.includes('Sidebar')) {
                localStorage.removeItem(key);
            }
        });
        // Also try sessionStorage
        Object.keys(sessionStorage).forEach(key => {
            if (key.includes('sidebar') || key.includes('Sidebar')) {
                sessionStorage.removeItem(key);
            }
        });
        // Force reload after clearing storage
        window.location.reload();
    " 
    style="background: #ff4b4b; color: white; border: none; border-radius: 6px; padding: 8px 12px; cursor: pointer; font-size: 16px;"
    title="Clear sidebar state and reload">
        📋 Show Sidebar
    </button>
    """, unsafe_allow_html=True)

# Add additional localStorage clearing method for debugging
st.markdown("""
<div style="text-align: center; margin: 10px 0;">
    <button onclick="
        // Nuclear option: Clear ALL localStorage and sessionStorage
        localStorage.clear();
        sessionStorage.clear();
        // Also clear specific Streamlit keys if they exist
        ['streamlit', 'stSidebar', 'sidebarState', 'sidebar_state', 'sidebar-state'].forEach(key => {
            localStorage.removeItem(key);
            sessionStorage.removeItem(key);
        });
        alert('Cleared all browser storage. Reloading...');
        window.location.reload();
    " 
    style="background: #8b5cf6; color: white; border: none; border-radius: 6px; padding: 8px 16px; cursor: pointer; font-size: 14px; margin: 5px;"
    title="Nuclear option: Clear all browser storage">
        🗑️ Clear All Browser Data
    </button>
</div>
""", unsafe_allow_html=True)

# Load RAG system
rag_system = load_rag_system()
if not rag_system:
    st.error("❌ RAG system not loaded. Please run the setup process first.")
    st.stop()

# Chat container
chat_placeholder = st.container()

with chat_placeholder:
    # Show selected history or live chat
    if st.session_state.selected_history:
        st.info("📖 Viewing question from history. Click 'Back to Live Chat' to continue chatting.")
        
        if st.button("⬅️ Back to Live Chat", type="secondary"):
            st.session_state.selected_history = None
            st.rerun()
        
        # Show the historical Q&A
        st.markdown(f"""
        <div class="chat-container">
            {render_message({'content': st.session_state.selected_history['question']}, is_user=True)}
            {render_message({
                'content': st.session_state.selected_history['answer'],
                'sources': st.session_state.selected_history['sources']
            }, is_user=False)}
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Live chat - no container frame, directly render messages
        if not st.session_state.messages:
            st.markdown("""
            <div style="text-align: center; padding: 100px 50px; color: #666;">
                <h2>👋 Welcome to your Odoo 18.0 Certification Assistant!</h2>
                <p>Ask me anything about Odoo 18.0 for your certification preparation.</p>
                <p><em>Example: "How do I create a custom module in Odoo?"</em></p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Create a full-height container without frame
            chat_html = '<div class="chat-container" id="chat-container">'
            for message in st.session_state.messages:
                if message["role"] == "user":
                    chat_html += render_message(message, is_user=True)
                elif message["role"] == "assistant":
                    chat_html += render_message(message, is_user=False)
            chat_html += '</div>'
            st.markdown(chat_html, unsafe_allow_html=True)

# Input area - positioned lower
st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
col1, col2 = st.columns([8, 1])

with col1:
    user_input = st.text_input(
        "Ask your question...", 
        key="user_input",
        placeholder="Type your Odoo question here...",
        label_visibility="collapsed",
        value=""  # Clear the input after each rerun
    )

with col2:
    send_button = st.button("↑", type="primary", help="Send message")

# Handle sending message
if send_button and user_input.strip():
    # Add user message
    user_message = {
        "role": "user",
        "content": user_input.strip(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.messages.append(user_message)
    
    # Add a temporary thinking message
    thinking_message = {
        "role": "assistant",
        "content": "thinking...",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "thinking": True
    }
    st.session_state.messages.append(thinking_message)
    
    # Clear input immediately
    st.session_state.input_text = ""
    if "user_input" in st.session_state:
        del st.session_state["user_input"]
    
    # Refresh to show user message and thinking indicator
    st.rerun()
    
# Handle AI response if there's a thinking message
if st.session_state.messages and st.session_state.messages[-1].get("thinking"):
    try:
        # Get the user's question (second to last message)
        user_question = st.session_state.messages[-2]["content"]
        
        # Get AI response
        result = rag_system.ask(
            user_question,
            top_k=5 if certification_mode else 3
        )
        
        # Replace thinking message with actual response
        st.session_state.messages[-1] = {
            "role": "assistant",
            "content": result['answer'],
            "sources": result.get('sources', []),
            "response_time": result.get('response_time', 0),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save history
        save_chat_history(st.session_state.messages)
        st.rerun()
        
    except Exception as e:
        # Remove thinking message and show error
        st.session_state.messages.pop()
        st.error(f"❌ Error getting response: {e}")

# Auto-scroll script
st.markdown("""
<script>
function scrollToBottom() {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}
setTimeout(scrollToBottom, 100);
</script>
""", unsafe_allow_html=True)

# JavaScript for Enter key
st.markdown("""
<script>
function setupEnterKey() {
    // Find the text input
    const inputs = document.querySelectorAll('input[type="text"]');
    const input = inputs[inputs.length - 1]; // Get the last one (our input)
    
    if (input && !input.hasAttribute('data-enter-setup')) {
        input.setAttribute('data-enter-setup', 'true');
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                // Find the send button
                const buttons = document.querySelectorAll('button');
                for(let btn of buttons) {
                    if(btn.textContent.includes('↑')) {
                        btn.click();
                        break;
                    }
                }
            }
        });
    }
}

// Setup immediately and on any DOM changes
setupEnterKey();
setInterval(setupEnterKey, 1000);
</script>
""", unsafe_allow_html=True)