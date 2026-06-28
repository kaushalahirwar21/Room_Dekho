import logging
import smtplib
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def _send(subject, message, recipient_list):
        """
        Base helper method to send emails securely.
        Returns a tuple: (success: bool, status_message: str)
        """
        sender = settings.EMAIL_HOST_USER or 'noreply@roomdekho.com'
        
        # If in debug mode, print the email details to the terminal
        if settings.DEBUG:
            print("\n" + "="*60)
            print(f"✉ SENDING EMAIL via {settings.EMAIL_BACKEND}")
            print(f"FROM: {sender}")
            print(f"TO: {', '.join(recipient_list)}")
            print(f"SUBJECT: {subject}")
            print(f"BODY:\n{message}")
            print("="*60 + "\n")

        try:
            # Check if email settings are missing in non-debug mode
            if not settings.DEBUG and not settings.EMAIL_HOST_USER:
                error_msg = "SMTP configuration error: EMAIL_HOST_USER is not set."
                logger.error(error_msg)
                return False, error_msg

            send_mail(
                subject=subject,
                message=message,
                from_email=sender,
                recipient_list=recipient_list,
                fail_silently=False, # Raise errors so we can catch and report them
            )
            logger.info(f"Email sent successfully to {recipient_list}")
            return True, "Email sent successfully."
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "SMTP Authentication failed. Please check your EMAIL_HOST_USER and EMAIL_HOST_PASSWORD."
            logger.error(error_msg)
            return False, error_msg
        except smtplib.SMTPConnectError:
            error_msg = "Failed to connect to SMTP Server. Please check your EMAIL_HOST, EMAIL_PORT, and TLS settings."
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    @classmethod
    def send_otp_email(cls, user_email, user_name, otp_code):
        subject = "Verify Your Email - Room Dekho"
        message = (
            f"Hello {user_name},\n\n"
            f"Thank you for registering on Room Dekho!\n\n"
            f"Your 6-digit email verification OTP is:\n"
            f"👉 {otp_code}\n\n"
            f"This OTP is valid for 5 minutes.\n\n"
            f"Best regards,\n"
            f"Room Dekho Team"
        )
        return cls._send(subject, message, [user_email])

    @classmethod
    def send_forgot_password_otp(cls, user_email, user_name, otp_code):
        subject = "Reset Your Room Dekho Password"
        message = (
            f"Hello {user_name},\n\n"
            f"We received a request to reset your password for your Room Dekho account.\n\n"
            f"Your OTP is:\n"
            f"👉 {otp_code}\n\n"
            f"This OTP is valid for 5 minutes.\n\n"
            f"If you did not request a password reset, you can safely ignore this email.\n\n"
            f"Regards,\n"
            f"Room Dekho Team"
        )
        return cls._send(subject, message, [user_email])

    @classmethod
    def send_password_reset_confirmation(cls, user_email, user_name):
        subject = "Password Changed Successfully - Room Dekho"
        message = (
            f"Hello {user_name},\n\n"
            f"This is a confirmation that the password for your Room Dekho account has been changed successfully.\n\n"
            f"If you did not make this change, please contact our support team immediately.\n\n"
            f"Best regards,\n"
            f"Room Dekho Team"
        )
        return cls._send(subject, message, [user_email])

    @classmethod
    def send_booking_notification(cls, owner_email, owner_name, seeker_name, seeker_email, seeker_mobile, property_title, property_location, property_price):
        subject = f"New Booking Inquiry for {property_title} - Room Dekho"
        message = (
            f"Hello {owner_name},\n\n"
            f"You have received a new booking inquiry for your property:\n\n"
            f"🏠 Title: {property_title}\n"
            f"📍 Location: {property_location}\n"
            f"💰 Price: Rs. {property_price}/month\n\n"
            f"Seeker Details:\n"
            f"👤 Name: {seeker_name}\n"
            f"✉️ Email: {seeker_email}\n"
            f"📞 Mobile: {seeker_mobile}\n\n"
            f"Please log in to your dashboard to review and approve/reject this request.\n\n"
            f"Regards,\n"
            f"Room Dekho Team"
        )
        return cls._send(subject, message, [owner_email])

    @classmethod
    def send_welcome_email(cls, user_email, user_name):
        subject = "Welcome to Room Dekho!"
        message = (
            f"Hello {user_name},\n\n"
            f"Welcome to Room Dekho, Bhopal's leading broker-free room rental marketplace!\n\n"
            f"Your account is now fully verified. You can search for rooms, bookmark your favorites, and connect with owners directly.\n\n"
            f"Thank you for choosing Room Dekho!\n\n"
            f"Regards,\n"
            f"Room Dekho Team"
        )
        return cls._send(subject, message, [user_email])

    @classmethod
    def send_property_approval(cls, owner_email, owner_name, property_title):
        subject = "Property Listing Approved - Room Dekho"
        message = (
            f"Hello {owner_name},\n\n"
            f"Great news! Your property listing '{property_title}' has been reviewed and approved by our team.\n"
            f"It is now active on the platform and visible to seekers.\n\n"
            f"Thank you for listing with us!\n\n"
            f"Regards,\n"
            f"Room Dekho Team"
        )
        return cls._send(subject, message, [owner_email])

    @classmethod
    def send_test_email(cls, recipient_email):
        subject = "SMTP Configuration Test - Room Dekho"
        message = (
            f"Hello,\n\n"
            f"This is a test email from Room Dekho to verify your SMTP configuration.\n\n"
            f"If you are reading this, your email settings are configured correctly and working!\n\n"
            f"Regards,\n"
            f"Room Dekho Team"
        )
        return cls._send(subject, message, [recipient_email])
