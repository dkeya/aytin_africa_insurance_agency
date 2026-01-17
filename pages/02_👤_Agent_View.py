# pages/02_👤_Agent_View.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Agent Dashboard - AYTIN AFRICA",
    page_icon="👤",
    layout="wide"
)

# Try to import database modules
try:
    from config.database import db
    from models.member import Member
    from models.agent import Agent
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    # Create mock classes for demo
    class Member:
        def __init__(self):
            self.id = 1
            self.public_id = "M001"
            self.name = "John Kamau"
            self.phone_number = "+254712345678"
            self.cover_type = "standard"
            self.status = "Active"
            self.created_at = datetime.now()
            self.agent_id = 1
    
    class Agent:
        def __init__(self):
            self.id = 1
            self.name = "Demo Agent"
            self.code = "AG001"
    
    db = None

def get_demo_data():
    """Generate demo data for testing"""
    demo_members = [
        {
            "id": 1,
            "public_id": "M001",
            "name": "John Kamau",
            "phone_number": "+254712345678",
            "cover_type": "standard",
            "status": "Active",
            "created_at": datetime.now() - timedelta(hours=2),
            "family_count": 2
        },
        {
            "id": 2,
            "public_id": "M002",
            "name": "Mary Wanjiku",
            "phone_number": "+254723456789",
            "cover_type": "basic",
            "status": "Active",
            "created_at": datetime.now() - timedelta(hours=4),
            "family_count": 0
        },
        {
            "id": 3,
            "public_id": "M003",
            "name": "Peter Omondi",
            "phone_number": "+254734567890",
            "cover_type": "premium",
            "status": "Active",
            "created_at": datetime.now() - timedelta(hours=1),
            "family_count": 3
        }
    ]
    return demo_members

def get_todays_registrations(agent_id=1):
    """Get today's registrations for the agent"""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if DATABASE_AVAILABLE and db:
        try:
            # Get members from database
            members_data = db.get_all_members()
            # Filter for today and this agent
            today_members = [
                m for m in members_data 
                if datetime.fromisoformat(m.get('saved_at', '')).date() == datetime.now().date()
                and m.get('agent_id') == agent_id
            ]
            return today_members
        except:
            return get_demo_data()
    else:
        return get_demo_data()

def main():
    st.title("👤 Agent Dashboard")
    st.markdown("### Simple. Clean. Effective.")
    
    # Get current agent (simulated for demo)
    agent_id = 1  # Default agent ID
    
    if not DATABASE_AVAILABLE:
        st.info("⚠️ Using demo data - Database module not fully configured")
    
    # Simple two-column layout
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("---")
        st.subheader("Quick Actions")
        
        # New Registration Button
        if st.button("🎯 **New Registration**", 
                    type="primary", 
                    use_container_width=True,
                    help="Start a new member registration"):
            st.switch_page("pages/01_🏠_Onboarding.py")
        
        st.markdown("---")
        
        # Today's stats
        today_registrations = get_todays_registrations(agent_id)
        today_count = len(today_registrations)
        
        st.metric("Today's Registrations", today_count)
        
        # Agent info
        agent_name = "Demo Agent"
        agent_code = "AG001"
        st.caption(f"Agent: {agent_name}")
        st.caption(f"Code: {agent_code}")
        
        # Quick stats
        st.markdown("---")
        st.subheader("Quick Stats")
        
        if today_registrations:
            cover_types = [m.get('cover_type', 'unknown') for m in today_registrations]
            most_common = max(set(cover_types), key=cover_types.count) if cover_types else "None"
            st.write(f"**Most Common Cover:** {most_common}")
            
            total_family = sum(m.get('family_count', 0) for m in today_registrations)
            st.write(f"**Total Family Members:** {total_family}")
    
    with col2:
        st.markdown("---")
        st.subheader("✅ Success List - Today's Signups")
        
        if not today_registrations:
            st.info("No registrations yet today. Click 'New Registration' to get started!")
        else:
            # Display in a clean, simple format
            for i, member in enumerate(today_registrations, 1):
                created_time = member.get('created_at', datetime.now())
                if isinstance(created_time, str):
                    try:
                        created_time = datetime.fromisoformat(created_time)
                    except:
                        created_time = datetime.now()
                
                time_str = created_time.strftime('%H:%M')
                name = member.get('name', 'Unknown')
                
                with st.expander(f"{i}. {name} - {time_str}"):
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.write(f"**ID:** {member.get('public_id', 'N/A')}")
                        st.write(f"**Phone:** {member.get('phone_number', 'N/A')}")
                    
                    with col_b:
                        cover_type = member.get('cover_type', 'unknown')
                        cover_display = {
                            'basic': 'Basic',
                            'standard': 'Standard',
                            'premium': 'Premium',
                            'family': 'Family',
                            'corporate': 'Corporate'
                        }.get(cover_type, cover_type)
                        st.write(f"**Cover:** {cover_display}")
                        st.write(f"**Status:** {member.get('status', 'Active')}")
                    
                    with col_c:
                        family_count = member.get('family_count', 0)
                        st.write(f"**Family:** {family_count} member{'s' if family_count != 1 else ''}")
                        
                        # Days since registration
                        days_since = (datetime.now() - created_time).days
                        st.write(f"**Member for:** {days_since} day{'s' if days_since != 1 else ''}")
        
        # Summary section
        st.markdown("---")
        st.subheader("Today's Summary")
        
        summary_cols = st.columns(4)
        
        # Calculate totals
        total_today = len(today_registrations)
        
        # Count by cover type
        cover_counts = {}
        for member in today_registrations:
            cover_type = member.get('cover_type', 'unknown')
            cover_counts[cover_type] = cover_counts.get(cover_type, 0) + 1
        
        with summary_cols[0]:
            st.metric("Total", total_today, 
                     f"+{total_today} today" if total_today > 0 else "0")
        
        with summary_cols[1]:
            # Most popular cover
            if cover_counts:
                popular = max(cover_counts, key=cover_counts.get)
                popular_display = {
                    'basic': 'Basic',
                    'standard': 'Standard',
                    'premium': 'Premium'
                }.get(popular, popular)
                st.metric("Popular Cover", popular_display)
            else:
                st.metric("Popular Cover", "None")
        
        with summary_cols[2]:
            # Family members total
            total_family = sum(m.get('family_count', 0) for m in today_registrations)
            st.metric("Family Members", total_family)
        
        with summary_cols[3]:
            # Success rate
            success_rate = "100%" if total_today > 0 else "0%"
            st.metric("Success Rate", success_rate)
    
    # Additional features
    st.markdown("---")
    
    with st.expander("📊 Performance Insights"):
        if today_registrations:
            # Create a simple chart
            df = pd.DataFrame(today_registrations)
            if 'cover_type' in df.columns:
                cover_dist = df['cover_type'].value_counts()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Cover Distribution:**")
                    for cover, count in cover_dist.items():
                        cover_name = {
                            'basic': 'Basic Cover',
                            'standard': 'Standard Cover',
                            'premium': 'Premium Cover',
                            'family': 'Family Cover',
                            'corporate': 'Corporate Cover'
                        }.get(cover, cover)
                        st.write(f"- {cover_name}: {count}")
                
                with col2:
                    st.write("**Timeline:**")
                    times = []
                    for member in today_registrations:
                        created = member.get('created_at', datetime.now())
                        if isinstance(created, str):
                            try:
                                created = datetime.fromisoformat(created)
                            except:
                                created = datetime.now()
                        times.append(created.strftime('%H:%M'))
                    
                    for time in sorted(times):
                        st.write(f"- {time}")
        else:
            st.info("No data to display")
    
    # Footer note
    st.markdown("---")
    st.caption("""
    ℹ️ **Agent Note:** This view shows only successful registrations. 
    No commission amounts, total money collected, or payout information is displayed here.
    Contact admin for financial reports.
    """)
    
    # Refresh button
    if st.button("🔄 Refresh Data", type="secondary"):
        st.rerun()

if __name__ == "__main__":
    main()