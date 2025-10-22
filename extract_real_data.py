#!/usr/bin/env python3

import json
import re

def extract_meaningful_data():
    """Extract meaningful database information from results"""
    
    # Read the manual extraction results
    with open('manual_extraction_results.json', 'r') as f:
        data = json.load(f)
    
    meaningful_results = []
    
    for result in data:
        url = result.get('url', 'Unknown')
        databases = result.get('databases', [])
        tables = result.get('tables', [])
        columns = result.get('columns', [])
        
        # Filter for meaningful database names (common patterns)
        real_databases = []
        real_tables = []
        real_columns = []
        
        # Common database name patterns
        db_patterns = ['mysql', 'information_schema', 'test', 'main', 'postgres', 'master', 'sys', 'admin', 'user', 'app', 'web', 'db', 'data', 'prod', 'dev']
        
        for db in databases:
            if any(pattern in db.lower() for pattern in db_patterns) or len(db) < 20:
                real_databases.append(db)
        
        # Common table name patterns  
        table_patterns = ['user', 'admin', 'account', 'profile', 'session', 'log', 'config', 'setting', 'product', 'order', 'payment', 'transaction', 'customer', 'employee']
        
        for table in tables:
            if any(pattern in table.lower() for pattern in table_patterns) or len(table) < 15:
                real_tables.append(table)
        
        # Common column name patterns
        column_patterns = ['id', 'name', 'email', 'password', 'user', 'admin', 'date', 'time', 'status', 'type', 'value', 'data', 'key', 'token']
        
        for column in columns:
            if any(pattern in column.lower() for pattern in column_patterns) or len(column) < 15:
                real_columns.append(column)
        
        if real_databases or real_tables or real_columns:
            meaningful_results.append({
                'url': url,
                'databases': real_databases[:20],  # Top 20
                'tables': real_tables[:20],        # Top 20  
                'columns': real_columns[:20]       # Top 20
            })
    
    return meaningful_results

def main():
    results = extract_meaningful_data()
    
    print("=== EXTRACTED DATABASE INFORMATION ===\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. URL: {result['url']}")
        
        if result['databases']:
            print(f"   DATABASES ({len(result['databases'])}): {', '.join(result['databases'])}")
        
        if result['tables']:
            print(f"   TABLES ({len(result['tables'])}): {', '.join(result['tables'])}")
            
        if result['columns']:
            print(f"   COLUMNS ({len(result['columns'])}): {', '.join(result['columns'])}")
        
        print()
    
    # Save meaningful results
    with open('meaningful_extracted_data.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Saved meaningful data to: meaningful_extracted_data.json")

if __name__ == "__main__":
    main()
