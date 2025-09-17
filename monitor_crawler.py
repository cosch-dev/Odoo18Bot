#!/usr/bin/env python3
"""
Monitor the progress of the Odoo crawler
"""
import os
import time

def monitor_progress():
    log_file = "crawler_output.log"
    
    if not os.path.exists(log_file):
        print("Crawler output log not found!")
        return
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        html_count = len([line for line in lines if "Found HTML:" in line])
        directory_count = len([line for line in lines if "Queued directory:" in line])
        crawled_count = len([line for line in lines if "Crawling:" in line])
        
        print(f"📊 Crawler Progress Report:")
        print(f"   • HTML files found: {html_count}")
        print(f"   • Directories queued: {directory_count}")
        print(f"   • Pages crawled: {crawled_count}")
        
        # Show last few entries
        print(f"\n📋 Recent activity:")
        recent_lines = [line.strip() for line in lines[-10:] if line.strip()]
        for line in recent_lines:
            if "Found HTML:" in line:
                print(f"   ✅ {line}")
            elif "Crawling:" in line:
                print(f"   🔍 {line}")
            elif "Queued directory:" in line:
                print(f"   📁 {line}")
        
        # Check if CSV exists
        if os.path.exists("odoo_docs_links.csv"):
            print(f"\n✅ CSV file generated: odoo_docs_links.csv")
        else:
            print(f"\n⏳ Still crawling... CSV will be generated when complete")
            
    except Exception as e:
        print(f"Error reading log file: {e}")

if __name__ == "__main__":
    monitor_progress()