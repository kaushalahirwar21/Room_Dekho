import hashlib
import logging
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User, OTP
from .serializers import (
    SignupSerializer, OTPSerializer, LoginSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer, UserSerializer
)
from .utils import generate_and_send_otp
from .email_service import EmailService

logger = logging.getLogger(__name__)

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                name=serializer.validated_data['name'],
                mobile_number=serializer.validated_data.get('mobile_number', ''),
                role=serializer.validated_data.get('role', 'Seeker')
            )
            generate_and_send_otp(user)
            return Response({"message": "User created successfully. Please verify your email via OTP."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            
            try:
                user = User.objects.get(email=email)
                otp_obj = OTP.objects.filter(user=user).last()
                
                if not otp_obj:
                    return Response({"error": "No OTP found."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Increment and check attempts
                otp_obj.attempts += 1
                otp_obj.save()
                
                if otp_obj.attempts > 5:
                    otp_obj.delete()
                    logger.warning(f"OTP verification blocked: Max attempts exceeded for {email}")
                    return Response({"error": "Maximum verification attempts exceeded. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)
                
                if not otp_obj.is_valid():
                    return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Verify SHA-256 hash
                hashed_input = hashlib.sha256(otp_code.encode()).hexdigest()
                if otp_obj.otp_code == hashed_input:
                    if not user.is_verified:
                        user.is_verified = True
                        user.save()
                        otp_obj.delete()
                    else:
                        # Keep the OTP for the subsequent reset-password API call to verify and delete
                        pass
                    tokens = get_tokens_for_user(user)
                    logger.info(f"Email verified successfully via OTP: {email}")
                    return Response({"message": "Email verified successfully.", "tokens": tokens, "user": UserSerializer(user).data}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
                    
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            
            if user:
                # Skip OTP for superuser (is_superuser=True)
                if user.is_superuser:
                    from django.contrib.auth import login
                    login(request, user)
                    tokens = get_tokens_for_user(user)
                    return Response({"message": "Login successful.", "tokens": tokens, "user": UserSerializer(user).data}, status=status.HTTP_200_OK)
                
                if not user.is_verified:
                    generate_and_send_otp(user)
                    return Response({"error": "Email is not verified. A new OTP has been sent."}, status=status.HTTP_403_FORBIDDEN)
                
                # Create session for standard Django Admin to work
                from django.contrib.auth import login
                login(request, user)
                
                tokens = get_tokens_for_user(user)
                return Response({"message": "Login successful.", "tokens": tokens, "user": UserSerializer(user).data}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                generate_and_send_otp(user)
            except User.DoesNotExist:
                # Log silently and proceed to prevent email enumeration
                logger.info(f"Password reset requested for non-existent email: {email}")
                
            return Response({"message": "An OTP has been sent to your registered email if it exists."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            new_password = serializer.validated_data['new_password']
            
            try:
                user = User.objects.get(email=email)
                otp_obj = OTP.objects.filter(user=user).last()
                
                if not otp_obj:
                    return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Increment and check attempts
                otp_obj.attempts += 1
                otp_obj.save()
                
                if otp_obj.attempts > 5:
                    otp_obj.delete()
                    logger.warning(f"Password reset blocked: Max attempts exceeded for {email}")
                    return Response({"error": "Maximum verification attempts exceeded. Please request a new OTP."}, status=status.HTTP_400_BAD_REQUEST)
                
                if not otp_obj.is_valid():
                    return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Verify SHA-256 hash
                hashed_input = hashlib.sha256(otp_code.encode()).hexdigest()
                if otp_obj.otp_code != hashed_input:
                    return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
                
                user.set_password(new_password)
                user.save()
                otp_obj.delete()
                logger.info(f"Password reset completed successfully for user: {email}")
                return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendTestEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Recipient email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        success, message = EmailService.send_test_email(email)
        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

import smtplib
from django.conf import settings
from rest_framework.permissions import IsAdminUser

class EmailConfigView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Return current SMTP settings from django settings
        password_masked = "••••••••" if getattr(settings, 'EMAIL_HOST_PASSWORD', None) else ""
        data = {
            "email_host": getattr(settings, 'EMAIL_HOST', 'smtp.gmail.com'),
            "email_port": getattr(settings, 'EMAIL_PORT', 587),
            "email_host_user": getattr(settings, 'EMAIL_HOST_USER', ''),
            "email_use_tls": getattr(settings, 'EMAIL_USE_TLS', True),
            "email_host_password": password_masked,
            "sender_name": "Room Dekho"
        }
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        email_host = request.data.get('email_host', 'smtp.gmail.com')
        try:
            email_port = int(request.data.get('email_port', 587))
        except ValueError:
            return Response({"error": "SMTP Port must be a valid number."}, status=status.HTTP_400_BAD_REQUEST)
            
        email_host_user = request.data.get('email_host_user', '').strip()
        email_host_password = request.data.get('email_host_password', '')
        email_use_tls = request.data.get('email_use_tls', True)

        if not email_host_user:
            return Response({"error": "Email Address is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Handle password masking
        if email_host_password == '••••••••':
            email_host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        
        if not email_host_password:
            return Response({"error": "App Password is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate SMTP settings by trying to log in
        try:
            # We use a short timeout of 5 seconds to prevent freezing
            server = smtplib.SMTP(email_host, email_port, timeout=5)
            if email_use_tls:
                server.ehlo()
                server.starttls()
                server.ehlo()
            server.login(email_host_user, email_host_password)
            server.quit()
        except smtplib.SMTPAuthenticationError:
            return Response({"error": "SMTP Authentication failed. Please check your Email Address and App Password."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"SMTP Connection failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # SMTP Validated! Now save to .env
        env_path = settings.BASE_DIR / '.env'
        key_values = {
            "EMAIL_HOST": email_host,
            "EMAIL_PORT": str(email_port),
            "EMAIL_HOST_USER": email_host_user,
            "EMAIL_HOST_PASSWORD": email_host_password,
            "EMAIL_USE_TLS": "True" if email_use_tls else "False",
        }

        try:
            lines = []
            if env_path.exists():
                with open(env_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            
            updated_keys = set()
            new_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and '=' in stripped:
                    key, val = stripped.split('=', 1)
                    key = key.strip()
                    if key in key_values:
                        new_lines.append(f"{key}={key_values[key]}\n")
                        updated_keys.add(key)
                        continue
                new_lines.append(line)
            
            for key, val in key_values.items():
                if key not in updated_keys:
                    new_lines.append(f"{key}={val}\n")
            
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

        except Exception as e:
            logger.error(f"Failed to write to .env file: {str(e)}")
            # Even if .env write fails (e.g. read-only filesystem on Vercel), we still update in-memory settings

        # Update Django settings in-memory immediately
        settings.EMAIL_HOST = email_host
        settings.EMAIL_PORT = email_port
        settings.EMAIL_HOST_USER = email_host_user
        settings.EMAIL_HOST_PASSWORD = email_host_password
        settings.EMAIL_USE_TLS = email_use_tls
        
        # If in local debug mode, force the backend to SMTP to test real emails
        if settings.DEBUG:
            settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

        return Response({"message": "Email configuration saved and verified successfully!"}, status=status.HTTP_200_OK)


from rest_framework.permissions import IsAdminUser

class AdminUserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class AdminBanUserView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.is_active = False
            user.save()
            return Response({"message": "User banned successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


from django.http import HttpResponse
from django.shortcuts import render
from rooms.models import Property

def sitemap_view(request):
    base_url = request.build_absolute_uri('/')[:-1]
    
    static_urls = [
        {'loc': f"{base_url}/", 'priority': '1.0', 'changefreq': 'daily'},
        {'loc': f"{base_url}/about/", 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': f"{base_url}/login/", 'priority': '0.5', 'changefreq': 'monthly'},
        {'loc': f"{base_url}/signup/", 'priority': '0.5', 'changefreq': 'monthly'},
        {'loc': f"{base_url}/forgot-password/", 'priority': '0.5', 'changefreq': 'monthly'},
        {'loc': f"{base_url}/privacy-policy/", 'priority': '0.3', 'changefreq': 'monthly'},
        {'loc': f"{base_url}/terms-conditions/", 'priority': '0.3', 'changefreq': 'monthly'},
    ]
    
    properties = Property.objects.all().order_by('-created_at')
    
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    for url in static_urls:
        xml_content += '  <url>\n'
        xml_content += f"    <loc>{url['loc']}</loc>\n"
        xml_content += f"    <priority>{url['priority']}</priority>\n"
        xml_content += f"    <changefreq>{url['changefreq']}</changefreq>\n"
        xml_content += '  </url>\n'
        
    for prop in properties:
        loc = f"{base_url}/property/{prop.id}/"
        lastmod = prop.created_at.strftime('%Y-%m-%d')
        xml_content += '  <url>\n'
        xml_content += f"    <loc>{loc}</loc>\n"
        xml_content += f"    <lastmod>{lastmod}</lastmod>\n"
        xml_content += '    <priority>0.9</priority>\n'
        xml_content += '    <changefreq>weekly</changefreq>\n'
        xml_content += '  </url>\n'
        
    xml_content += '</urlset>'
    
    return HttpResponse(xml_content, content_type="application/xml")

def robots_view(request):
    base_url = request.build_absolute_uri('/')[:-1]
    robots_content = "User-agent: *\n"
    robots_content += "Allow: /\n"
    robots_content += "Disallow: /admin/\n"
    robots_content += "Disallow: /dashboard/\n"
    robots_content += "Disallow: /api/\n"
    robots_content += f"\nSitemap: {base_url}/sitemap.xml\n"
    
    return HttpResponse(robots_content, content_type="text/plain")

def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)

def custom_500_view(request):
    return render(request, '500.html', status=500)
