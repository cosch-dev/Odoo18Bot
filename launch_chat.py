"""
Launch script for the improved Odoo chatbot
"""
import subprocess
import sys
import time

def main():
    print("🚀 Launching Improved Odoo 18.0 Certification Chat Interface")
    print("=" * 60)
    
    try:
        # Check if user wants demo data
        response = input("Add demo chat history for testing? (y/N): ").lower().strip()
        if response == 'y':
            subprocess.run([sys.executable, "demo_history.py"])
            time.sleep(1)
        
        # Kill any existing streamlit processes on port 8501
        subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
        time.sleep(2)
        
        print("🌐 Starting chat interface on http://localhost:8501")
        print("📝 New Features:")
        print("   - Modern chat UI (user right, AI left)")
        print("   - ALL questions shown in history (not just last 10)")
        print("   - Smart module detection: Question X - Module")
        print("   - Click history items to view past Q&A")
        print("   - Auto-scrolling chat and history")
        print("   - Fast certification mode")
        print("")
        
        # Launch the improved app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app_improved.py",
            "--server.headless", "true",
            "--server.port", "8501"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Chat interface stopped")
    except Exception as e:
        print(f"❌ Error launching interface: {e}")

if __name__ == "__main__":
    main()