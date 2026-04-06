"""
Security Utilities for SAHAJ
Includes AES-256 Encryption for documents at rest.
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class FileEncryptor:
    """
    Handles AES-256 encryption/decryption for file uploads.
    Uses a master key from environment variables.
    """
    
    def __init__(self, key=None):
        """
        Initialize with a key. If no key provided, tries to load from env 
        or generates a persistent local one for development.
        """
        self.key = key or os.getenv('ENCRYPTION_KEY')
        
        if not self.key:
            # Persistent key for development/demo
            key_path = os.path.join(os.getcwd(), 'instance', 'master.key')
            if os.path.exists(key_path):
                with open(key_path, 'rb') as f:
                    self.key = f.read()
            else:
                print("WARNING: Generating a persistent local ENCRYPTION_KEY for development.")
                self.key = Fernet.generate_key()
                # Ensure instance dir exists
                os.makedirs(os.path.dirname(key_path), exist_ok=True)
                with open(key_path, 'wb') as f:
                    f.write(self.key)
        else:
            # Ensure key is bytes
            if isinstance(self.key, str):
                self.key = self.key.encode()
                
        self.fernet = Fernet(self.key)

    def encrypt_data(self, data):
        """
        Encrypts bytes data.
        """
        if not data:
            return data
        return self.fernet.encrypt(data)

    def decrypt_data(self, encrypted_data):
        """
        Decrypts bytes data.
        """
        if not encrypted_data:
            return encrypted_data
        return self.fernet.decrypt(encrypted_data)

# Global instance
_encryptor = None

def get_encryptor():
    global _encryptor
    if not _encryptor:
        _encryptor = FileEncryptor()
    return _encryptor
