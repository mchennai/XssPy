#!/usr/bin/env python3
"""
Reality Test - What actually happens when testing major platforms
"""

import requests
import sys

def test_basic_xss(url, param_name="q"):
    """Test basic XSS payload on a URL"""
    payload = '<script>alert("XSS")</script>'
    
    print(f"\n[*] Testing: {url}")
    print(f"[*] Parameter: {param_name}")
    print(f"[*] Payload: {payload}")
    
    try:
        response = requests.get(url, params={param_name: payload}, timeout=10)
        
        print(f"[*] Status Code: {response.status_code}")
        print(f"[*] Response Headers:")
        
        # Check security headers
        security_headers = [
            'X-XSS-Protection',
            'Content-Security-Policy', 
            'X-Content-Type-Options',
            'X-Frame-Options',
            'Strict-Transport-Security'
        ]
        
        for header in security_headers:
            if header in response.headers:
                value = response.headers[header]
                if len(value) > 100:
                    value = value[:100] + "..."
                print(f"    {header}: {value}")
        
        # Check if payload is reflected
        if payload in response.text:
            print(f"[!] Payload reflected in response!")
            print(f"[!] But this doesn't mean it's exploitable...")
        else:
            print(f"[*] Payload NOT reflected (filtered/blocked)")
            
        # Check for WAF indicators
        waf_indicators = [
            "cloudflare",
            "access denied", 
            "blocked",
            "security",
            "firewall",
            "403 forbidden"
        ]
        
        response_lower = response.text.lower()
        for indicator in waf_indicators:
            if indicator in response_lower:
                print(f"[!] WAF detected: {indicator}")
                break
                
    except requests.exceptions.RequestException as e:
        print(f"[!] Request failed: {str(e)}")

def main():
    print("Reality Test - Major Platform Security")
    print("=" * 50)
    
    # Test some major platforms (these are public URLs, not exploitation)
    test_urls = [
        ("https://www.google.com/search", "q"),
        ("https://duckduckgo.com/", "q"),
        ("https://github.com/search", "q"),
    ]
    
    for url, param in test_urls:
        test_basic_xss(url, param)
        print("-" * 50)
    
    print("\n[*] REALITY CHECK COMPLETE")
    print("\nWhat you'll typically see:")
    print("- Security headers present")
    print("- Payloads filtered or blocked")
    print("- WAF protection active")
    print("- No actual XSS vulnerabilities")
    print("\nMajor platforms invest heavily in security!")

if __name__ == "__main__":
    main()