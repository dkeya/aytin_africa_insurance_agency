# models/family.py
from datetime import datetime

class FamilyMember:
    """Family member model - simplified version"""
    def __init__(self):
        self.id = None
        self.member_id = None
        self.relationship = None  # spouse, child
        self.name_encrypted = None
        self.dob_encrypted = None
        self.gender = None
        self.is_active = True

# For backward compatibility
family_member = FamilyMember