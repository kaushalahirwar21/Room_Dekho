from django.urls import path
from .views import (
    SignupView, VerifyOTPView, LoginView,
    ForgotPasswordView, ResetPasswordView,
    AdminUserListView, AdminBanUserView
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-users'),
    path('admin/ban-user/<int:pk>/', AdminBanUserView.as_view(), name='admin-ban-user'),
]
