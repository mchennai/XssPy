#!/usr/bin/env python3

import os
import json
import time
import glob

def monitor_extraction_progress():
    """Monitor the progress of all extraction attempts"""
    print("=== MONITORING EXTRACTION PROGRESS ===")
    
    result_files = [
        'comprehensive_extraction_results.json',
        'manual_extraction_results.json', 
        'ghauri_extraction_results.json',
        'direct_sqlmap_results.json'
    ]
    
    total_successful = 0
    all_results = []
    
    while total_successful < 5:
        print(f"\n[{time.strftime('%H:%M:%S')}] Checking extraction progress...")
        
        current_successful = 0
        
        for result_file in result_files:
            if os.path.exists(result_file):
                try:
                    with open(result_file, 'r') as f:
                        data = json.load(f)
                        if data:
                            current_successful += len(data)
                            print(f"  [+] {result_file}: {len(data)} successful extractions")
                            
                            # Add to all results if not already added
                            for result in data:
                                if result not in all_results:
                                    all_results.append(result)
                except:
                    pass
            else:
                print(f"  [-] {result_file}: Not found yet")
        
        print(f"  [=] Total successful extractions: {current_successful}")
        
        if current_successful >= 5:
            print(f"\n[!] SUCCESS: Reached target of 5+ database extractions!")
            break
        elif current_successful > total_successful:
            total_successful = current_successful
            print(f"  [+] Progress: {total_successful}/5 extractions completed")
        
        time.sleep(30)  # Check every 30 seconds
    
    # Create final combined results
    with open('FINAL_DATABASE_EXTRACTIONS.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Create summary report
    create_final_extraction_report(all_results)
    
    return all_results

def create_final_extraction_report(results):
    """Create final extraction report"""
    with open('FINAL_EXTRACTION_REPORT.md', 'w') as f:
        f.write("# FINAL DATABASE EXTRACTION REPORT\n\n")
        f.write(f"## Summary\n")
        f.write(f"- **Total Successful Extractions**: {len(results)}\n")
        f.write(f"- **Target Achievement**: {'✅ COMPLETED' if len(results) >= 5 else '❌ IN PROGRESS'}\n\n")
        
        for i, result in enumerate(results, 1):
            f.write(f"## Extraction {i}: {result.get('url', 'Unknown URL')}\n\n")
            f.write(f"**Tool/Method**: {result.get('tool', result.get('method', 'Unknown'))}\n\n")
            
            if result.get('current_database'):
                f.write(f"**Current Database**: {result['current_database']}\n\n")
            
            if result.get('current_user'):
                f.write(f"**Current User**: {result['current_user']}\n\n")
            
            if result.get('hostname'):
                f.write(f"**Hostname**: {result['hostname']}\n\n")
            
            if result.get('databases'):
                f.write(f"**Databases Found ({len(result['databases'])})**:\n")
                for db in result['databases']:
                    f.write(f"- {db}\n")
                f.write("\n")
            
            if result.get('tables'):
                f.write(f"**Tables Found ({len(result['tables'])})**:\n")
                for table in result['tables'][:20]:  # Show first 20
                    f.write(f"- {table}\n")
                if len(result['tables']) > 20:
                    f.write(f"- ... and {len(result['tables']) - 20} more tables\n")
                f.write("\n")
            
            if result.get('columns'):
                f.write(f"**Columns Found ({len(result['columns'])})**:\n")
                for col in result['columns'][:20]:  # Show first 20
                    f.write(f"- {col}\n")
                if len(result['columns']) > 20:
                    f.write(f"- ... and {len(result['columns']) - 20} more columns\n")
                f.write("\n")
            
            if result.get('users'):
                f.write(f"**Database Users ({len(result['users'])})**:\n")
                for user in result['users']:
                    f.write(f"- {user}\n")
                f.write("\n")
            
            f.write("---\n\n")

if __name__ == "__main__":
    results = monitor_extraction_progress()
    
    print(f"\n=== MONITORING COMPLETE ===")
    print(f"Final results: {len(results)} successful database extractions")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('url', 'Unknown URL')}")
        print(f"   Tool: {result.get('tool', result.get('method', 'Unknown'))}")
        print(f"   Databases: {len(result.get('databases', []))}")
        print(f"   Tables: {len(result.get('tables', []))}")
        print(f"   Columns: {len(result.get('columns', []))}")
