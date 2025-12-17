from django.urls import path
from .views import (
    RegisterView, LoginView,  
    ResendOTPView, VerifyOTPView, PasswordResetRequestView, 
    PasswordResetConfirmationView, LogoutAPIView,UserDetailUpdateDeleteView
)
from rest_framework_simplejwt.views import (TokenRefreshView,)

urlpatterns = [
    
    # Accounts Api Endpoints
    
    path('register/', RegisterView.as_view(), name='register'),
    path('users/', UserDetailUpdateDeleteView.as_view(), name='user-list'),
    path('user/<uuid:pk>/', UserDetailUpdateDeleteView.as_view(), name='user-detail-update-delete'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('otp/resend/', ResendOTPView.as_view(), name='otp_resend'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmationView.as_view(), name='password_reset_confirm'),
   
]