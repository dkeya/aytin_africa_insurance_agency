# models/agent.py
from datetime import datetime

class Agent:
    """Agent model - simplified version"""
    def __init__(self):
        self.id = None
        self.name = None
        self.code = None
        self.phone_number = None
        self.is_active = True
        self.daily_registrations = 0
        self.created_at = datetime.utcnow()

# For backward compatibility
agent = Agent