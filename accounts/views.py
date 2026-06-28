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
                
                if not otp_obj.is_valid():
                    return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
                
                if otp_obj.otp_code == otp_code:
                    user.is_verified = True
                    user.save()
                    otp_obj.delete()
                    tokens = get_tokens_for_user(user)
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
                return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
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
                
                if not otp_obj or not otp_obj.is_valid() or otp_obj.otp_code != otp_code:
                    return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
                
                user.set_password(new_password)
                user.save()
                otp_obj.delete()
                return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

