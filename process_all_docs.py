"""
Process ALL 1,364 Odoo documentation URLs
This is the full dataset processing for complete certification coverage
"""

from data_processor import OdooDocProcessor
import time

def main():
    print("🚀 Processing ALL 1,364 Odoo Documentation URLs")
    print("=" * 60)
    print("⏱️  Estimated time: 30-45 minutes")
    print("📊 This will give you complete Odoo 18.0 certification coverage")
    print("")
    
    response = input("Continue? (y/N): ").lower().strip()
    if response != 'y':
        print("❌ Processing cancelled")
        return
    
    processor = OdooDocProcessor('odoo_docs_links.csv')
    
    print(f"\n📥 Starting full document processing...")
    start_time = time.time()
    
    # Process ALL documents (remove max_docs limit)
    processor.process_all_docs(max_docs=None, delay=1.5)  # 1.5s delay to be respectful
    processor.save_processed_docs()
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"\n✅ Complete! Processed in {processing_time:.1f} seconds ({processing_time/60:.1f} minutes)")
    print(f"📊 Total document chunks: {len(processor.processed_docs)}")
    print(f"\n🧠 Next step: Run 'python embedding_system.py' to generate embeddings")

if __name__ == "__main__":
    main()