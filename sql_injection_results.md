# SQL Injection Testing Results

## Domains Tested
- acorns.com
- gohenry.com  
- pixpay.fr
- graphql.acorns.com

## Subdomains Discovered
Total subdomains found: 835

### Key API Endpoints Identified:
1. **Acorns.com APIs:**
   - https://api.acorns.com [302] - Live endpoint with Ruby on Rails
   - https://api-mobile.acorns.com [302] - Mobile API endpoint  
   - https://api-app.acorns.com [302] - App API endpoint
   - https://graphql.acorns.com [404] - GraphQL endpoint (Envoy)
   - https://mobile-api.acorns.com [503] - Service temporarily unavailable
   - https://partner-api.acorns.com [503] - Service temporarily unavailable
   - https://client-api.acorns.com [403] - Access forbidden
   - https://shipmunk-api.acorns.com [403] - Access forbidden

2. **GoHenry.com APIs:**
   - https://api-uk.gohenry.com [403] - Behind Cloudflare protection
   - https://api-us.gohenry.com [403] - Behind Cloudflare protection

3. **Pixpay.fr:**
   - https://murder.pixpay.fr [302] - Laravel application with login redirect
   - https://www.pixpay.fr [200] - Main website

## Live URLs with Potential SQL Injection Vectors

### High Priority Targets:
1. **https://api.acorns.com** - Ruby on Rails API (302 redirect)
2. **https://api-mobile.acorns.com** - Mobile API (302 redirect) 
3. **https://api-app.acorns.com** - App API (302 redirect)
4. **https://murder.pixpay.fr** - Laravel app with login (302 redirect)

### Medium Priority Targets:
1. **https://graphql.acorns.com** - GraphQL endpoint (404 but Envoy detected)
2. **https://mobile-api.acorns.com** - 503 error but potentially vulnerable
3. **https://partner-api.acorns.com** - 503 error but potentially vulnerable

## SQL Injection Testing Status

### Testing Challenges:
- Many endpoints are behind Cloudflare protection
- API endpoints require authentication
- Rate limiting and timeouts during testing
- Most endpoints return 403/404 without parameters

### Recommended Next Steps:
1. **Parameter Discovery**: Use tools like Arjun or ParamMiner to find hidden parameters
2. **Authentication Bypass**: Test for authentication bypass vulnerabilities
3. **GraphQL Testing**: Focus on GraphQL introspection and injection
4. **POST Request Testing**: Test POST endpoints with JSON payloads
5. **Header Injection**: Test for SQL injection in HTTP headers

### Security Observations:
- Most production APIs are well-protected
- Cloudflare WAF is blocking many requests
- Development/staging endpoints may be more vulnerable
- GraphQL endpoint may allow introspection queries

## Potential Vulnerabilities Found:
**Note**: Due to testing limitations and security controls, no confirmed SQL injection vulnerabilities were identified during this automated scan. Manual testing with proper authentication and parameter discovery would be required for thorough assessment.

### Recommended Manual Testing:
1. Test GraphQL introspection: `{__schema{types{name}}}`
2. Test API endpoints with valid authentication tokens
3. Fuzz parameters on 302 redirect endpoints
4. Test Laravel application for common SQL injection points
5. Use Burp Suite for comprehensive parameter discovery and testing