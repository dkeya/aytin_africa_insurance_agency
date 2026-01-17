# pages/05_💳_Member_Portal.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Member Portal - AYTIN AFRICA",
    page_icon="💳",
    layout="wide"
)

# Try to import modules
try:
    from services.encryption_service import EncryptionService
    from config.database import db
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    
    class EncryptionService:
        def mask_id_number(self, id_number, is_super_admin=False):
            if not id_number or len(id_number) < 4:
                return id_number
            return f"{id_number[:3]}****{id_number[-1]}"
    
    db = None

def generate_demo_member_data(member_id="M001"):
    """Generate demo member data"""
    import random
    
    member_data = {
        "public_id": member_id,
        "name": "John Kamau",
        "phone": "+254712345678",
        "cover_type": "standard",
        "daily_premium": 200,
        "registration_date": datetime.now() - timedelta(days=30),
        "status": "Active",
        "family_members": [
            {"name": "Mary Kamau", "relationship": "spouse", "dob": "1990-05-12"},
            {"name": "Sarah Kamau", "relationship": "child", "dob": "2015-08-23"},
            {"name": "David Kamau", "relationship": "child", "dob": "2018-03-17"}
        ]
    }
    
    # Payment history
    payment_history = []
    balance_days = random.randint(-2, 5)
    
    for i in range(30, 0, -1):
        amount = 200 if random.random() > 0.3 else 0
        if amount > 0:
            payment_history.append({
                "date": datetime.now() - timedelta(days=i),
                "amount": amount,
                "days": 1,
                "method": "M-Pesa",
                "transaction_id": f"MP{i:06d}"
            })
    
    return member_data, payment_history, balance_days

def main():
    st.title("💳 Member Portal")
    st.markdown("### Manage Your Insurance Account")
    
    # Member Login/Selection
    if 'member_logged_in' not in st.session_state:
        st.session_state.member_logged_in = False
    
    if not st.session_state.member_logged_in:
        st.subheader("🔐 Member Login")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            login_method = st.radio(
                "Login with:",
                ["Phone Number", "Member ID", "ID Number"]
            )
            
            if login_method == "Phone Number":
                credential = st.text_input("Phone Number", value="+254")
            elif login_method == "Member ID":
                credential = st.text_input("Member ID", placeholder="M001")
            else:
                credential = st.text_input("ID Number", placeholder="12345678")
        
        with col2:
            st.write("")  # Spacer
            st.write("")
            if st.button("Login", type="primary", use_container_width=True):
                if credential:
                    st.session_state.member_logged_in = True
                    st.session_state.member_id = credential if "M" in credential else "M001"
                    st.rerun()
                else:
                    st.error("Please enter your credentials")
        
        # Quick demo access
        st.markdown("---")
        st.write("**Quick Demo Access:**")
        if st.button("Try Demo Account", type="secondary"):
            st.session_state.member_logged_in = True
            st.session_state.member_id = "M001"
            st.rerun()
        
        return
    
    # Get member data
    if db and MODULES_AVAILABLE:
        try:
            members = db.get_all_members()
            current_member = next((m for m in members if m.get('public_id') == st.session_state.member_id), None)
            if not current_member:
                current_member, payment_history, balance_days = generate_demo_member_data(st.session_state.member_id)
        except:
            current_member, payment_history, balance_days = generate_demo_member_data(st.session_state.member_id)
    else:
        current_member, payment_history, balance_days = generate_demo_member_data(st.session_state.member_id)
    
    # Member Header
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader(f"Welcome, {current_member.get('name', 'Member')}!")
        st.write(f"**Member ID:** {current_member.get('public_id', 'N/A')}")
        st.write(f"**Cover:** {current_member.get('cover_type', '').title()} Cover")
    
    with col2:
        status = current_member.get('status', 'Active')
        status_color = "🟢" if status == "Active" else "🟡" if status == "Inactive" else "🔴"
        st.metric("Status", f"{status_color} {status}")
    
    with col3:
        days_color = "🟢" if balance_days >= 0 else "🔴"
        st.metric("Balance Days", f"{days_color} {balance_days}")
    
    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "💰 Make Payment", "👨‍👩‍👧‍👦 Family", "📜 History"])
    
    with tab1:
        # Coverage Summary
        st.subheader("🛡️ Coverage Summary")
        
        summary_cols = st.columns(4)
        with summary_cols[0]:
            st.metric("Daily Premium", f"KES {current_member.get('daily_premium', 200)}")
        with summary_cols[1]:
            st.metric("Family Covered", len(current_member.get('family_members', [])))
        with summary_cols[2]:
            reg_date = current_member.get('registration_date', datetime.now())
            if isinstance(reg_date, str):
                reg_date = datetime.fromisoformat(reg_date)
            days_member = (datetime.now() - reg_date).days
            st.metric("Member For", f"{days_member} days")
        with summary_cols[3]:
            total_paid = sum(p.get('amount', 0) for p in payment_history)
            st.metric("Total Paid", f"KES {total_paid:,}")
        
        # Coverage Status
        st.subheader("📈 Coverage Timeline")
        
        if balance_days >= 0:
            st.success(f"✅ Your coverage is ACTIVE for the next {balance_days} day(s)")
            next_payment = datetime.now() + timedelta(days=balance_days + 1)
            st.info(f"⏰ Next payment due: {next_payment.strftime('%B %d, %Y')}")
        else:
            st.error(f"⚠️ Your coverage is INACTIVE. You are {abs(balance_days)} day(s) in arrears")
            amount_needed = abs(balance_days) * current_member.get('daily_premium', 200)
            st.warning(f"💳 Need to pay KES {amount_needed:,} to restore coverage")
            
            # Quick payment button
            if st.button("🔄 Restore Coverage Now", type="primary"):
                st.success(f"Redirecting to payment of KES {amount_needed:,}...")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        action_cols = st.columns(4)
        with action_cols[0]:
            if st.button("📱 Top Up", use_container_width=True):
                st.session_state.active_tab = "💰 Make Payment"
                st.rerun()
        with action_cols[1]:
            if st.button("👨‍👩‍👧‍👦 Add Family", use_container_width=True):
                st.session_state.active_tab = "👨‍👩‍👧‍👦 Family"
                st.rerun()
        with action_cols[2]:
            if st.button("📋 Update Details", use_container_width=True):
                st.info("Contact agent to update personal details")
        with action_cols[3]:
            if st.button("📄 Get Certificate", use_container_width=True):
                st.success("Insurance certificate generated!")
                st.download_button(
                    "Download PDF",
                    data=b"Demo certificate content",
                    file_name=f"certificate_{current_member.get('public_id')}.pdf",
                    mime="application/pdf"
                )
    
    with tab2:
        st.subheader("💰 Make Payment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Payment Options**")
            
            payment_method = st.radio(
                "Choose method:",
                ["M-Pesa", "Bank Transfer", "Agent Payment", "Card"]
            )
            
            if payment_method == "M-Pesa":
                st.info("""
                **M-Pesa Instructions:**
                1. Go to Lipa na M-Pesa
                2. Select PayBill
                3. Business: 123456
                4. Account: Your Member ID
                5. Enter Amount
                6. Enter PIN
                """)
            
            amount = st.number_input(
                "Amount (KES)",
                min_value=current_member.get('daily_premium', 200),
                value=current_member.get('daily_premium', 200) * 7,
                step=current_member.get('daily_premium', 200)
            )
            
            days_to_pay = int(amount / current_member.get('daily_premium', 200))
            
            if st.button("💳 Process Payment", type="primary", use_container_width=True):
                st.success(f"✅ Payment of KES {amount:,} processed!")
                st.info(f"Coverage extended by {days_to_pay} day(s)")
                new_balance = balance_days + days_to_pay
                st.metric("New Balance Days", new_balance)
        
        with col2:
            st.write("**Payment Calculator**")
            
            days = st.slider("How many days to pay for?", 1, 90, 7)
            calculated_amount = days * current_member.get('daily_premium', 200)
            
            st.metric("Amount to Pay", f"KES {calculated_amount:,}")
            st.metric("Days Covered", days)
            
            if balance_days < 0:
                days_needed = abs(balance_days)
                amount_needed = days_needed * current_member.get('daily_premium', 200)
                st.warning(f"**Catch Up Needed:** {days_needed} days = KES {amount_needed:,}")
            
            # Recurring payment
            st.markdown("---")
            st.write("**💫 Set Up Auto-Pay**")
            auto_frequency = st.selectbox(
                "Auto-pay frequency",
                ["Disabled", "Daily", "Weekly", "Monthly"]
            )
            
            if auto_frequency != "Disabled":
                st.success(f"Auto-pay enabled: {auto_frequency}")
                st.caption("Payments will be deducted automatically")
    
    with tab3:
        st.subheader("👨‍👩‍👧‍👦 Family Members")
        
        family_members = current_member.get('family_members', [])
        
        if family_members:
            for i, member in enumerate(family_members, 1):
                with st.expander(f"{i}. {member.get('name')} - {member.get('relationship').title()}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Date of Birth:** {member.get('dob', 'N/A')}")
                        st.write(f"**Coverage:** {'✅ Active' if current_member.get('status') == 'Active' else '❌ Inactive'}")
                    with col2:
                        st.write(f"**Added:** {current_member.get('registration_date', datetime.now()).strftime('%Y-%m-%d')}")
                        st.write(f"**Premium:** Included in family cover")
            
            st.metric("Total Family Members", len(family_members))
        else:
            st.info("No family members added yet")
        
        # Add family member
        st.markdown("---")
        st.subheader("➕ Add Family Member")
        
        with st.form("add_family"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                name = st.text_input("Full Name")
            with col2:
                relationship = st.selectbox("Relationship", ["Spouse", "Child", "Parent", "Other"])
            with col3:
                dob = st.date_input("Date of Birth")
            
            if st.form_submit_button("Add Family Member"):
                if name:
                    st.success(f"Added {name} as {relationship}")
                    # In real app, this would save to database
    
    with tab4:
        st.subheader("📜 Payment History")
        
        if payment_history:
            history_df = pd.DataFrame(payment_history)
            history_df['date'] = pd.to_datetime(history_df['date'])
            history_df = history_df.sort_values('date', ascending=False)
            
            st.dataframe(
                history_df.style.format({
                    'amount': 'KES {:,.0f}',
                    'date': lambda x: x.strftime('%Y-%m-%d %H:%M')
                }),
                use_container_width=True
            )
            
            # Summary
            total_paid = history_df['amount'].sum()
            total_days = history_df['days'].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Paid", f"KES {total_paid:,}")
            with col2:
                st.metric("Total Days", total_days)
            with col3:
                avg_daily = total_paid / total_days if total_days > 0 else 0
                st.metric("Avg Daily", f"KES {avg_daily:,.0f}")
        else:
            st.info("No payment history found")
    
    # Logout
    st.markdown("---")
    if st.button("🚪 Logout", type="secondary"):
        st.session_state.member_logged_in = False
        st.rerun()

if __name__ == "__main__":
    main()