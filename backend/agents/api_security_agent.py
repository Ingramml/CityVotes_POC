"""
API Security Agent - Expert on API routes, security vulnerabilities, and best practices

This agent provides security analysis, vulnerability detection, and recommendations
for protecting API endpoints against common attack vectors.
"""
from typing import Dict, List, Any, Optional
import re
import json


class APISecurityAgent:
    """
    Expert agent for API route security analysis and vulnerability detection.

    Capabilities:
    - Analyze API routes for security vulnerabilities
    - Detect common attack vectors (OWASP Top 10)
    - Validate input sanitization
    - Check authentication/authorization patterns
    - Recommend security improvements
    """

    def __init__(self):
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.security_headers = self._get_required_security_headers()

    def _load_vulnerability_patterns(self) -> Dict[str, Dict]:
        """Load patterns for detecting common vulnerabilities"""
        return {
            'sql_injection': {
                'name': 'SQL Injection',
                'severity': 'CRITICAL',
                'owasp': 'A03:2021',
                'patterns': [
                    r'execute\s*\(\s*["\'].*\+',  # String concatenation in SQL
                    r'cursor\.execute\s*\(\s*f["\']',  # f-string in SQL
                    r'\.format\s*\(.*\)\s*\)',  # .format() in SQL context
                ],
                'recommendation': 'Use parameterized queries or ORM methods. Never concatenate user input into SQL.'
            },
            'xss': {
                'name': 'Cross-Site Scripting (XSS)',
                'severity': 'HIGH',
                'owasp': 'A03:2021',
                'patterns': [
                    r'innerHTML\s*=',
                    r'document\.write\s*\(',
                    r'eval\s*\(',
                ],
                'recommendation': 'Sanitize and escape all user input before rendering. Use Content-Security-Policy headers.'
            },
            'path_traversal': {
                'name': 'Path Traversal',
                'severity': 'HIGH',
                'owasp': 'A01:2021',
                'patterns': [
                    r'open\s*\(\s*.*\+',  # String concat in file paths
                    r'os\.path\.join.*request',  # User input in file paths
                ],
                'recommendation': 'Validate and sanitize file paths. Use allowlists for accessible directories.'
            },
            'insecure_deserialization': {
                'name': 'Insecure Deserialization',
                'severity': 'CRITICAL',
                'owasp': 'A08:2021',
                'patterns': [
                    r'pickle\.loads?\s*\(',
                    r'yaml\.load\s*\([^,)]+\)',  # yaml.load without Loader
                ],
                'recommendation': 'Use JSON for serialization. If pickle is required, only deserialize trusted data.'
            },
            'hardcoded_secrets': {
                'name': 'Hardcoded Secrets',
                'severity': 'HIGH',
                'owasp': 'A02:2021',
                'patterns': [
                    r'password\s*=\s*["\'][^"\']+["\']',
                    r'api_key\s*=\s*["\'][^"\']+["\']',
                    r'secret\s*=\s*["\'][^"\']+["\']',
                    r'token\s*=\s*["\'][a-zA-Z0-9]{20,}["\']',
                ],
                'recommendation': 'Store secrets in environment variables or a secrets manager. Never commit secrets to code.'
            },
            'missing_auth': {
                'name': 'Missing Authentication',
                'severity': 'CRITICAL',
                'owasp': 'A07:2021',
                'indicators': ['No auth decorator', 'No token validation', 'Public endpoint with sensitive data'],
                'recommendation': 'Implement authentication for all sensitive endpoints. Use JWT or OAuth2.'
            },
            'mass_assignment': {
                'name': 'Mass Assignment',
                'severity': 'MEDIUM',
                'owasp': 'A04:2021',
                'patterns': [
                    r'\*\*request\.json',
                    r'\*\*data',
                ],
                'recommendation': 'Explicitly define allowed fields. Use Pydantic models for input validation.'
            },
            'ssrf': {
                'name': 'Server-Side Request Forgery',
                'severity': 'HIGH',
                'owasp': 'A10:2021',
                'patterns': [
                    r'requests\.(get|post|put|delete)\s*\(\s*.*\+',
                    r'urllib\..*open\s*\(\s*.*\+',
                ],
                'recommendation': 'Validate and allowlist URLs. Block internal/private IP ranges.'
            }
        }

    def _get_required_security_headers(self) -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }

    def analyze_route(self, route_code: str, route_path: str) -> Dict[str, Any]:
        """
        Analyze a single API route for security vulnerabilities.

        Args:
            route_code: The source code of the route handler
            route_path: The URL path of the route (e.g., "/api/users/{id}")

        Returns:
            Analysis results with findings and recommendations
        """
        findings = []

        # Check for vulnerability patterns
        for vuln_type, vuln_info in self.vulnerability_patterns.items():
            if 'patterns' in vuln_info:
                for pattern in vuln_info['patterns']:
                    if re.search(pattern, route_code, re.IGNORECASE):
                        findings.append({
                            'type': vuln_type,
                            'name': vuln_info['name'],
                            'severity': vuln_info['severity'],
                            'owasp': vuln_info.get('owasp', 'N/A'),
                            'recommendation': vuln_info['recommendation']
                        })
                        break  # Only report once per vulnerability type

        # Check for path parameter injection risks
        path_params = re.findall(r'\{(\w+)\}', route_path)
        for param in path_params:
            if not re.search(rf'{param}\s*:\s*(int|str|UUID)', route_code):
                findings.append({
                    'type': 'untyped_path_param',
                    'name': 'Untyped Path Parameter',
                    'severity': 'LOW',
                    'detail': f"Path parameter '{param}' should have type annotation",
                    'recommendation': 'Add type annotations to path parameters for automatic validation'
                })

        # Check for authentication
        auth_patterns = [
            r'Depends\s*\(\s*get_current_user',
            r'@requires_auth',
            r'@login_required',
            r'Authorization',
            r'Bearer',
        ]
        has_auth = any(re.search(p, route_code) for p in auth_patterns)

        # Sensitive endpoints that should have auth
        sensitive_patterns = ['delete', 'update', 'create', 'admin', 'user', 'password']
        is_sensitive = any(p in route_path.lower() for p in sensitive_patterns)

        if is_sensitive and not has_auth:
            findings.append({
                'type': 'missing_auth',
                'name': 'Potentially Missing Authentication',
                'severity': 'HIGH',
                'detail': f"Route '{route_path}' appears sensitive but may lack authentication",
                'recommendation': 'Add authentication dependency if this endpoint handles sensitive data'
            })

        # Check for rate limiting
        rate_limit_patterns = [r'@limiter', r'RateLimiter', r'slowapi', r'ratelimit']
        has_rate_limit = any(re.search(p, route_code, re.IGNORECASE) for p in rate_limit_patterns)

        if not has_rate_limit:
            findings.append({
                'type': 'no_rate_limit',
                'name': 'No Rate Limiting',
                'severity': 'MEDIUM',
                'recommendation': 'Consider adding rate limiting to prevent abuse and DoS attacks'
            })

        return {
            'route': route_path,
            'findings': findings,
            'finding_count': len(findings),
            'severity_summary': self._summarize_severity(findings),
            'is_secure': len([f for f in findings if f['severity'] in ['CRITICAL', 'HIGH']]) == 0
        }

    def _summarize_severity(self, findings: List[Dict]) -> Dict[str, int]:
        """Count findings by severity level"""
        summary = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for finding in findings:
            severity = finding.get('severity', 'LOW')
            if severity in summary:
                summary[severity] += 1
        return summary

    def validate_input_schema(self, schema: Dict) -> List[Dict]:
        """
        Validate a Pydantic schema for security issues.

        Args:
            schema: A dictionary representation of a Pydantic model

        Returns:
            List of security concerns with the schema
        """
        issues = []

        for field_name, field_info in schema.get('properties', {}).items():
            field_type = field_info.get('type', '')

            # Check for overly permissive types
            if field_type == 'object' and 'properties' not in field_info:
                issues.append({
                    'field': field_name,
                    'issue': 'Unbounded object type',
                    'risk': 'Could allow arbitrary nested data',
                    'recommendation': 'Define explicit schema for nested objects'
                })

            # Check for missing constraints on strings
            if field_type == 'string':
                if 'maxLength' not in field_info:
                    issues.append({
                        'field': field_name,
                        'issue': 'No maximum length',
                        'risk': 'Could lead to DoS via large payloads',
                        'recommendation': 'Add maxLength constraint'
                    })
                if 'pattern' not in field_info and field_name in ['email', 'url', 'phone']:
                    issues.append({
                        'field': field_name,
                        'issue': 'No format validation',
                        'risk': f'Invalid {field_name} values could be accepted',
                        'recommendation': f'Add regex pattern or use built-in {field_name} type'
                    })

        return issues

    def check_cors_config(self, origins: List[str]) -> Dict[str, Any]:
        """
        Analyze CORS configuration for security issues.

        Args:
            origins: List of allowed origins

        Returns:
            Analysis of CORS configuration
        """
        issues = []

        if '*' in origins:
            issues.append({
                'issue': 'Wildcard origin',
                'severity': 'HIGH',
                'detail': 'Allowing all origins defeats the purpose of CORS',
                'recommendation': 'Specify explicit allowed origins'
            })

        for origin in origins:
            if origin.startswith('http://') and 'localhost' not in origin:
                issues.append({
                    'issue': 'Non-HTTPS origin',
                    'severity': 'MEDIUM',
                    'detail': f"Origin '{origin}' uses HTTP",
                    'recommendation': 'Use HTTPS for production origins'
                })

            if re.match(r'https?://\*\.', origin):
                issues.append({
                    'issue': 'Wildcard subdomain',
                    'severity': 'MEDIUM',
                    'detail': f"Origin '{origin}' allows any subdomain",
                    'recommendation': 'Specify exact subdomains if possible'
                })

        return {
            'origins_count': len(origins),
            'issues': issues,
            'is_secure': len(issues) == 0
        }

    def generate_security_report(self, routes: List[Dict]) -> Dict[str, Any]:
        """
        Generate a comprehensive security report for all API routes.

        Args:
            routes: List of route definitions with 'path' and 'code' keys

        Returns:
            Complete security analysis report
        """
        all_findings = []
        routes_analyzed = []

        for route in routes:
            analysis = self.analyze_route(route.get('code', ''), route.get('path', ''))
            routes_analyzed.append(analysis)
            all_findings.extend(analysis['findings'])

        # Aggregate findings
        severity_totals = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for finding in all_findings:
            severity = finding.get('severity', 'LOW')
            if severity in severity_totals:
                severity_totals[severity] += 1

        # Calculate security score (0-100)
        deductions = severity_totals['CRITICAL'] * 25 + severity_totals['HIGH'] * 15 + severity_totals['MEDIUM'] * 5 + severity_totals['LOW'] * 2
        security_score = max(0, 100 - deductions)

        return {
            'summary': {
                'routes_analyzed': len(routes),
                'total_findings': len(all_findings),
                'severity_breakdown': severity_totals,
                'security_score': security_score,
                'grade': self._get_grade(security_score)
            },
            'routes': routes_analyzed,
            'recommendations': self._get_top_recommendations(all_findings),
            'required_headers': self.security_headers
        }

    def _get_grade(self, score: int) -> str:
        """Convert security score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'

    def _get_top_recommendations(self, findings: List[Dict]) -> List[str]:
        """Extract unique recommendations prioritized by severity"""
        recommendations = []
        seen = set()

        # Sort by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_findings = sorted(findings, key=lambda x: severity_order.get(x.get('severity', 'LOW'), 4))

        for finding in sorted_findings:
            rec = finding.get('recommendation', '')
            if rec and rec not in seen:
                seen.add(rec)
                recommendations.append(rec)

        return recommendations[:10]  # Top 10 recommendations

    def sanitize_input(self, value: Any, input_type: str = 'string') -> Any:
        """
        Sanitize user input based on expected type.

        Args:
            value: The input value to sanitize
            input_type: Expected type ('string', 'int', 'email', 'url', 'filename')

        Returns:
            Sanitized value
        """
        if value is None:
            return None

        if input_type == 'string':
            # Remove potentially dangerous characters
            if isinstance(value, str):
                # Strip null bytes and control characters
                value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', value)
                # Limit length
                return value[:10000]
            return str(value)[:10000]

        elif input_type == 'int':
            try:
                return int(value)
            except (ValueError, TypeError):
                return None

        elif input_type == 'email':
            if isinstance(value, str):
                # Basic email validation
                if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                    return value.lower()[:254]
            return None

        elif input_type == 'url':
            if isinstance(value, str):
                # Only allow http/https URLs
                if re.match(r'^https?://[a-zA-Z0-9.-]+', value):
                    return value[:2000]
            return None

        elif input_type == 'filename':
            if isinstance(value, str):
                # Remove path traversal attempts and dangerous characters
                value = re.sub(r'[/\\]', '', value)
                value = re.sub(r'\.\.', '', value)
                value = re.sub(r'[<>:"|?*]', '', value)
                return value[:255]
            return None

        return value
