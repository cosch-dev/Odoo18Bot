"""
Gemini Embeddings System for Odoo Documentation RAG
Generates embeddings for processed documents using Gemini API
"""

import os
import json
import numpy as np
import pickle
from typing import List, Dict, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from pathlib import Path
import time

load_dotenv()

class GeminiEmbeddingSystem:
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('models/text-embedding-004')
        self.embeddings_cache = {}
        
    def generate_embedding(self, text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
        """Generate embedding for a single text using Gemini"""
        try:
            # Use the embed_content function with the appropriate model
            response = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type=task_type
            )
            return response['embedding']
        
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            # Try with a simpler approach if the above fails
            try:
                response = genai.embed_content(
                    model="models/text-embedding-004",
                    content=text
                )
                return response['embedding']
            except Exception as e2:
                print(f"Fallback embedding also failed: {str(e2)}")
                return None
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 10, delay: float = 1.0) -> List[List[float]]:
        """Generate embeddings for multiple texts with rate limiting"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
            
            batch_embeddings = []
            for text in batch:
                embedding = self.generate_embedding(text)
                if embedding:
                    batch_embeddings.append(embedding)
                else:
                    # Use zero vector as fallback
                    batch_embeddings.append([0.0] * 768)  # Default embedding size
                
                time.sleep(delay)  # Rate limiting
            
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def process_documents(self, documents_path: str, output_path: str = "embeddings"):
        """Process documents and generate embeddings"""
        output_dir = Path(output_path)
        output_dir.mkdir(exist_ok=True)
        
        # Load processed documents
        with open(documents_path, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        print(f"Generating embeddings for {len(documents)} document chunks...")
        
        # Extract texts for embedding
        texts = [doc['content'] for doc in documents]
        
        # Generate embeddings
        embeddings = self.generate_embeddings_batch(texts, batch_size=5, delay=2.0)
        
        # Create embedding database
        embedding_db = {
            'documents': documents,
            'embeddings': embeddings,
            'embedding_dim': len(embeddings[0]) if embeddings else 0,
            'total_docs': len(documents)
        }
        
        # Save embeddings
        embeddings_file = output_dir / "odoo_embeddings.pkl"
        with open(embeddings_file, 'wb') as f:
            pickle.dump(embedding_db, f)
        
        # Save as JSON for inspection (without embeddings to keep file size manageable)
        metadata_file = output_dir / "embedding_metadata.json"
        metadata = {
            'total_documents': len(documents),
            'embedding_dimension': len(embeddings[0]) if embeddings else 0,
            'sample_document': documents[0] if documents else None
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"Embeddings saved to {embeddings_file}")
        print(f"Metadata saved to {metadata_file}")
        
        return embedding_db

def main():
    """Main function to generate embeddings"""
    embedding_system = GeminiEmbeddingSystem()
    
    # Check if processed documents exist
    docs_path = "processed_docs/processed_odoo_docs.json"
    if not Path(docs_path).exists():
        print(f"Processed documents not found at {docs_path}")
        print("Please run data_processor.py first")
        return
    
    # Generate embeddings
    embedding_db = embedding_system.process_documents(docs_path)
    print(f"Successfully generated embeddings for {embedding_db['total_docs']} documents")

if __name__ == "__main__":
    main()