"""
Test script for the Odoo RAG system
Quick verification that all components work together
"""

from pathlib import Path
from rag_system import OdooRAGSystem

def test_system():
    print("🧪 Testing Odoo RAG System")
    print("=" * 40)
    
    # Check if embeddings exist
    embeddings_path = "embeddings/odoo_embeddings.pkl"
    if not Path(embeddings_path).exists():
        print("❌ Embeddings file not found!")
        print(f"Please run: python embedding_system.py")
        return False
    
    try:
        # Initialize RAG system
        print("🔄 Initializing RAG system...")
        rag = OdooRAGSystem(embeddings_path)
        
        # Get system stats
        stats = rag.get_system_stats()
        print(f"✅ Loaded {stats['vector_database']['total_chunks']} document chunks")
        print(f"✅ {stats['vector_database']['unique_documents']} unique documents")
        print(f"✅ {stats['vector_database']['embedding_dimension']}D embeddings")
        
        # Test questions
        test_questions = [
            "How do I create a new module in Odoo?",
            "What are the components of an Odoo model?"
        ]
        
        print("\n🔍 Testing with sample questions:")
        for i, question in enumerate(test_questions, 1):
            print(f"\n--- Test {i}: {question} ---")
            result = rag.ask(question, top_k=3)
            
            print(f"✅ Answer generated ({len(result['answer'])} characters)")
            print(f"✅ Found {len(result['sources'])} relevant sources")
            
            if result['sources']:
                top_source = result['sources'][0]
                print(f"📄 Top source: {top_source['title']} (similarity: {top_source['similarity']:.3f})")
            
            # Show first 200 chars of answer
            print(f"💬 Answer preview: {result['answer'][:200]}...")
        
        print(f"\n🎉 RAG system test completed successfully!")
        print(f"🌐 Run 'streamlit run app.py' to start the web interface")
        return True
        
    except Exception as e:
        print(f"❌ Error testing system: {str(e)}")
        return False

if __name__ == "__main__":
    test_system()