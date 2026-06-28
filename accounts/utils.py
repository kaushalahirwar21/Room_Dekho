import random
from django.core.mail import send_mail
from django.conf import settings
from .models import OTP

def generate_and_send_otp(user):
    otp_code = str(random.randint(100000, 999999))
    OTP.objects.filter(user=user).delete() # Clear old OTPs
    OTP.objects.create(user=user, otp_code=otp_code)
    
    subject = "Your OTP for Room Dekho"
    message = f"Hello {user.name},\nYour OTP is {otp_code}. It is valid for 5 minutes.\n\nThank you,\nRoom Dekho Team"
    
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=True,  # Set to false for debug
    )
