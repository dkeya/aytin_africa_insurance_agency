# pages/04_📱_USSD_Interface.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys

# Add path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="USSD/SMS Interface - AYTIN AFRICA",
    page_icon="📱",
    layout="wide"
)

def main():
    st.title("📱 USSD/SMS Interface")
    st.markdown("### Access Insurance Services Without a Smartphone")
    
    # Introduction
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **For Members Without Smartphones:**
        
        📞 **Dial:** *789#
        
        📱 **Available Services:**
        1. Register for insurance
        2. Check balance
        3. Make payment
        4. Add family members
        5. Check coverage status
        """)
    
    with col2:
        st.success("""
        **How It Works:**
        
        1. Dial **\\*789#** from any phone
        2. Follow the voice/SMS prompts
        3. Complete registration via SMS
        4. Receive confirmation
        5. Start paying daily premiums
        
        **No smartphone needed!**
        """)
    
    st.markdown("---")
    
    # USSD Flow Simulation
    st.subheader("🎮 USSD Flow Simulator")
    
    tab1, tab2, tab3 = st.tabs(["📝 Registration", "💰 Payments", "📊 Status"])
    
    with tab1:
        st.markdown("### Registration via USSD")
        
        with st.form("ussd_registration"):
            st.write("**Step 1:** Dial *789#")
            st.write("**Step 2:** Select '1' for New Registration")
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Your Name (via SMS)")
                id_number = st.text_input("ID Number")
            
            with col2:
                phone = st.text_input("Phone Number", value="+254")
                dob = st.date_input("Date of Birth")
            
            st.write("**Step 3:** Select cover type")
            cover = st.selectbox(
                "Cover Type",
                ["Basic - KES 150/day", "Standard - KES 200/day", "Premium - KES 300/day"]
            )
            
            if st.form_submit_button("Simulate USSD Registration"):
                st.success(f"✅ SMS Registration Complete for {name}!")
                st.info(f"Cover: {cover}")
                st.warning("📲 Confirmation SMS sent to your phone")
    
    with tab2:
        st.markdown("### Payments via USSD")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("""**M-Pesa Payment:**

            1. Dial *789#
            2. Select '3' for Payments
            3. Enter amount
            4. Confirm M-Pesa PIN
            5. Receive confirmation

            **Daily Premium:** KES 200
            **Weekly:** KES 1,400
            **Monthly:** KES 6,000""")
       
        with col2:
            with st.form("ussd_payment"):
                st.write("**Make a Payment**")
                amount = st.number_input("Amount (KES)", min_value=100, value=200, step=100)
                days = st.slider("Number of days", 1, 30, 1)
                phone = st.text_input("M-Pesa Number", value="+254")
                
                if st.form_submit_button("Simulate Payment"):
                    total = amount * days
                    st.success(f"✅ Payment of KES {total:,} simulated!")
                    st.info(f"Covered for {days} day(s)")
    
    with tab3:
        st.markdown("### Check Status via USSD")
        
        with st.form("ussd_status"):
            st.write("**Check Your Coverage**")
            member_id = st.text_input("Member ID or Phone", placeholder="M001 or +254...")
            
            if st.form_submit_button("Check Status"):
                # Simulate status check
                import random
                statuses = ["Active", "Active", "Active", "Inactive", "Suspended"]
                balance = random.randint(-3, 5)
                
                st.success(f"📊 Status for {member_id}:")
                st.write(f"**Coverage:** {random.choice(statuses)}")
                st.write(f"**Balance Days:** {balance} {'overpaid' if balance > 0 else 'in arrears' if balance < 0 else 'current'}")
                st.write(f"**Daily Premium:** KES 200")
                
                if balance < 0:
                    amount_needed = abs(balance) * 200
                    st.warning(f"⚠️ You need to pay KES {amount_needed} to restore coverage")
    
    st.markdown("---")
    
    # SMS Gateway Setup
    st.subheader("⚙️ SMS Gateway Configuration")
    
    with st.expander("Configure SMS Service"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Africa's Talking Setup:**")
            api_key = st.text_input("API Key", type="password")
            sender_id = st.text_input("Sender ID", value="AYTININS")
            shortcode = st.text_input("Short Code", value="22384")
        
        with col2:
            st.write("**SMS Templates:**")
            registration_sms = st.text_area(
                "Registration SMS",
                value="Welcome {name}! Your AYTIN insurance is active. Member ID: {member_id}. Daily: KES {amount}. Dial *789# for services."
            )
            payment_sms = st.text_area(
                "Payment Confirmation",
                value="Payment received! {name}, KES {amount} for {days} days. New balance: {balance} days. Cover active until {date}."
            )
        
        if st.button("Save SMS Configuration", type="primary"):
            st.success("SMS configuration saved!")
    
    # Statistics
    st.markdown("---")
    st.subheader("📈 USSD/SMS Statistics")
    
    stats_cols = st.columns(4)
    with stats_cols[0]:
        st.metric("USSD Users", "1,247", "+12 this week")
    with stats_cols[1]:
        st.metric("SMS Registrations", "892", "71% of total")
    with stats_cols[2]:
        st.metric("USSD Payments", "KES 245,800", "+8%")
    with stats_cols[3]:
        st.metric("Avg Session", "2.4 min", "-0.1 min")
    
    # Help Section
    st.markdown("---")
    st.subheader("❓ Need Help?")
    
    help_cols = st.columns(3)
    with help_cols[0]:
        st.write("**Common Issues:**")
        st.write("• Can't dial *789#? Use SMS: REG to 22384")
        st.write("• Payment failed? Check M-Pesa balance")
        st.write("• No confirmation? Wait 5 minutes")
    
    with help_cols[1]:
        st.write("**Contact Support:**")
        st.write("📞 Call: 0700 000 000")
        st.write("📧 Email: support@aytinafrica.co.ke")
        st.write("💬 WhatsApp: +254 700 000 000")
    
    with help_cols[2]:
        st.write("**Business Hours:**")
        st.write("Monday - Friday: 8AM - 6PM")
        st.write("Saturday: 9AM - 1PM")
        st.write("Sunday: Emergency only")

if __name__ == "__main__":
    main()