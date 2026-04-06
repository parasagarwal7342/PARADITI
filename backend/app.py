"""
Main Flask application for Paraditi
"""
"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026 P Λ R Λ D I T I. All rights reserved.
Proprietary and Confidential. Unauthorized copying is strictly prohibited.
Patent Pending: Claims A-U (See IP_MANIFEST.md).
"""
import os
import sys
import io

# Set UTF-8 encoding for stdout/stderr on Windows (skip if closed/unavailable)
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'buffer') and sys.stdout.buffer is not None:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        if hasattr(sys.stderr, 'buffer') and sys.stderr.buffer is not None:
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (ValueError, OSError, AttributeError):
        pass

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, send_from_directory, render_template_string, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.config import config
from backend.database import init_db
from backend.cache import init_cache
from backend.routes import api

def create_app(config_name='default'):
    """Create and configure Flask application"""
    app = Flask(__name__, 
                static_folder='../frontend',
                template_folder='../frontend')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # CRITICAL SECURITY CHECK
    if config_name == 'production':
        if app.config.get('SECRET_KEY') == 'dev-secret-key-change-in-production':
            raise ValueError("CRITICAL SECURITY ERROR: Default SECRET_KEY used in Production. Set SCHEME_SECRET_KEY environment variable.")
        if app.config.get('JWT_SECRET_KEY') == 'dev-jwt-secret-key-change-in-production':
            raise ValueError("CRITICAL SECURITY ERROR: Default JWT_SECRET_KEY used in Production.")
    
    print(f"Server DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    JWTManager(app)
    
    # Initialize database
    init_db(app)
    
    # Initialize Redis Cache
    init_cache(app)
    
    # ----------------------------
    # SECURITY HARDENING START
    # ----------------------------
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    from flask_talisman import Talisman
    from backend.firewall import firewall
    
    # 0. Application Firewall (WAF-lite)
    firewall.init_app(app)

    # 1. Rate Limiting
    # Securely check Redis availability (Self-Healing Infrastructure)
    limiter_storage = "memory://"
    redis_url = app.config.get('REDIS_URL')
    
    if redis_url and redis_url.startswith("redis"):
        try:
            import redis
            r = redis.from_url(redis_url)
            r.ping()
            limiter_storage = redis_url
            print(f"Rate Limiter: Using Redis at {redis_url}")
        except Exception:
            print("Rate Limiter: Redis unreachable. Falling back to In-Memory storage.")
            
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["2000 per day", "500 per hour"],
        storage_uri=limiter_storage
    )
    
    # 2. Security Headers (CSP, HSTS, etc.)
    # In development (HTTP), force_https=False. In prod, True.
    is_production = (config_name == 'production')
    
    # CSP: Allow unsafe-inline for now as we have legacy frontend code.
    # ideally we should move to nonces.
    csp = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' https://cdn.jsdelivr.net", # Allow CDNs if needed
        'style-src': "'self' 'unsafe-inline' https://fonts.googleapis.com",
        'font-src': "'self' https://fonts.gstatic.com",
        'img-src': "'self' data: https: blob:"
    }
    
    Talisman(app, 
             content_security_policy=csp, 
             force_https=is_production,
             strict_transport_security=is_production,
             session_cookie_secure=is_production)
    
    # 3. Security Middleware for Real-time Threat Detection
    @app.before_request
    def security_middleware():
        # Prevent access to dotfiles or sensitive paths
        path = request.path
        if any(part.startswith('.') for part in path.split('/')):
            print(f"SECURITY ALERT: Blocked access to hidden path {path}")
            return render_template_string("<h1>403 Forbidden</h1>"), 403
            
        # Detect large payloads (DoS prevention)
        if request.content_length and request.content_length > 10 * 1024 * 1024:
            print(f"SECURITY ALERT: Large payload rejected from {request.remote_addr}")
            return render_template_string("<h1>Payload Too Large</h1>"), 413

    @app.after_request
    def set_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
             
    # ----------------------------
    # SECURITY HARDENING END
    # ----------------------------
    
    # Register blueprints
    app.register_blueprint(api)
    
    # Serve frontend files
    @app.route('/')
    def index():
        """Serve index.html"""
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/<path:filename>')
    def serve_static(filename):
        """
        Securely serve static files from the frontend directory.
        Flask's send_from_directory automatically prevents directory traversal.
        """
        # Ensure we don't accidentally serve from parent directories via '..'
        # and fallback to index.html for SPA routing
        try:
            return send_from_directory(app.static_folder, filename)
        except:
            # If file doesn't exist, serve index.html (SPA fallback)
            return send_from_directory(app.static_folder, 'index.html')
    
    return app

if __name__ == '__main__':
    # When run in background, stdout/stderr may be closed; redirect to devnull so Flask doesn't crash
    try:
        sys.stdout.fileno()
    except (ValueError, OSError, AttributeError):
        # Redirect to log file for debugging in non-interactive environments
        sys.stdout = open('server.log', 'w', encoding='utf-8')
        sys.stderr = open('server.error.log', 'w', encoding='utf-8')
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    try:
        print("\n" + "="*50)
        print("P Λ R Λ D I T I - AI-Powered Government Scheme Recommender")
        print("Server: http://localhost:5000")
        print("="*50 + "\n")
    except (ValueError, OSError):
        pass
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=(env == 'development')
    )
