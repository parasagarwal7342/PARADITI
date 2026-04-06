"""
P Λ R Λ D I T I (परादिति) - AI-Powered Government Scheme Gateway
Copyright (c) 2026 P Λ R Λ D I T I. All rights reserved.
Proprietary and Confidential. Unauthorized copying is strictly prohibited.
Patent Pending: Claims A-U (See IP_MANIFEST.md).
"""
import re
import html
import filetype
import bleach
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# Initialize Argon2 password hasher
# Using high memory and CPU parameters for security
ph = PasswordHasher(
    time_cost=3,      # Number of iterations
    memory_cost=65536,  # Memory usage in KB (64 MB)
    parallelism=4,    # Number of parallel threads
    hash_len=32,      # Length of the hash
    salt_len=16       # Length of the salt
)

def hash_password(password):
    """
    Hash a password using Argon2
    
    Args:
        password (str): Plain text password
        
    Returns:
        str: Hashed password
    """
    try:
        return ph.hash(password)
    except Exception as e:
        raise Exception(f"Error hashing password: {str(e)}")

def verify_password(password_hash, password):
    """
    Verify a password against its hash
    
    Args:
        password_hash (str): Hashed password from database
        password (str): Plain text password to verify
        
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False
    except Exception as e:
        print(f"Error verifying password: {str(e)}")
        return False

def sanitize_input(input_string):
    """
    Sanitize user input to prevent XSS attacks while ensuring data integrity.
    Note: SQL Injection is primarily handled by SQLAlchemy's parameterized queries.
    This function focuses on preventing XSS and removing dangerous control characters.
    
    Args:
        input_string (str): User input string
        
    Returns:
        str: Sanitized string
    """
    if not isinstance(input_string, str):
        return str(input_string)
    
    # 1. Remove null bytes
    input_string = input_string.replace('\x00', '')
    
    # 2. Robust Sanitization using Bleach
    # Strip ALL HTML tags to ensure plain text input.
    # This prevents XSS by removing <script>, <img>, etc. entirely.
    cleaned_string = bleach.clean(input_string, tags=[], attributes={}, strip=True)
    
    return cleaned_string.strip()

def validate_email(email):
    """
    Validate email format
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validate_password_strength(password):
    """
    Validate password strength
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid, message)
    """
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"

def validate_file_upload(file_stream, allowed_types=['image/jpeg', 'image/png', 'application/pdf']):
    """
    Validate file type using magic numbers (content inspection)
    
    Args:
        file_stream: File-like object (e.g. request.files['key'])
        allowed_types (list): List of allowed MIME types
        
    Returns:
        bool: True if valid
        str: Detected MIME type or error message
    """
    # Read first 2048 bytes for type detection
    head = file_stream.read(2048)
    file_stream.seek(0) # Reset pointer
    
    kind = filetype.guess(head)
    if kind is None:
        return False, "Could not determine file type"
        
    if kind.mime not in allowed_types:
        return False, f"Invalid file type: {kind.mime}. Allowed: {', '.join(allowed_types)}"
        
    return True, kind.mime


