# pages/03_👑_Admin_Dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
import io

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Admin Dashboard - AYTIN AFRICA",
    page_icon="👑",
    layout="wide"
)

# Try to import modules
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from services.encryption_service import EncryptionService
    from config.database import db
    from config.settings import APP_CONFIG
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    
    # Fallback classes
    class EncryptionService:
        def mask_id_number(self, id_number, is_super_admin=False):
            if not id_number or len(id_number) < 4:
                return id_number
            if is_super_admin:
                return id_number
            return f"{id_number[:3]}****{id_number[-1]}"
    
    db = None

def generate_demo_data():
    """Generate demo data for admin dashboard"""
    # Demo members
    members = []
    for i in range(1, 31):
        status = "Active" if i % 4 != 0 else "Inactive" if i % 4 == 1 else "Suspended"
        cover_types = ["basic", "standard", "premium", "family", "corporate"]
        cover = cover_types[i % 5]
        
        members.append({
            "public_id": f"M{1000 + i}",
            "name": f"Member {i}",
            "id_number": f"1234567{i:02d}",
            "phone_number": f"+2547{i:08d}",
            "cover_type": cover,
            "status": status,
            "registration_date": datetime.now() - timedelta(days=i % 30),
            "balance_days": i % 7 - 3,  # Range from -3 to +3
            "total_paid": (i % 10) * 2000,
            "agent_id": (i % 3) + 1
        })
    
    # Demo agents
    agents = [
        {"id": 1, "name": "John Kamau", "code": "AG001", "is_active": True},
        {"id": 2, "name": "Mary Wanjiku", "code": "AG002", "is_active": True},
        {"id": 3, "name": "Peter Omondi", "code": "AG003", "is_active": False}
    ]
    
    return members, agents

def calculate_metrics(members):
    """Calculate key metrics from member data"""
    total_members = len(members)
    
    # Total premiums (simulated)
    total_premium = sum(m.get('total_paid', 0) for m in members)
    
    # Today's registrations
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_registrations = sum(1 for m in members 
                             if m.get('registration_date', datetime.now()) >= today_start)
    
    # Pending payments (negative balances)
    pending_count = sum(1 for m in members if m.get('balance_days', 0) < 0)
    
    # Active members
    active_members = sum(1 for m in members if m.get('status') == "Active")
    
    return {
        "total_members": total_members,
        "total_premium": total_premium,
        "today_registrations": today_registrations,
        "pending_count": pending_count,
        "active_members": active_members
    }

def main():
    st.title("👑 Admin Dashboard")
    st.markdown("### The Big Picture - Total Control & Visibility")
    
    # Check module availability
    if not MODULES_AVAILABLE:
        st.info("ℹ️ Using demo data - Some modules not fully configured")
    
    # Initialize encryption service
    enc_service = EncryptionService()
    
    # Authentication
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        with st.form("admin_login"):
            st.subheader("Admin Login")
            col1, col2 = st.columns([2, 1])
            
            with col1:
                username = st.text_input("Username", placeholder="admin")
                password = st.text_input("Password", type="password", placeholder="••••••••")
            
            with col2:
                st.write("")  # Spacer
                st.write("")
                if st.form_submit_button("🔑 Login", type="primary", use_container_width=True):
                    if username == "admin" and password == "admin123":
                        st.session_state.admin_authenticated = True
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            
            st.caption("Default: admin / admin123")
        return
    
    # Get data
    if db:
        try:
            members_data = db.get_all_members()
            # Convert string dates to datetime
            for member in members_data:
                if 'saved_at' in member:
                    member['registration_date'] = datetime.fromisoformat(member['saved_at'])
        except:
            members_data, agents_data = generate_demo_data()
    else:
        members_data, agents_data = generate_demo_data()
    
    # Calculate metrics
    metrics = calculate_metrics(members_data)
    
    # Header Metrics
    st.markdown("---")
    st.subheader("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Premiums", f"KES {metrics['total_premium']:,.2f}")
    
    with col2:
        st.metric("Total Members", metrics['total_members'], 
                 f"+{metrics['today_registrations']} today")
    
    with col3:
        st.metric("Pending Policies", metrics['pending_count'])
    
    with col4:
        st.metric("Active Members", f"{metrics['active_members']}/{metrics['total_members']}")
    
    # Filters Section
    st.markdown("---")
    st.subheader("🔍 Filter & Export Data")
    
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        date_filter = st.date_input("Filter by Date", value=None)
    
    with filter_col2:
        agent_options = ["All", "AG001 - John", "AG002 - Mary", "AG003 - Peter"]
        agent_filter = st.selectbox("Filter by Agent", agent_options)
    
    with filter_col3:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Active", "Inactive", "Suspended"]
        )
    
    with filter_col4:
        cover_filter = st.selectbox(
            "Filter by Cover",
            ["All", "Basic", "Standard", "Premium", "Family", "Corporate"]
        )
    
    # Filter data
    filtered_members = members_data.copy()
    
    if date_filter:
        filtered_members = [
            m for m in filtered_members 
            if m.get('registration_date', datetime.now()).date() == date_filter
        ]
    
    if agent_filter != "All":
        agent_id = agent_options.index(agent_filter)
        filtered_members = [
            m for m in filtered_members 
            if m.get('agent_id', 0) == agent_id
        ]
    
    if status_filter != "All":
        filtered_members = [
            m for m in filtered_members 
            if m.get('status', '').lower() == status_filter.lower()
        ]
    
    if cover_filter != "All":
        filtered_members = [
            m for m in filtered_members 
            if m.get('cover_type', '').lower() == cover_filter.lower()
        ]
    
    # Payment Details Section
    st.markdown("---")
    st.subheader("💰 Payment Status Details")
    
    # Create payment status table
    payment_data = []
    for member in filtered_members[:50]:  # Limit for display
        days_balance = member.get('balance_days', 0)
        amount_due = abs(days_balance) * 200 if days_balance < 0 else 0
        
        # Mask ID
        masked_id = enc_service.mask_id_number(
            member.get('id_number', ''),
            is_super_admin=st.session_state.get('is_super_admin', False)
        )
        
        payment_data.append({
            "Member ID": member.get('public_id', ''),
            "Name": member.get('name', ''),
            "ID Number": masked_id,
            "Phone": member.get('phone_number', ''),
            "Cover": member.get('cover_type', '').title(),
            "Balance Days": days_balance,
            "Amount Due": f"KES {amount_due:,.2f}" if amount_due > 0 else "Paid",
            "Status": member.get('status', ''),
            "Registration Date": member.get('registration_date', datetime.now()).strftime("%Y-%m-%d")
        })
    
    if payment_data:
        df_payments = pd.DataFrame(payment_data)
        
        # Color code balance days
        def color_balance(val):
            if isinstance(val, (int, float)):
                if val > 0:
                    return 'background-color: #d4edda; color: #155724;'
                elif val < 0:
                    return 'background-color: #f8d7da; color: #721c24;'
            return ''
        
        # Display styled dataframe
        styled_df = df_payments.style.map(color_balance, subset=['Balance Days'])
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Export buttons
        st.subheader("📤 Export Data")
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            # Excel export
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_payments.to_excel(writer, index=False, sheet_name='Members')
            
            st.download_button(
                label="📊 Download Excel",
                data=excel_buffer.getvalue(),
                file_name=f"aytin_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col_exp2:
            # CSV export
            csv = df_payments.to_csv(index=False)
            st.download_button(
                label="📈 Download CSV",
                data=csv,
                file_name=f"aytin_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("No data matching the selected filters")
    
    # Visualizations
    if PLOTLY_AVAILABLE and filtered_members:
        st.markdown("---")
        st.subheader("📈 Analytics & Charts")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            # Registration trend (last 7 days)
            dates = [(datetime.now() - timedelta(days=i)).date() for i in range(7, -1, -1)]
            reg_counts = []
            
            for date in dates:
                count = sum(1 for m in members_data 
                           if m.get('registration_date', datetime.now()).date() == date)
                reg_counts.append(count)
            
            trend_df = pd.DataFrame({
                "Date": [d.strftime("%b %d") for d in dates],
                "Registrations": reg_counts
            })
            
            fig1 = px.bar(
                trend_df, 
                x="Date", 
                y="Registrations",
                title="📅 Daily Registrations (Last 7 Days)",
                color="Registrations",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with viz_col2:
            # Cover type distribution
            cover_counts = {}
            for member in filtered_members:
                cover = member.get('cover_type', 'unknown').title()
                cover_counts[cover] = cover_counts.get(cover, 0) + 1
            
            if cover_counts:
                covers_df = pd.DataFrame({
                    "Cover": list(cover_counts.keys()),
                    "Count": list(cover_counts.values())
                })
                
                fig2 = px.pie(
                    covers_df,
                    values="Count",
                    names="Cover",
                    title="🛡️ Cover Type Distribution",
                    hole=0.3
                )
                st.plotly_chart(fig2, use_container_width=True)
    
    # Agent Performance
    st.markdown("---")
    st.subheader("👥 Agent Performance")
    
    agent_performance = [
        {"Agent": "John Kamau", "Code": "AG001", "Total Members": 12, "Today": 3, "Active": True},
        {"Agent": "Mary Wanjiku", "Code": "AG002", "Total Members": 8, "Today": 2, "Active": True},
        {"Agent": "Peter Omondi", "Code": "AG003", "Total Members": 5, "Today": 0, "Active": False}
    ]
    
    df_agents = pd.DataFrame(agent_performance)
    st.dataframe(df_agents, use_container_width=True)
    
    # Admin actions
    st.markdown("---")
    st.subheader("⚙️ Admin Actions")
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("🔄 Run Daily Reminders", use_container_width=True):
            st.success("Daily reminders processed successfully!")
            st.info("This would send SMS reminders to members with negative balances")
    
    with action_col2:
        if st.button("📧 Send Reports", use_container_width=True):
            st.success("Reports queued for sending!")
            st.info("This would email reports to underwriters")
    
    with action_col3:
        if st.button("🔐 Toggle Super Admin", use_container_width=True):
            current = st.session_state.get('is_super_admin', False)
            st.session_state.is_super_admin = not current
            status = "🟢 ON" if not current else "⚪ OFF"
            st.success(f"Super Admin Mode: {status}")
            st.rerun()
    
    # Logout
    st.markdown("---")
    if st.button("🚪 Logout", type="secondary", use_container_width=True):
        st.session_state.admin_authenticated = False
        st.rerun()

if __name__ == "__main__":
    main()