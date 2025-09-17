#!/usr/bin/env python3
"""
Generate a preview CSV from the current crawler output
"""
import csv
import re

def generate_preview():
    log_file = "crawler_output.log"
    output_file = "preview_odoo_docs.csv"
    
    html_links = []
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                if "Found HTML:" in line:
                    # Extract URL and slug from log line
                    # Format: "  Found HTML: URL (slug: SLUG)"
                    match = re.search(r'Found HTML: (https://[^\s]+) \(slug: ([^)]+)\)', line)
                    if match:
                        url = match.group(1)
                        slug = match.group(2)
                        filename = url.split('/')[-1]
                        
                        html_links.append({
                            'url': url,
                            'path_slug': slug,
                            'filename': filename
                        })
        
        # Write preview CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'path_slug', 'filename']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for link in sorted(html_links, key=lambda x: x['path_slug']):
                writer.writerow(link)
        
        print(f"✅ Preview CSV generated: {output_file}")
        print(f"📊 Contains {len(html_links)} HTML files so far")
        
        # Show first 10 entries as sample
        print(f"\n📋 Sample entries:")
        for i, link in enumerate(sorted(html_links, key=lambda x: x['path_slug'])[:10]):
            print(f"   {i+1}. {link['path_slug']} -> {link['url']}")
        
        if len(html_links) > 10:
            print(f"   ... and {len(html_links) - 10} more")
            
    except Exception as e:
        print(f"Error generating preview: {e}")

if __name__ == "__main__":
    generate_preview()