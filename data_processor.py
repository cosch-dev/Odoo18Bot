"""
Odoo Documentation Data Processor
Fetches and processes Odoo documentation from CSV links for RAG system
"""

import os
import csv
import requests
import time
import json
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class OdooDocProcessor:
    def __init__(self, csv_path: str, output_dir: str = "processed_docs"):
        self.csv_path = csv_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.processed_docs = []
        
    def load_urls(self) -> List[Dict[str, str]]:
        """Load URLs from CSV file"""
        urls = []
        with open(self.csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                urls.append({
                    'url': row['url'],
                    'path_slug': row['path_slug'],
                    'filename': row['filename']
                })
        return urls
    
    def fetch_page_content(self, url: str) -> Optional[str]:
        """Fetch and extract text content from a webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Find main content - Odoo docs typically use specific classes
            main_content = soup.find('main') or soup.find('div', class_='content') or soup.find('article')
            if main_content:
                text = main_content.get_text()
            else:
                text = soup.get_text()
            
            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                search_start = max(start, end - 100)
                sentence_end = text.rfind('.', search_start, end)
                if sentence_end != -1 and sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap
        
        return chunks
    
    def process_all_docs(self, max_docs: Optional[int] = None, delay: float = 1.0):
        """Process all documentation URLs"""
        urls = self.load_urls()
        
        if max_docs:
            urls = urls[:max_docs]
        
        print(f"Processing {len(urls)} documents...")
        
        for i, doc_info in enumerate(urls):
            print(f"Processing {i+1}/{len(urls)}: {doc_info['path_slug']}")
            
            content = self.fetch_page_content(doc_info['url'])
            if content and len(content.strip()) > 100:  # Skip very short content
                chunks = self.chunk_text(content)
                
                for j, chunk in enumerate(chunks):
                    self.processed_docs.append({
                        'url': doc_info['url'],
                        'path_slug': doc_info['path_slug'],
                        'filename': doc_info['filename'],
                        'chunk_id': f"{doc_info['path_slug']}_chunk_{j}",
                        'content': chunk,
                        'chunk_index': j,
                        'total_chunks': len(chunks)
                    })
            
            # Rate limiting
            time.sleep(delay)
        
        print(f"Processed {len(self.processed_docs)} document chunks")
    
    def save_processed_docs(self, filename: str = "processed_odoo_docs.json"):
        """Save processed documents to JSON file"""
        output_path = self.output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.processed_docs, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(self.processed_docs)} chunks to {output_path}")
        
        # Also save as CSV for easier inspection
        csv_path = self.output_dir / filename.replace('.json', '.csv')
        df = pd.DataFrame(self.processed_docs)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"Also saved as CSV to {csv_path}")

def main():
    """Main function to run document processing"""
    processor = OdooDocProcessor('odoo_docs_links.csv')
    
    # Process first 50 docs for testing (remove limit for full processing)
    processor.process_all_docs(max_docs=50, delay=1.0)
    processor.save_processed_docs()

if __name__ == "__main__":
    main()