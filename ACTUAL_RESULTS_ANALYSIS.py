#!/usr/bin/env python3

import json
import os

def analyze_actual_results():
    """Analyze the actual extraction results"""
    print("=== ACTUAL RESULTS ANALYSIS ===")
    
    # Check manual extraction results
    if os.path.exists('manual_extraction_results.json'):
        with open('manual_extraction_results.json', 'r') as f:
            manual_data = json.load(f)
        
        print(f"\nManual Extraction Results: {len(manual_data)} entries")
        
        for i, result in enumerate(manual_data, 1):
            print(f"\n{i}. URL: {result.get('url', 'Unknown')}")
            print(f"   Method: {result.get('method', 'Unknown')}")
            print(f"   Databases: {len(result.get('databases', []))} found")
            print(f"   Tables: {len(result.get('tables', []))} found")
            print(f"   Columns: {len(result.get('columns', []))} found")
            
            # Check if these are actually meaningful results
            databases = result.get('databases', [])
            if databases:
                print(f"   Sample databases: {databases[:3]}")
                # Check if these look like real database names or just extracted text
                real_db_patterns = ['mysql', 'information_schema', 'test', 'main', 'postgres', 'master']
                real_dbs = [db for db in databases if any(pattern in db.lower() for pattern in real_db_patterns)]
                print(f"   Likely real databases: {len(real_dbs)} - {real_dbs[:3]}")
    
    # Check other result files
    result_files = [
        'expanded_scan_results.json',
        'detailed_results.json',
        'direct_sqlmap_results.json'
    ]
    
    for file in result_files:
        if os.path.exists(file):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                print(f"\n{file}: {len(data) if isinstance(data, list) else 'Object'} entries")
            except:
                print(f"\n{file}: Error reading file")

if __name__ == "__main__":
    analyze_actual_results()
