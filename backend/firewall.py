"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026 P Λ R Λ D I T I. All rights reserved.
Proprietary and Confidential. Unauthorized copying is strictly prohibited.
Patent Pending: Claims A-U (See IP_MANIFEST.md).
"""
import re
import logging
from flask import request, abort, render_template_string

# Configure logging for security events
security_logger = logging.getLogger('paraditi_security')
security_logger.setLevel(logging.INFO)
handler = logging.FileHandler('security_events.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
security_logger.addHandler(handler)

class ParaditiFirewall:
    """
    A lightweight Web Application Firewall (WAF) for Flask.
    Detects SQL injection, XSS, and path traversal patterns.
    """
    
    # Common attack patterns
    PATTERNS = {
        'sql_injection': [
            r"union\s+select",
            r"select\s+.*\s+from",
            r"insert\s+into",
            r"delete\s+from",
            r"drop\s+table",
            r"update\s+.*\s+set",
            r"--",
            r"/\*.*\*/",
            r"'\s*or\s*'.*='",
            r"\"\s*or\s*\".*=\""
        ],
        'xss': [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"alert\(",
            r"eval\(",
            r"document\.cookie"
        ],
        'path_traversal': [
            r"\.\./",
            r"\.\.\\",
            r"/etc/passwd",
            r"/windows/system32",
            r"boot\.ini"
        ],
        'remote_file_inclusion': [
            r"https?://",
            r"ftp://"
        ]
    }

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        @app.before_request
        def firewall_check():
            # Skip check for static files if served by Flask
            if request.path.startswith('/static/'):
                return

            # 1. Check Query Parameters
            for key, value in request.args.items():
                self._check_value(key, value)

            # 2. Check Form Data
            if request.form:
                for key, value in request.form.items():
                    self._check_value(key, value)

            # 3. Check JSON Body
            if request.is_json:
                try:
                    json_data = request.get_json()
                    self._check_recursive(json_data)
                except Exception:
                    pass

            # 4. Check Headers for common exploitation headers
            user_agent = request.headers.get('User-Agent', '')
            if any(p in user_agent.lower() for p in ['sqlmap', 'nikto', 'nmap', 'python-requests/']):
                self._log_and_block('suspicious_user_agent', user_agent)

    def _check_value(self, key, value):
        if not isinstance(value, str):
            return
            
        for threat, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    self._log_and_block(threat, f"{key}={value}")

    def _check_recursive(self, data):
        if isinstance(data, dict):
            for k, v in data.items():
                self._check_recursive(v)
        elif isinstance(data, list):
            for item in data:
                self._check_recursive(item)
        elif isinstance(data, str):
            self._check_value("json_data", data)

    def _log_and_block(self, threat_type, details):
        ip = request.remote_addr
        security_logger.warning(f"BLOCKED {threat_type} from {ip}: {details}")
        
        # Return a polite but firm security block message
        block_html = """
        <div style="font-family: 'Inter', sans-serif; text-align: center; padding: 50px; background: #0f172a; color: white; height: 100vh; display: flex; flex-direction: column; justify-content: center;">
            <h1 style="color: #00f2ff; font-size: 3rem;">P Λ R Λ D I T I</h1>
            <h2 style="color: #f43f5e;">Security Block Engaged</h2>
            <p>Your request has been intercepted by the <strong>Paraditi Firewall</strong>.</p>
            <p style="color: #94a3b8;">Threat Analysis: {{ threat_type }} | Incident ID: {{ security_id }}</p>
            <hr style="width: 200px; border: 1px solid #1e293b; margin: 20px auto;">
            <p><small>&copy; 2026 P Λ R Λ D I T I Autonomous Systems</small></p>
        </div>
        """
        import uuid
        security_id = str(uuid.uuid4())[:8]
        abort(render_template_string(block_html, security_id=security_id), 403)

# Initialize global instance
firewall = ParaditiFirewall()
