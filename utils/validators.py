# utils/validators.py
import re
from datetime import datetime
import phonenumbers

class Validators:
    """Validation utilities for the insurance platform"""
    
    @staticmethod
    def validate_kenyan_id(id_number: str) -> bool:
        """Validate Kenyan ID number format"""
        if not id_number or not isinstance(id_number, str):
            return False
        
        id_number = id_number.strip()
        
        # Basic format validation
        if not re.match(r'^\d{8,10}$', id_number):
            return False
        
        # Additional validation logic can be added here
        # For example, check digit validation
        
        return True
    
    @staticmethod
    def validate_phone_number(phone: str, country='KE') -> bool:
        """Validate phone number format"""
        try:
            parsed = phonenumbers.parse(phone, country)
            return phonenumbers.is_valid_number(parsed)
        except:
            return False
    
    @staticmethod
    def validate_date_of_birth(dob: datetime) -> bool:
        """Validate date of birth is reasonable"""
        if not isinstance(dob, datetime):
            return False
        
        # Must be at least 18 years old
        min_age = datetime.now().year - 18
        if dob.year > min_age:
            return False
        
        # Cannot be born before 1900
        if dob.year < 1900:
            return False
        
        return True
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate name format"""
        if not name or len(name.strip()) < 2:
            return False
        
        # Name should contain only letters, spaces, and common punctuation
        if not re.match(r'^[A-Za-z\s\'-]+$', name):
            return False
        
        return True