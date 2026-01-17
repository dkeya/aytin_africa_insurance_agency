# database/init_db.py
from config.database import Base, engine, SessionLocal
from models.member import Member
from models.agent import Agent
from models.payment import PaymentBalance
from models.family import FamilyMember
from services.encryption_service import EncryptionService
from datetime import datetime, timedelta
import random

def init_database():
    """Initialize database with sample data for testing"""
    
    print("Initializing database...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create sample agents
        agents = [
            Agent(name="John Kamau", code="AG001", phone_number="+254712345678"),
            Agent(name="Mary Wanjiku", code="AG002", phone_number="+254723456789"),
            Agent(name="Peter Omondi", code="AG003", phone_number="+254734567890"),
        ]
        
        for agent in agents:
            db.add(agent)
        
        db.commit()
        
        print("✅ Database initialized successfully!")
        print(f"Created {len(agents)} sample agents")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()