# config/database.py - SIMPLIFIED VERSION
import pandas as pd
from datetime import datetime
import json
import os

class SimpleDatabase:
    """Simple file-based database for testing"""
    
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
    def save_member(self, member_data):
        """Save member to JSON file"""
        member_id = member_data.get('public_id', f"M{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        # Add timestamp
        member_data['saved_at'] = datetime.now().isoformat()
        
        # Save to file
        filename = os.path.join(self.data_dir, f"member_{member_id}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(member_data, f, indent=2, default=str)
        
        return member_id
    
    def get_all_members(self):
        """Get all members from files"""
        members = []
        if os.path.exists(self.data_dir):
            for filename in os.listdir(self.data_dir):
                if filename.startswith('member_') and filename.endswith('.json'):
                    filepath = os.path.join(self.data_dir, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            member_data = json.load(f)
                            members.append(member_data)
                    except:
                        continue
        return members
    
    def export_to_excel(self, date_filter=None):
        """Export to Excel for testing"""
        members = self.get_all_members()
        
        if not members:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(members)
        
        # Filter by date if specified
        if date_filter:
            if 'saved_at' in df.columns:
                df['saved_at'] = pd.to_datetime(df['saved_at'])
                df = df[df['saved_at'].dt.date == date_filter]
        
        # Create Excel file
        excel_file = os.path.join(self.data_dir, f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        df.to_excel(excel_file, index=False)
        
        return excel_file

# Create a global instance
db = SimpleDatabase()

# For compatibility with original code
def get_db():
    """Mock database session"""
    return db

def SessionLocal():
    """Mock session"""
    return db

def export_to_excel(date_filter=None, agent_filter=None):
    """Export function"""
    return db.export_to_excel(date_filter)