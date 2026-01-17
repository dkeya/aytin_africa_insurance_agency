# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Cover options
    COVER_OPTIONS = {
        "basic": {"name": "Basic Cover", "daily": 150, "features": ["Inpatient", "Emergency"]},
        "standard": {"name": "Standard Cover", "daily": 200, "features": ["Inpatient", "Outpatient", "Maternity"]},
        "premium": {"name": "Premium Cover", "daily": 300, "features": ["Full coverage", "Dental", "Optical"]},
        "family": {"name": "Family Cover", "daily": 500, "features": ["4 members", "Full coverage"]},
        "corporate": {"name": "Corporate Cover", "daily": 400, "features": ["Group", "Custom benefits"]}
    }
    
    # Payment settings
    DAILY_PREMIUM_RATE = 200  # KES per day
    GRACE_PERIOD_DAYS = 7
    REMINDER_TIME = "13:00"  # 1:00 PM
    
    # Application
    APP_NAME = "AYTIN AFRICA Insurance"
    APP_VERSION = "1.0.0"

APP_CONFIG = Config()