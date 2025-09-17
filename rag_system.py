"""
RAG (Retrieval Augmented Generation) System for Odoo Documentation
Combines semantic search with Gemini 2.5 Pro for accurate Q&A
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from vector_database import VectorDatabase
from embedding_system import GeminiEmbeddingSystem

load_dotenv()

class OdooRAGSystem:
    def __init__(self, embeddings_path: str = "embeddings/odoo_embeddings.pkl"):
        # Initialize API
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        
        # Initialize components
        self.vector_db = VectorDatabase(embeddings_path)
        self.embedding_system = GeminiEmbeddingSystem()
        # Use Flash instead of Pro to avoid rate limits
        self.generator = genai.GenerativeModel('gemini-2.5-flash')
        
        # Load and build index
        self.vector_db.load_embeddings()
        self.vector_db.build_index()
        
        print("RAG System initialized successfully")
    
    def retrieve_relevant_docs(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve most relevant documents for a query"""
        # Generate query embedding with RETRIEVAL_QUERY task type
        query_embedding = self.embedding_system.generate_embedding(query, task_type="RETRIEVAL_QUERY")
        if not query_embedding:
            return []
        
        # Search for similar documents
        results = self.vector_db.search(query_embedding, top_k=top_k)
        return results
    
    def generate_answer(self, query: str, retrieved_docs: List[Dict]) -> str:
        """Generate answer using retrieved documents and Gemini 2.5 Pro"""
        if not retrieved_docs:
            return "I couldn't find relevant information in the Odoo documentation to answer your question."
        
        # Prepare context from retrieved documents
        context_parts = []
        for i, doc in enumerate(retrieved_docs):
            context_parts.append(f"Source {i+1} ({doc['path_slug']}):\n{doc['content']}\n")
        
        context = "\n".join(context_parts)
        
        # Create prompt optimized for fast, accurate certification answers
        prompt = f"""You are an Odoo 18.0 certification expert. Provide concise, confident answers for this certification question(s).

Question(s): {query}

Context from Odoo 18.0 Documentation:
{context}

Instructions:
1. Give the most accurate answer(s) based on the context
2. Be concise and direct - this is for a timed certification exam
3. If multiple questions are asked, format each answer on a separate line like:
   1. [Answer to question 1]
   2. [Answer to question 2]
   3. [Answer to question 3]
4. For multiple choice questions, clearly state the correct answer (e.g., "A" or "The correct answer is A")
5. Keep explanations minimal - focus on the correct answer only
6. If you cannot find an answer in the documentation context, start that specific answer with "⚠️ General knowledge: "
7. IMPORTANT: Provide ONLY plain text - no HTML tags, markup, or code snippets

Answer(s):"""

        try:
            response = self.generator.generate_content(prompt)
            answer = response.text
            
            # Check if the AI is indicating it doesn't know - if so, try general knowledge fallback
            if self._is_unknown_response(answer):
                answer = self._generate_fallback_answer(query)
                
            return answer
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _is_unknown_response(self, answer: str) -> bool:
        """Check if the AI response indicates it doesn't know the answer"""
        unknown_indicators = [
            "i don't know",
            "i couldn't find",
            "the provided documentation does not contain",
            "not available in the documentation",
            "no information",
            "cannot find",
            "unclear from the documentation"
        ]
        answer_lower = answer.lower()
        return any(indicator in answer_lower for indicator in unknown_indicators)
    
    def _generate_fallback_answer(self, query: str) -> str:
        """Generate a fallback answer using general Odoo knowledge when docs don't have the answer"""
        fallback_prompt = f"""You are an experienced Odoo consultant with deep knowledge of Odoo 18.0. 
The user asked question(s) that couldn't be answered from the official documentation. 
Provide the best possible answers based on your general Odoo knowledge and common practices.

Question(s): {query}

Instructions:
1. Be concise and direct - this is for a timed certification exam
2. If multiple questions are asked, format each answer on a separate line like:
   1. ⚠️ General knowledge: [Answer to question 1]
   2. ⚠️ General knowledge: [Answer to question 2]
   3. ⚠️ General knowledge: [Answer to question 3]
3. For multiple choice questions, clearly state the correct answer (e.g., "A" or "The correct answer is A")
4. Keep explanations minimal - focus on the correct answer only
5. Start each answer with "⚠️ General knowledge: " to indicate it's not from official docs

Provide helpful, practical answers based on:
- Common Odoo workflows and best practices
- Typical Odoo configurations 
- Standard business processes in Odoo
- Logical deductions about how Odoo likely works

Answer(s):"""
        
        try:
            response = self.generator.generate_content(fallback_prompt)
            return response.text
        except Exception as e:
            return f"⚠️ Based on general knowledge: I can provide an educated guess about '{query}', but I'd recommend checking the latest Odoo documentation or consulting with an Odoo expert for the most accurate information."
    
    def ask(self, query: str, top_k: int = 3, image_data: bytes = None) -> Dict:
        """Main method to ask a question and get RAG-powered answer"""
        print(f"Processing query: {query}")
        if image_data:
            print("📷 Image provided - using Gemini Vision")
        
        # If image is provided, use vision model directly
        if image_data:
            return self._ask_with_image(query, image_data)
        
        # Text-only query - use existing RAG pipeline
        # Retrieve relevant documents
        retrieved_docs = self.retrieve_relevant_docs(query, top_k)
        
        if not retrieved_docs:
            # No relevant docs found, use general knowledge fallback
            fallback_answer = self._generate_fallback_answer(query)
            return {
                "query": query,
                "answer": fallback_answer,
                "sources": [],
                "from_docs": False
            }
        
        # Generate answer
        answer = self.generate_answer(query, retrieved_docs)
        
        # Check if we used fallback (answer will contain the warning)
        from_docs = not self._is_unknown_response(answer)
        
        # Format sources - deduplicate by URL to avoid showing same page multiple times
        sources = []
        seen_urls = set()
        for doc in retrieved_docs:
            url = doc['url']
            if url not in seen_urls:
                seen_urls.add(url)
                sources.append({
                    "title": doc['filename'].replace('.html', ''),
                    "path": doc['path_slug'],
                    "url": url,
                    "similarity": doc['similarity'],
                    "preview": doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
                })
        
        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "retrieved_docs_count": len(retrieved_docs),
            "from_docs": from_docs
        }
    
    def _ask_with_image(self, query: str, image_data: bytes) -> Dict:
        """Handle image-based questions using Gemini Vision"""
        try:
            # Prepare image for Gemini
            import PIL.Image
            import io
            
            # Convert bytes to PIL Image
            image = PIL.Image.open(io.BytesIO(image_data))
            
            # Try to get relevant docs for the text part of the question
            retrieved_docs = self.retrieve_relevant_docs(query, top_k=3)
            
            # Create optimized prompt for certification questions with images
            vision_prompt = f"""You are an Odoo 18.0 certification expert. Provide concise, confident answers for this certification question(s).

Question(s): {query}

Instructions:
1. Give the most accurate answer(s) based on the image and question(s)
2. Be concise and direct - this is for a timed certification exam
3. If multiple questions are asked, format each answer on a separate line like:
   1. [Answer to question 1]
   2. [Answer to question 2]
   3. [Answer to question 3]
4. For multiple choice questions, clearly state the correct answer (e.g., "A" or "The correct answer is A")
5. Keep explanations minimal - focus on the correct answer only
6. IMPORTANT: Provide ONLY plain text - no HTML tags, markup, or code snippets

Answer(s):"""

            # Use Gemini Vision model
            response = self.generator.generate_content([vision_prompt, image])
            answer = response.text
            
            # Format sources if any were found
            sources = []
            if retrieved_docs:
                seen_urls = set()
                for doc in retrieved_docs:
                    url = doc['url']
                    if url not in seen_urls:
                        seen_urls.add(url)
                        sources.append({
                            "title": doc['filename'].replace('.html', ''),
                            "path": doc['path_slug'],
                            "url": url,
                            "similarity": doc['similarity'],
                            "preview": doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
                        })
            
            return {
                "query": query,
                "answer": answer,
                "sources": sources,
                "from_docs": len(sources) > 0,
                "image_analysis": True
            }
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return {
                "query": query,
                "answer": f"❌ Error analyzing image: {str(e)}",
                "sources": [],
                "from_docs": False,
                "image_analysis": True
            }
    
    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        db_stats = self.vector_db.get_stats()
        return {
            "vector_database": db_stats,
            "models": {
                "embedding_model": "text-embedding-004",
                "generation_model": "gemini-2.5-pro"
            }
        }

def main():
    """Test the RAG system with sample questions"""
    try:
        # Initialize RAG system
        rag = OdooRAGSystem()
        
        # Print system stats
        stats = rag.get_system_stats()
        print("System Statistics:")
        print(f"  Total document chunks: {stats['vector_database']['total_chunks']}")
        print(f"  Unique documents: {stats['vector_database']['unique_documents']}")
        
        # Test questions for Odoo certification
        test_questions = [
            "How do I create a new module in Odoo?",
            "What are the main components of an Odoo model?",
            "How do I configure email settings in Odoo?",
            "What is the difference between kanban and list views?",
            "How do I set up multi-company configuration?"
        ]
        
        print("\nTesting RAG system with sample questions:")
        for i, question in enumerate(test_questions[:2]):  # Test first 2 questions
            print(f"\n--- Question {i+1}: {question} ---")
            result = rag.ask(question)
            print(f"Answer: {result['answer'][:300]}...")
            print(f"Sources found: {len(result['sources'])}")
            if result['sources']:
                print(f"Top source: {result['sources'][0]['path']}")
    
    except Exception as e:
        print(f"Error testing RAG system: {str(e)}")

if __name__ == "__main__":
    main()