# services/payment_service.py
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from models.payment import PaymentBalance, PaymentTransaction
from services.sms_service import SMSService
from config.settings import APP_CONFIG

class PaymentService:
    """Service for managing premium payments and balances"""
    
    def __init__(self, db: Session):
        self.db = db
        self.sms_service = SMSService()
        self.daily_rate = APP_CONFIG.DAILY_PREMIUM_RATE
    
    def calculate_balance(self, member_id: int) -> int:
        """Calculate day-based balance (+3 or -3 days)"""
        balance = self.db.query(PaymentBalance).filter(
            PaymentBalance.member_id == member_id
        ).first()
        
        if not balance:
            return 0
        
        # If last payment was made, calculate days since
        if balance.last_payment_date:
            days_since_last = (datetime.utcnow() - balance.last_payment_date).days
            # Adjust balance based on days since last payment
            new_balance = balance.balance_days - days_since_last
            balance.balance_days = max(new_balance, -APP_CONFIG.GRACE_PERIOD_DAYS)
            self.db.commit()
        
        return balance.balance_days
    
    def add_payment(self, member_id: int, amount: float, days_paid: int = None):
        """Record a payment"""
        if days_paid is None:
            days_paid = int(amount / self.daily_rate)
        
        balance = self.db.query(PaymentBalance).filter(
            PaymentBalance.member_id == member_id
        ).first()
        
        if not balance:
            balance = PaymentBalance(
                member_id=member_id,
                balance_days=days_paid,
                last_payment_date=datetime.utcnow(),
                total_paid=amount
            )
            self.db.add(balance)
        else:
            balance.balance_days += days_paid
            balance.last_payment_date = datetime.utcnow()
            balance.total_paid += amount
        
        # Record transaction
        transaction = PaymentTransaction(
            member_id=member_id,
            amount=amount,
            days_paid=days_paid,
            transaction_date=datetime.utcnow(),
            payment_method="M-Pesa"  # Default, can be changed
        )
        self.db.add(transaction)
        
        self.db.commit()
        
        # Update member status if needed
        self._update_member_status(member_id)
        
        return balance.balance_days
    
    def _update_member_status(self, member_id: int):
        """Update member status based on balance"""
        from models.member import Member
        
        balance = self.calculate_balance(member_id)
        member = self.db.query(Member).filter(Member.id == member_id).first()
        
        if not member:
            return
        
        if balance >= 0:
            member.status = "Active"
        elif balance >= -APP_CONFIG.GRACE_PERIOD_DAYS:
            member.status = "Inactive"
        else:
            member.status = "Suspended"
        
        self.db.commit()
    
    def send_reminder(self, member_id: int):
        """Send payment reminder SMS"""
        from models.member import Member
        
        member = self.db.query(Member).filter(Member.id == member_id).first()
        if not member:
            return
        
        balance = self.calculate_balance(member_id)
        
        if balance >= 0:
            return  # No reminder needed
        
        # Get family info
        from models.family import FamilyMember
        family = self.db.query(FamilyMember).filter(
            FamilyMember.member_id == member_id,
            FamilyMember.is_active == True
        ).all()
        
        # Prepare message
        if balance == 0:
            return  # No arrears
        
        amount_needed = abs(balance) * self.daily_rate
        
        if balance >= -7:  # Within grace period
            message = f"Hello {member.name}, your medical cover for today is NOT active. "
            if family:
                spouse = next((f for f in family if f.relationship == 'spouse'), None)
                if spouse:
                    message += f"You, {self._decrypt_name(spouse.name_encrypted)}, "
            message += f"and your children are currently NOT covered for hospital visits. "
            message += f"Pay KES {amount_needed} now to restore protection immediately."
        else:
            message = f"Habari {member.name}, you are currently {balance} days in arrears. "
            message += f"To access the hospital today, you need to catch up. "
            message += f"Pay KES {amount_needed} now to clear your debt and activate your account."
        
        # Send SMS
        self.sms_service.send_sms(member.phone_number, message)
        
        # Update next reminder date
        balance_record = self.db.query(PaymentBalance).filter(
            PaymentBalance.member_id == member_id
        ).first()
        
        if balance_record:
            balance_record.next_reminder_date = datetime.utcnow() + timedelta(days=1)
            self.db.commit()
    
    def _decrypt_name(self, encrypted_name):
        """Helper to decrypt names for SMS"""
        from services.encryption_service import EncryptionService
        enc_service = EncryptionService()
        return enc_service.decrypt(encrypted_name)
    
    def process_daily_reminders(self):
        """Process all daily reminders (to be run at 13:00)"""
        # Get all members with negative balance
        balances = self.db.query(PaymentBalance).filter(
            PaymentBalance.balance_days < 0
        ).all()
        
        for balance in balances:
            self.send_reminder(balance.member_id)