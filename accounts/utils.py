import random
import hashlib
import logging
from .models import OTP
from .email_service import EmailService

logger = logging.getLogger(__name__)

def generate_and_send_otp(user):
    otp_code = str(random.randint(100000, 999999))
    
    # Hash the OTP before storing it
    hashed_otp = hashlib.sha256(otp_code.encode()).hexdigest()
    
    OTP.objects.filter(user=user).delete() # Clear old OTPs
    OTP.objects.create(user=user, otp_code=hashed_otp)
    
    # Route to appropriate email template based on user verification status
    if not user.is_verified:
        success, error_msg = EmailService.send_otp_email(user.email, user.name, otp_code)
    else:
        success, error_msg = EmailService.send_forgot_password_otp(user.email, user.name, otp_code)
        
    if not success:
        logger.error(f"Failed to dispatch OTP to {user.email}: {error_msg}")
    else:
        logger.info(f"Successfully dispatched OTP to {user.email}")
