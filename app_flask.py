"""
Flask Chat Interface for Odoo 18.0 Certification RAG System
Clean, professional interface without Streamlit limitations
"""
from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from rag_system import OdooRAGSystem

app = Flask(__name__)

# Initialize RAG system
print("🚀 Initializing RAG system...")
try:
    rag_system = OdooRAGSystem()
    print("✅ RAG system loaded successfully!")
except Exception as e:
    print(f"❌ Error loading RAG system: {e}")
    rag_system = None

# Chat history is now handled client-side

def detect_module(question):
    """Detect which Odoo module the question relates to"""
    question_lower = question.lower()
    modules = {
        'accounting': ['accounting', 'invoice', 'payment', 'tax', 'fiscal', 'journal', 'reconciliation'],
        'sales': ['sales', 'quotation', 'order', 'customer', 'crm', 'lead', 'opportunity'],
        'inventory': ['inventory', 'stock', 'warehouse', 'product', 'location', 'picking', 'delivery'],
        'purchase': ['purchase', 'vendor', 'supplier', 'rfq', 'receipt'],
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

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with optional image support"""
    if not rag_system:
        return jsonify({
            'error': 'RAG system not available. Please check the setup.'
        }), 500
    
    # Check if this is multipart form data (with image)
    if request.content_type and 'multipart/form-data' in request.content_type:
        user_message = request.form.get('message', '').strip()
        image_file = request.files.get('image')
        
        image_data = None
        if image_file:
            image_data = image_file.read()
    else:
        # JSON data (text only)
        data = request.get_json()
        user_message = data.get('message', '').strip()
        image_data = None
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        # Get RAG response (with optional image) - no session storage
        result = rag_system.ask(user_message, image_data=image_data)
        
        return jsonify({
            'response': result['answer'],
            'sources': result.get('sources', []),
            'from_docs': result.get('from_docs', True),
            'image_analysis': result.get('image_analysis', False)
        })
        
    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({'error': f'Error processing message: {str(e)}'}), 500

# History endpoints removed - handled client-side

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    if not rag_system:
        return jsonify({'error': 'RAG system not available'}), 500
    
    try:
        stats = rag_system.get_system_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Odoo 18.0 Certification Chat Interface")
    port = int(os.getenv('PORT', 5000))
    print(f"📱 Access at: http://localhost:{port}")
    app.run(debug=False, host='0.0.0.0', port=port)