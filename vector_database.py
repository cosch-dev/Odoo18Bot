"""
Vector Database for Semantic Search using FAISS
Handles storage and retrieval of document embeddings
"""

import pickle
import numpy as np
import faiss
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import json

class VectorDatabase:
    def __init__(self, embeddings_path: str = "embeddings/odoo_embeddings.pkl"):
        self.embeddings_path = embeddings_path
        self.index = None
        self.documents = []
        self.embeddings = []
        self.dimension = 0
        
    def load_embeddings(self):
        """Load embeddings from pickle file"""
        if not Path(self.embeddings_path).exists():
            raise FileNotFoundError(f"Embeddings file not found: {self.embeddings_path}")
        
        with open(self.embeddings_path, 'rb') as f:
            data = pickle.load(f)
        
        self.documents = data['documents']
        self.embeddings = np.array(data['embeddings'], dtype=np.float32)
        self.dimension = data['embedding_dim']
        
        print(f"Loaded {len(self.documents)} documents with {self.dimension}D embeddings")
    
    def build_index(self):
        """Build FAISS index for fast similarity search"""
        if len(self.embeddings) == 0:
            raise ValueError("No embeddings loaded. Call load_embeddings() first.")
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(self.embeddings)
        
        # Create FAISS index - using Inner Product for normalized vectors (cosine similarity)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(self.embeddings)
        
        print(f"Built FAISS index with {self.index.ntotal} vectors")
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """Search for similar documents using query embedding"""
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Convert query to numpy array and normalize
        query_vector = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query_vector)
        
        # Search
        similarities, indices = self.index.search(query_vector, top_k)
        
        # Format results
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if idx < len(self.documents):  # Valid index
                doc = self.documents[idx].copy()
                doc['similarity'] = float(similarity)
                doc['rank'] = i + 1
                results.append(doc)
        
        return results
    
    def get_document_by_id(self, chunk_id: str) -> Optional[Dict]:
        """Get a specific document by its chunk ID"""
        for doc in self.documents:
            if doc.get('chunk_id') == chunk_id:
                return doc
        return None
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        if not self.documents:
            return {"error": "No documents loaded"}
        
        # Count unique documents
        unique_paths = set(doc['path_slug'] for doc in self.documents)
        
        # Calculate chunk statistics
        chunks_per_doc = {}
        for doc in self.documents:
            path = doc['path_slug']
            chunks_per_doc[path] = chunks_per_doc.get(path, 0) + 1
        
        return {
            "total_chunks": len(self.documents),
            "unique_documents": len(unique_paths),
            "embedding_dimension": self.dimension,
            "average_chunks_per_doc": np.mean(list(chunks_per_doc.values())),
            "max_chunks_per_doc": max(chunks_per_doc.values()) if chunks_per_doc else 0,
            "sample_paths": list(unique_paths)[:5]
        }

def main():
    """Test the vector database functionality"""
    try:
        # Initialize and load
        db = VectorDatabase()
        db.load_embeddings()
        db.build_index()
        
        # Print statistics
        stats = db.get_stats()
        print("Database Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Test search with a sample embedding (first document's embedding)
        if len(db.embeddings) > 0:
            sample_embedding = db.embeddings[0].tolist()
            results = db.search(sample_embedding, top_k=3)
            
            print(f"\nSample search results:")
            for result in results:
                print(f"  Rank {result['rank']}: {result['path_slug']} (similarity: {result['similarity']:.4f})")
                print(f"    Content preview: {result['content'][:100]}...")
        
    except Exception as e:
        print(f"Error testing vector database: {str(e)}")

if __name__ == "__main__":
    main()