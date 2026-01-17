# services/ocr_service.py - WORKING VERSION
from PIL import Image
import io
import re
from datetime import datetime
import pytesseract
import cv2
import numpy as np

class OCRService:
    """Service for extracting data from ID photos"""
    
    def __init__(self):
        # Try to find Tesseract path
        try:
            # Common Windows paths
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break
        except:
            pass
    
    def extract_id_details(self, image_file):
        """Extract details from ID/DL photo"""
        
        try:
            # Read image
            if hasattr(image_file, 'read'):
                image = Image.open(io.BytesIO(image_file.read()))
            else:
                image = Image.open(image_file)
            
            # Convert to OpenCV format if available
            try:
                open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
                gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                
                # Extract text with OCR
                text = pytesseract.image_to_string(gray)
            except:
                # Fallback: use PIL directly
                text = pytesseract.image_to_string(image)
            
            # Parse extracted text
            details = self._parse_id_text(text)
            
            return details
            
        except Exception as e:
            # Return empty details if OCR fails
            print(f"OCR Error: {e}")
            return {
                "name": "",
                "id_number": "",
                "dob": None,
                "gender": "",
                "extraction_confidence": 0.0
            }
    
    def _parse_id_text(self, text):
        """Parse OCR text to extract ID details"""
        details = {
            "name": "",
            "id_number": "",
            "dob": None,
            "gender": "",
            "extraction_confidence": 0.5
        }
        
        if not text:
            return details
        
        # Patterns for Kenyan ID
        id_pattern = r'\b\d{8,10}\b'
        name_pattern = r'Name[:\s]+([A-Z][A-Z\s]+[A-Z])'
        dob_pattern = r'(?:DOB|Date of Birth)[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{4})'
        gender_pattern = r'(Male|Female|M|F)'
        
        # Extract ID number
        id_matches = re.findall(id_pattern, text)
        if id_matches:
            details["id_number"] = id_matches[0]
            details["extraction_confidence"] = 0.7
        
        # Extract name
        name_match = re.search(name_pattern, text, re.IGNORECASE)
        if name_match:
            details["name"] = name_match.group(1).strip()
        else:
            # Try alternative patterns
            name_patterns = [
                r'Name\s*[:]?\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'([A-Z][A-Z\s]{3,}[A-Z])'  # All caps names
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, text)
                if match:
                    details["name"] = match.group(1).strip()
                    break
        
        # Extract date of birth
        dob_match = re.search(dob_pattern, text, re.IGNORECASE)
        if dob_match:
            dob_str = dob_match.group(1)
            try:
                details["dob"] = datetime.strptime(dob_str, "%d/%m/%Y")
            except:
                try:
                    details["dob"] = datetime.strptime(dob_str, "%d-%m-%Y")
                except:
                    pass
        
        # Extract gender
        gender_match = re.search(gender_pattern, text, re.IGNORECASE)
        if gender_match:
            gender = gender_match.group(1).upper()
            if gender in ['MALE', 'M']:
                details["gender"] = 'Male'
            elif gender in ['FEMALE', 'F']:
                details["gender"] = 'Female'
        
        return details
    
    def validate_id_number(self, id_number):
        """Validate Kenyan ID number format"""
        if not id_number or not isinstance(id_number, str):
            return False
        
        id_number = id_number.strip()
        
        if not id_number.isdigit():
            return False
        
        if len(id_number) not in [8, 9, 10]:
            return False
        
        return True

# For backward compatibility
ocr_service = OCRService()