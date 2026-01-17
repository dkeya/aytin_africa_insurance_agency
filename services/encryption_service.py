# services/encryption_service.py - SIMPLIFIED VERSION
import hashlib
import base64
from cryptography.fernet import Fernet
from config.settings import APP_CONFIG

class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        # Use a simple key for testing
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return ""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except:
            return data  # Return as-is if encryption fails
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return ""
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except:
            return encrypted_data  # Return as-is if decryption fails
    
    def hash_data(self, data: str) -> str:
        """Create hash for searching"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    def mask_id_number(self, id_number: str, is_super_admin: bool = False) -> str:
        """Partially mask ID number for display"""
        if not id_number:
            return ""
        
        if is_super_admin or len(id_number) <= 4:
            return id_number
        
        visible_start = id_number[:3]
        visible_end = id_number[-1]
        masked_middle = "*" * (len(id_number) - 4)
        
        return f"{visible_start}{masked_middle}{visible_end}"