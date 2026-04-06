"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026 P Λ R Λ D I T I. All rights reserved.
Proprietary and Confidential. Unauthorized copying is strictly prohibited.
Patent Pending: Claims A-U (See IP_MANIFEST.md).
"""
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from functools import wraps
from backend.models import User
from backend.database import db

def generate_token(user):
    """
    Generate JWT token for user
    
    Args:
        user (User): User object
        
    Returns:
        str: JWT access token
    """
    identity = str(user.id)
    return create_access_token(identity=identity)

def get_current_user():
    """
    Get current authenticated user from JWT token
    
    Returns:
        User: Current user object or None
    """
    try:
        identity = get_jwt_identity()
        if identity:
            # Handle both string ID (new) and dict (legacy/fallback)
            if isinstance(identity, dict):
                user_id = identity.get('id')
            else:
                user_id = identity
            
            return User.query.get(int(user_id))
    except Exception as e:
        print(f"Error getting current user: {str(e)}")
    return None

def admin_required(f):
    """
    Decorator to require admin role (for future use)
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return {'error': 'Authentication required'}, 401
        # Add admin check here if needed
        return f(*args, **kwargs)
    return decorated_function
