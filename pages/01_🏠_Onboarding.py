# pages/01_🏠_Onboarding.py - FIXED VERSION
import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
import io
from PIL import Image
import tempfile

# Import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import local modules
try:
    from services.ocr_service import OCRService
    from services.encryption_service import EncryptionService
    from services.pdf_service import PDFService
    from config.settings import APP_CONFIG
    from config.database import db
    MODULES_AVAILABLE = True
except ImportError as e:
    MODULES_AVAILABLE = False
    # Create minimal fallbacks
    class OCRService:
        def extract_id_details(self, image_file):
            return {"name": "", "id_number": "", "dob": None, "gender": "", "extraction_confidence": 0.0}
    
    class EncryptionService:
        def encrypt(self, data): return data
        def decrypt(self, data): return data
        def hash_data(self, data): return data
        def mask_id_number(self, id_number, is_super_admin=False): 
            return id_number[:3] + "****" + id_number[-1] if len(id_number) > 4 else id_number
    
    class PDFService:
        def generate_proposal_form(self, member_data, family_members=None):
            # Create a simple text file as fallback
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w')
            temp_file.write(f"Insurance Proposal for {member_data.get('name', 'Member')}\n")
            temp_file.write(f"Member ID: {member_data.get('public_id', 'N/A')}\n")
            temp_file.close()
            return temp_file.name
    
    class Config:
        COVER_OPTIONS = {
            "basic": {"name": "Basic Cover", "daily": 150, "features": ["Inpatient", "Emergency"]},
            "standard": {"name": "Standard Cover", "daily": 200, "features": ["Inpatient", "Outpatient", "Maternity"]},
            "premium": {"name": "Premium Cover", "daily": 300, "features": ["Full coverage", "Dental", "Optical"]},
            "family": {"name": "Family Cover", "daily": 500, "features": ["4 members", "Full coverage"]},
            "corporate": {"name": "Corporate Cover", "daily": 400, "features": ["Group", "Custom benefits"]}
        }
    APP_CONFIG = Config()
    db = None

st.set_page_config(
    page_title="Member Onboarding - AYTIN AFRICA",
    page_icon="📝",
    layout="wide"
)

# Initialize services
ocr_service = OCRService()
encryption_service = EncryptionService()
pdf_service = PDFService()

def initialize_session_state():
    """Initialize session state variables"""
    defaults = {
        'confirmed': False,
        'phone_verified': False,
        'cover_selected': False,
        'edit_manual': False,
        'children_count': 1,
        'member_data': {},
        'selected_cover': None,
        'registration_complete': False  # New flag
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def show_id_photo_upload():
    """Step 1: ID Photo Upload with OCR"""
    st.header("📸 Step 1: Upload ID Photo")
    
    uploaded_file = st.file_uploader(
        "Take a photo of your ID/DL",
        type=['jpg', 'jpeg', 'png'],
        help="Upload a clear photo of your National ID or Driving License"
    )
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, caption="Uploaded ID", width=300)
        
        with col2:
            if st.button("🔍 Extract ID Details", type="primary"):
                with st.spinner("Extracting details from ID..."):
                    extracted_data = ocr_service.extract_id_details(uploaded_file)
                    
                    if extracted_data and extracted_data.get("name"):
                        st.success("✅ Details extracted successfully!")
                        
                        # Display extracted data
                        st.subheader("Extracted Details:")
                        st.write(f"**Name:** {extracted_data['name']}")
                        st.write(f"**ID Number:** {extracted_data['id_number']}")
                        
                        if extracted_data['dob']:
                            dob_display = extracted_data['dob'].strftime('%d/%m/%Y') if hasattr(extracted_data['dob'], 'strftime') else str(extracted_data['dob'])
                            st.write(f"**Date of Birth:** {dob_display}")
                        
                        st.write(f"**Gender:** {extracted_data['gender']}")
                        
                        # Confirmation
                        st.header("Step 2: Confirm Your Details")
                        st.info(f"**Got it! Confirming: You are {extracted_data['name']}, "
                               f"{extracted_data['gender']}, ID {extracted_data['id_number']}. Correct?**")
                        
                        col_yes, col_no = st.columns(2)
                        
                        if col_yes.button("✅ Yes, Correct", type="primary"):
                            st.session_state.member_data = extracted_data
                            st.session_state.confirmed = True
                            st.rerun()
                        
                        if col_no.button("❌ No, Edit Manually"):
                            st.session_state.edit_manual = True
                            st.rerun()
                    else:
                        st.error("Could not extract details automatically. Please enter manually.")
                        st.session_state.edit_manual = True

def show_manual_entry():
    """Show manual entry form"""
    st.header("✍️ Step 1: Enter Details Manually")
    
    with st.form("manual_entry"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *", placeholder="John Kamau")
            id_number = st.text_input("ID Number *", placeholder="12345678")
        
        with col2:
            dob = st.date_input("Date of Birth *", min_value=datetime(1900, 1, 1))
            gender = st.selectbox("Gender *", ["Male", "Female", "Other"])
        
        if st.form_submit_button("Save Details & Continue"):
            if name and id_number:
                st.session_state.member_data = {
                    "name": name,
                    "id_number": id_number,
                    "dob": dob,
                    "gender": gender
                }
                st.session_state.confirmed = True
                st.rerun()
            else:
                st.error("Please fill in all required fields (*)")

def show_contact_verification():
    """Step 3: Contact Verification"""
    st.header("📱 Step 3: Contact Verification")
    
    member_data = st.session_state.member_data
    
    default_phone = "+254700000000"
    phone = st.text_input(
        "Phone Number *",
        value=default_phone,
        help="We'll use this number for SMS notifications and payments"
    )
    
    st.info(f"**To reach you, is this {phone} the best one for your policy?**")
    
    col_save, col_change = st.columns(2)
    
    if col_save.button("✅ Yes, Keep This", type="primary"):
        member_data['phone'] = phone
        st.session_state.phone_verified = True
        st.rerun()
    
    with col_change:
        alt_phone = st.text_input("Or enter different number:", key="alt_phone")
        if st.button("Use Different Number"):
            if alt_phone:
                member_data['phone'] = alt_phone
                st.session_state.phone_verified = True
                st.rerun()

def show_cover_selection():
    """Step 4: Cover Selection"""
    st.header("🛡️ Step 4: Select Your Cover")
    
    st.write("**What cover are you picking today?**")
    
    covers = APP_CONFIG.COVER_OPTIONS
    
    selected_cover = st.radio(
        "Choose a cover option:",
        options=list(covers.keys()),
        format_func=lambda x: f"{covers[x]['name']} - KES {covers[x]['daily']}/day",
        horizontal=False
    )
    
    if selected_cover:
        cover = covers[selected_cover]
        with st.expander(f"📋 {cover['name']} Details"):
            st.write("**Includes:**")
            for feature in cover['features']:
                st.write(f"• {feature}")
            st.write(f"**Daily Premium:** KES {cover['daily']}")
    
    if st.button("📋 Select This Cover", type="primary"):
        st.session_state.selected_cover = selected_cover
        st.session_state.cover_selected = True
        st.rerun()

def show_family_members():
    """Step 5: Family Members"""
    st.header("👨‍👩‍👧‍👦 Step 5: Add Family Members")
    
    st.write("**Would you like to add your spouse and dependants to the medical cover for extra protection?**")
    
    add_family = st.radio(
        "Add family members?",
        ["No", "Yes, add spouse only", "Yes, add spouse and children"],
        horizontal=True
    )
    
    family_members = []
    
    if "Yes" in add_family:
        # Spouse details
        st.subheader("Spouse Details")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            spouse_name = st.text_input("Spouse Full Name")
        with col2:
            spouse_dob = st.date_input("Spouse Date of Birth", key="spouse_dob")
        with col3:
            spouse_gender = st.selectbox("Spouse Gender", ["Male", "Female"], key="spouse_gender")
        
        if spouse_name:
            family_members.append({
                "relationship": "spouse",
                "name": spouse_name,
                "dob": spouse_dob,
                "gender": spouse_gender
            })
        
        # Children details
        if "children" in add_family.lower():
            st.subheader("Children Details")
            st.write("**For your children? Enter: Name, Gender, Date of Birth**")
            
            for i in range(st.session_state.children_count):
                with st.container():
                    st.markdown(f"**Child {i+1}**")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        child_name = st.text_input(f"Name", key=f"child_name_{i}")
                    with col2:
                        child_gender = st.selectbox(
                            "Gender", 
                            ["Male", "Female", "Other"],
                            key=f"child_gender_{i}"
                        )
                    with col3:
                        child_dob = st.date_input(
                            "Date of Birth",
                            key=f"child_dob_{i}"
                        )
                    
                    if child_name:
                        family_members.append({
                            "relationship": "child",
                            "name": child_name,
                            "dob": child_dob,
                            "gender": child_gender
                        })
            
            if st.button("➕ Add Another Child"):
                st.session_state.children_count += 1
                st.rerun()
    
    if st.button("✅ Complete Registration", type="primary"):
        process_registration(family_members)

def process_registration(family_members):
    """Process the final registration"""
    with st.spinner("Processing registration..."):
        try:
            member_data = st.session_state.member_data
            selected_cover = st.session_state.selected_cover
            
            # Generate member ID
            member_id = f"M{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Prepare complete record
            complete_record = {
                "public_id": member_id,
                "name": member_data['name'],
                "id_number": member_data['id_number'],
                "dob": member_data['dob'],
                "gender": member_data['gender'],
                "phone_number": member_data['phone'],
                "cover_type": selected_cover,
                "registration_date": datetime.now(),
                "status": "Active",
                "family_members": family_members
            }
            
            # Save to database if available
            database_saved = False
            if db:
                try:
                    saved_id = db.save_member(complete_record)
                    st.success(f"✅ Saved to database with ID: {saved_id}")
                    database_saved = True
                except Exception as db_error:
                    st.warning(f"⚠️ Database save skipped: {db_error}")
            
            # Generate PDF
            pdf_generated = False
            pdf_content = None
            pdf_filename = f"insurance_proposal_{member_id}.pdf"
            
            try:
                pdf_path = pdf_service.generate_proposal_form(complete_record, family_members)
                
                # Read the PDF file
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        pdf_content = f.read()
                    pdf_generated = True
                else:
                    # Create a simple text PDF as fallback
                    pdf_content = f"""
                    AYTIN AFRICA INSURANCE PROPOSAL
                    
                    Member ID: {member_id}
                    Name: {member_data['name']}
                    ID Number: {member_data['id_number']}
                    Phone: {member_data['phone']}
                    Cover: {APP_CONFIG.COVER_OPTIONS[selected_cover]['name']}
                    Daily Premium: KES {APP_CONFIG.COVER_OPTIONS[selected_cover]['daily']}
                    Registration Date: {datetime.now().strftime('%Y-%m-%d')}
                    
                    Family Members:
                    {chr(10).join(f"- {fm['name']} ({fm['relationship']})" for fm in family_members) if family_members else "None"}
                    
                    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """.encode('utf-8')
                    
            except Exception as pdf_error:
                # Create minimal PDF content
                pdf_content = f"Insurance Proposal for {member_data['name']}\nMember ID: {member_id}".encode('utf-8')
            
            # Show success message
            st.success("🎉 Registration Complete!")
            st.balloons()
            
            # Display summary
            cover_name = APP_CONFIG.COVER_OPTIONS[selected_cover]['name']
            daily_rate = APP_CONFIG.COVER_OPTIONS[selected_cover]['daily']
            
            st.markdown(f"""
            ### Welcome to AYTIN AFRICA Insurance!
            
            **Member ID:** `{member_id}`
            **Name:** {member_data['name']}
            **Phone:** {member_data['phone']}
            **Cover:** {cover_name}
            **Daily Premium:** KES {daily_rate}
            **Family Members:** {len(family_members)}
            
            Your registration has been successfully completed!
            """)
            
            # Download buttons
            col1, col2 = st.columns(2)
            
            with col1:
                # Download PDF
                if pdf_content:
                    st.download_button(
                        "📄 Download Insurance Proposal",
                        pdf_content,
                        file_name=pdf_filename,
                        mime="application/pdf" if pdf_generated else "text/plain"
                    )
            
            with col2:
                # Download Member Details
                details_content = f"""
                AYTIN AFRICA - MEMBER DETAILS
                Member ID: {member_id}
                Name: {member_data['name']}
                ID Number: {member_data['id_number']}
                Phone: {member_data['phone']}
                Cover: {cover_name}
                Daily Premium: KES {daily_rate}
                Registration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
                
                st.download_button(
                    "📝 Download Member Details",
                    details_content,
                    file_name=f"member_details_{member_id}.txt",
                    mime="text/plain"
                )
            
            # Set completion flag
            st.session_state.registration_complete = True
            
            # Don't reset session state immediately - let user download files first
            st.info("💡 **Note:** You can download your documents above. The form will reset when you navigate away.")
            
        except Exception as e:
            st.error(f"Registration error: {str(e)}")
            st.info("Please try again or contact support.")

def show_completion_screen():
    """Show completion screen after registration"""
    st.success("🎉 Registration Complete!")
    st.balloons()
    
    st.markdown("""
    ### Thank You for Choosing AYTIN AFRICA!
    
    Your registration has been successfully completed.
    
    **Next Steps:**
    1. Start paying your daily premium of KES 200
    2. Download your insurance proposal
    3. Access hospital services immediately
    4. Check your member portal for updates
    
    **Need Help?**
    - Call: 0700 000 000
    - SMS: HELP to 22384
    - Visit: Member Portal
    """)
    
    if st.button("🔄 Start New Registration", type="primary"):
        reset_session_state()
        st.rerun()

def reset_session_state():
    """Reset session state after registration"""
    keys_to_remove = [
        'confirmed', 'phone_verified', 'cover_selected',
        'edit_manual', 'member_data', 'selected_cover', 
        'children_count', 'registration_complete'
    ]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reinitialize
    initialize_session_state()

def main():
    """Main application function"""
    st.title("🏥 Member Onboarding - Medical Cover")
    st.markdown("### Complete your registration in 5 simple steps")
    
    # Check if modules are available
    if not MODULES_AVAILABLE:
        st.warning("⚠️ Some required modules are missing. Basic functionality only.")
    
    # Initialize session state
    initialize_session_state()
    
    # Check if registration is complete
    if st.session_state.get('registration_complete', False):
        show_completion_screen()
        return
    
    # Show appropriate step based on progress
    if not st.session_state.get('confirmed', False):
        show_id_photo_upload()
        show_manual_entry()
    elif not st.session_state.get('phone_verified', False):
        show_contact_verification()
    elif not st.session_state.get('cover_selected', False):
        show_cover_selection()
    else:
        show_family_members()
    
    # Progress indicator
    st.markdown("---")
    progress_cols = st.columns(5)
    steps = ["ID/Details", "Contact", "Cover", "Family", "Complete"]
    current_step = 0
    
    if st.session_state.get('confirmed', False):
        current_step = 1
    if st.session_state.get('phone_verified', False):
        current_step = 2
    if st.session_state.get('cover_selected', False):
        current_step = 3
    
    for i, (col, step) in enumerate(zip(progress_cols, steps)):
        if i <= current_step:
            col.success(f"✅ {step}")
        else:
            col.info(f"⬜ {step}")

if __name__ == "__main__":
    main()