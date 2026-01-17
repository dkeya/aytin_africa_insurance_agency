# models/member.py - UPDATED VERSION
from datetime import datetime

class Member:
    """Member model - working version"""
    def __init__(self):
        self.id = None
        self.public_id = None
        self.name = None
        self.id_number_encrypted = None
        self.id_number_hash = None
        self.dob = None
        self.gender = None
        self.phone_number = None
        self.phone_verified = False
        self.cover_type = None
        self.registration_date = datetime.now()
        self.agent_id = None
        self.status = "Active"
        self.created_at = datetime.now()

# For backward compatibility
member = Member