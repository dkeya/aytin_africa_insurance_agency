# services/pdf_service.py - WORKING VERSION
from fpdf import FPDF
from datetime import datetime
import os

class PDFService:
    """Service for generating insurance documents"""
    
    def __init__(self):
        self.template_dir = "static/templates"
        
    def generate_proposal_form(self, member_data, family_members=None):
        """Generate formal insurance proposal form PDF"""
        
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'AYTIN AFRICA INSURANCE AGENCY', 0, 1, 'C')
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, 'Insurance Proposal Form - Medical Cover', 0, 1, 'C')
        pdf.ln(5)
        
        # Member Information
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '1. Member Information', 0, 1)
        pdf.set_font('Arial', '', 12)
        
        pdf.cell(50, 10, 'Full Name:', 0, 0)
        pdf.cell(0, 10, member_data.get('name', 'N/A'), 0, 1)
        
        pdf.cell(50, 10, 'Member ID:', 0, 0)
        pdf.cell(0, 10, member_data.get('public_id', 'N/A'), 0, 1)
        
        pdf.cell(50, 10, 'Phone Number:', 0, 0)
        pdf.cell(0, 10, member_data.get('phone_number', 'N/A'), 0, 1)
        
        pdf.cell(50, 10, 'Cover Type:', 0, 0)
        pdf.cell(0, 10, member_data.get('cover_type', 'N/A'), 0, 1)
        
        pdf.cell(50, 10, 'Registration Date:', 0, 0)
        reg_date = member_data.get('registration_date', datetime.now())
        if hasattr(reg_date, 'strftime'):
            pdf.cell(0, 10, reg_date.strftime('%d/%m/%Y'), 0, 1)
        else:
            pdf.cell(0, 10, str(reg_date), 0, 1)
        
        pdf.ln(5)
        
        # Family Information
        if family_members and len(family_members) > 0:
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, '2. Family Members Covered', 0, 1)
            pdf.set_font('Arial', '', 12)
            
            for i, member in enumerate(family_members, 1):
                pdf.cell(0, 10, f'{i}. {member.get("relationship", "").title()}: {member.get("name", "N/A")}', 0, 1)
                pdf.cell(20, 10, '', 0, 0)
                
                dob = member.get('dob')
                if hasattr(dob, 'strftime'):
                    dob_str = dob.strftime('%d/%m/%Y')
                else:
                    dob_str = str(dob)
                
                pdf.cell(50, 10, f'DOB: {dob_str}', 0, 0)
                pdf.cell(50, 10, f'Gender: {member.get("gender", "N/A")}', 0, 1)
                pdf.ln(2)
        
        # Terms and Conditions
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, '3. Terms & Conditions', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        terms = [
            "1. This is a daily premium medical cover policy.",
            "2. Coverage is active only when premium payments are up to date.",
            "3. Premium rates vary by cover type (KES 150-500 per day).",
            "4. Grace period: 7 days of non-payment allowed before suspension.",
            "5. Hospital access requires active policy status.",
            "6. Claims must be submitted within 30 days of treatment.",
            "7. Policy can be cancelled with 30 days written notice."
        ]
        
        for term in terms:
            pdf.multi_cell(0, 8, term)
        
        # Footer
        pdf.ln(20)
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 10, f'Generated on: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', 0, 1, 'C')
        pdf.cell(0, 10, 'AYTIN AFRICA Insurance - https://aytinafrica.co.ke', 0, 1, 'C')
        
        # Save PDF
        os.makedirs('generated_pdfs', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        member_id = member_data.get('public_id', 'unknown')
        filename = f'generated_pdfs/proposal_{member_id}_{timestamp}.pdf'
        
        try:
            pdf.output(filename)
            return filename
        except Exception as e:
            # Fallback to simpler filename
            filename = f'generated_pdfs/proposal_{timestamp}.pdf'
            pdf.output(filename)
            return filename