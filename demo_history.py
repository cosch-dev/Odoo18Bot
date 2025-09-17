"""
Demo script to add sample history for testing the new interface
"""
import json
from datetime import datetime, timedelta

def create_demo_history():
    """Create sample chat history to demonstrate the new interface"""
    
    sample_questions = [
        {
            "user": "How do I create a new product in Odoo?",
            "assistant": "To create a new product in Odoo 18.0, go to Inventory > Products > Products and click Create...",
            "module": "Inventory"
        },
        {
            "user": "What are the steps to configure email settings?",
            "assistant": "To configure email settings in Odoo, navigate to Settings > General Settings > Discuss section...",
            "module": "Email"
        },
        {
            "user": "How do I set up security groups and access rights?",
            "assistant": "Security groups in Odoo are configured through Settings > Users & Companies > Groups...",
            "module": "Security"
        },
        {
            "user": "What is the difference between kanban and list views?",
            "assistant": "Kanban views display records as cards in columns, ideal for workflow visualization...",
            "module": "Development"
        },
        {
            "user": "How do I create a customer invoice?",
            "assistant": "To create a customer invoice, go to Accounting > Customers > Invoices and click Create...",
            "module": "Accounting"
        },
        {
            "user": "In a multi-company environment, how do you define whether a customer record is visible for all companies?",
            "assistant": "Leave the 'Company' field empty on the contact (Sales & Purchase Tab). When the Company field is empty, the contact is accessible to all companies in the database.",
            "module": "Configuration"
        }
    ]
    
    messages = []
    base_time = datetime.now() - timedelta(hours=2)
    
    for i, qa in enumerate(sample_questions):
        # User message
        user_time = base_time + timedelta(minutes=i*15)
        messages.append({
            "role": "user",
            "content": qa["user"],
            "timestamp": user_time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Assistant message
        assistant_time = user_time + timedelta(seconds=30)
        messages.append({
            "role": "assistant", 
            "content": qa["assistant"],
            "sources": [
                {
                    "title": f"{qa['module']} Documentation",
                    "path": f"applications/{qa['module'].lower()}",
                    "url": f"https://www.odoo.com/documentation/18.0/applications/{qa['module'].lower()}.html",
                    "similarity": 0.85 + (i * 0.02),
                    "preview": f"Documentation excerpt about {qa['module'].lower()} functionality..."
                }
            ],
            "response_time": 25.5 + (i * 2),
            "timestamp": assistant_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Save to chat history
    with open("chat_history.json", "w") as f:
        json.dump(messages, f, indent=2)
    
    print("✅ Demo chat history created!")
    print(f"📊 Added {len(sample_questions)} sample Q&A pairs")
    print("🔄 The improved interface will show:")
    for i, qa in enumerate(sample_questions):
        print(f"   - Question {i+1} - {qa['module']}")
    print("\n🚀 Launch app_improved.py to see the new interface!")

if __name__ == "__main__":
    create_demo_history()