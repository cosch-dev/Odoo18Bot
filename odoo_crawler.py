#!/usr/bin/env python3
"""
Odoo Documentation Web Crawler

This script crawls the Odoo documentation starting from the applications page,
extracting all HTML links and saving them to a CSV file with their paths/slugs.
"""

import requests
import csv
import time
import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import deque
import os

class OdooCrawler:
    def __init__(self, start_url, output_file="odoo_docs_links.csv"):
        self.start_url = start_url
        self.output_file = output_file
        self.visited_urls = set()
        self.html_links = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def is_valid_url(self, url):
        """Check if URL is within the Odoo documentation domain and path"""
        parsed = urlparse(url)
        return (parsed.netloc == 'www.odoo.com' and 
                parsed.path.startswith('/documentation/18.0/applications/'))
    
    def extract_links_from_index(self, url, content):
        """Extract links from directory index pages"""
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        
        # Look for links in the directory listing
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            
            # Skip parent directory and other non-content links
            if href in ['../', '../', '/', '#']:
                continue
                
            full_url = urljoin(url, href)
            
            if self.is_valid_url(full_url):
                links.append({
                    'url': full_url,
                    'text': link.get_text().strip(),
                    'is_html': href.endswith('.html'),
                    'is_directory': href.endswith('/')
                })
        
        return links
    
    def get_path_slug(self, url):
        """Extract the path/slug from URL for CSV column"""
        parsed = urlparse(url)
        path = parsed.path.replace('/documentation/18.0/applications/', '')
        
        if path.endswith('.html'):
            return path[:-5]  # Remove .html extension
        elif path.endswith('/'):
            return path[:-1]  # Remove trailing slash
        else:
            return path
    
    def crawl_page(self, url):
        """Crawl a single page and extract information"""
        if url in self.visited_urls:
            return []
        
        print(f"Crawling: {url}")
        self.visited_urls.add(url)
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Add small delay to be respectful
            time.sleep(0.5)
            
            return self.extract_links_from_index(url, response.text)
            
        except requests.RequestException as e:
            print(f"Error crawling {url}: {e}")
            return []
    
    def crawl(self):
        """Main crawling function using BFS to explore all directories"""
        print(f"Starting crawl from: {self.start_url}")
        
        # Use BFS to explore all directories
        queue = deque([self.start_url])
        
        while queue:
            current_url = queue.popleft()
            links = self.crawl_page(current_url)
            
            for link_info in links:
                url = link_info['url']
                
                if link_info['is_html']:
                    # This is an HTML file - add to our results
                    slug = self.get_path_slug(url)
                    self.html_links.append({
                        'url': url,
                        'path_slug': slug,
                        'filename': link_info['text']
                    })
                    print(f"  Found HTML: {url} (slug: {slug})")
                
                elif link_info['is_directory']:
                    # This is a directory - add to queue for further exploration
                    if url not in self.visited_urls:
                        queue.append(url)
                        print(f"  Queued directory: {url}")
        
        print(f"\nCrawl completed. Found {len(self.html_links)} HTML files.")
    
    def save_to_csv(self):
        """Save the collected HTML links to CSV"""
        print(f"Saving results to {self.output_file}")
        
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'path_slug', 'filename']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for link in sorted(self.html_links, key=lambda x: x['path_slug']):
                writer.writerow(link)
        
        print(f"Saved {len(self.html_links)} HTML links to {self.output_file}")
    
    def run(self):
        """Run the complete crawling process"""
        try:
            self.crawl()
            self.save_to_csv()
            return True
        except KeyboardInterrupt:
            print("\nCrawling interrupted by user")
            if self.html_links:
                print(f"Saving {len(self.html_links)} links collected so far...")
                self.save_to_csv()
            return False
        except Exception as e:
            print(f"Error during crawling: {e}")
            return False

def main():
    start_url = "https://www.odoo.com/documentation/18.0/applications/"
    output_file = "odoo_docs_links.csv"
    
    crawler = OdooCrawler(start_url, output_file)
    success = crawler.run()
    
    if success:
        print(f"\n✅ Crawling completed successfully!")
        print(f"📄 Results saved to: {output_file}")
        
        # Show some statistics
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                line_count = sum(1 for line in f) - 1  # Subtract header
            print(f"📊 Total HTML files found: {line_count}")
    else:
        print(f"\n❌ Crawling completed with errors")

if __name__ == "__main__":
    main()