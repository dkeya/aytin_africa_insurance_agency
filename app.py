# app.py - SIMPLIFIED TEST VERSION
import streamlit as st
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AYTIN AFRICA Insurance",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    
    # Load custom CSS
    try:
        with open('static/css/custom.css', 'r') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except:
        st.info("Custom CSS not found, using default styling")
    
    # Sidebar navigation
    with st.sidebar:
        # Simple text logo instead of image
        st.markdown("# 🏥 AYTIN AFRICA")
        st.markdown("### Insurance Agency")
        st.markdown("---")
        
        # User role selection
        user_role = st.selectbox(
            "Select Your Role",
            ["Member", "Agent", "Admin"]
        )
        
        st.markdown("---")
        
        if user_role == "Member":
            st.markdown("📝 **New Registration**")
            st.markdown("💳 **Member Portal**")
        elif user_role == "Agent":
            st.markdown("👤 **Agent Dashboard**")
        else:
            st.markdown("👑 **Admin Dashboard**")
        
        st.markdown("---")
        st.caption(f"© {datetime.now().year} AYTIN AFRICA")
    
    # Main content
    st.title("🏥 Welcome to AYTIN AFRICA Insurance")
    st.markdown("### Your Partner in Clear, Accessible Insurance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **For Members**
        - Easy registration
        - Daily premium payments
        - Family coverage
        """)
    
    with col2:
        st.success("""
        **For Agents**
        - Simple registration flow
        - Track daily success
        """)
    
    with col3:
        st.warning("""
        **For Admins**
        - Full dashboard
        - Payment tracking
        """)
    
    # Quick demo buttons
    st.markdown("---")
    st.subheader("Quick Actions")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("📝 Demo Registration", type="primary"):
            st.success("Registration form would open here")
            # Simulate form
            with st.form("demo_form"):
                name = st.text_input("Full Name")
                phone = st.text_input("Phone Number")
                if st.form_submit_button("Submit"):
                    st.balloons()
                    st.success(f"Demo registration for {name} complete!")
    
    with col_b:
        if st.button("💰 Make Payment"):
            st.info("Payment system would open here")
    
    with col_c:
        if st.button("📊 View Reports"):
            st.info("Admin reports would open here")

if __name__ == "__main__":
    main()