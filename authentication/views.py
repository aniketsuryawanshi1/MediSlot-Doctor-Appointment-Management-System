from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import User, OTP, OTPRequestTracker
from .serializers import (
    RegisterSerializer, LoginSerializer, OTPSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    LogoutSerializer,
    VerifyOTPSerializer,UpdateUserSerializer
)
from .utils import generate_otp, send_email
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.db.models import Q
from django.utils import timezone

class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            otp = OTP.objects.create(user=user, otp=generate_otp())

            send_email(
                "Your OTP Code",
                f"Hello {user.username}, \n\nYour OTP code is {otp.otp}. It expires in 150 seconds.",
                to_email=user.email
            )

            return Response({'message': 'User registered. Please verify your OTP.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserDetailUpdateDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(User, pk=pk)

    def get(self, request, pk=None):
        """Get all users if admin, else get own profile. Supports search."""
        if request.user.role == 'is_admin' and pk is None:
            search = request.query_params.get('search', '').strip()
            users = User.objects.all()
            if search:
                users = users.filter(
                    Q(username__icontains=search) |
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(role__icontains=search)
                )
            serializer = UpdateUserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # If not admin, user can view only own details
        if str(request.user.pk) == str(pk) or request.user.role == 'is_admin':
            user = self.get_object(pk)
            serializer = UpdateUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({'detail': 'You do not have permission to view this user.'}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk):
        """Only admin can update user"""
        if request.user.role == 'is_admin':
            user = self.get_object(pk)
            serializer = UpdateUserSerializer(user, data=request.data, partial=True)

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({'message': 'User updated successfully.', 'user': serializer.data}, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'detail': 'You do not have permission to update this user.'}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, pk):
        """Only admin can delete user"""
        if request.user.role == 'is_admin':
            user = self.get_object(pk)
            user.delete()
            return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

        return Response({'detail': 'You do not have permission to delete this user.'}, status=status.HTTP_403_FORBIDDEN)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            validated_data = serializer.validated_data
            login_message = "User logged in successfully"

            # Update last_login field
            user = User.objects.get(email=validated_data["email"])
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])

            response_data = {"message": login_message, **validated_data}
            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            otp_code = serializer.validated_data['otp']

            try:
                otp_instance = OTP.objects.get(otp=otp_code)
                user = otp_instance.user  # direct access

                print("user : ", user.email)  # .email to log properly

                if otp_instance.is_expired():
                    return Response({'error': 'OTP has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)

                if otp_instance.otp == otp_code:
                    user.is_verified = True
                    user.save()

                    otp_instance.is_verified = True
                    otp_instance.save()

                    return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

            except OTP.DoesNotExist:
                return Response({'error': "Invalid OTP or already verified"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'message': 'User logged out successfully'}, status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ResendOTPView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer =  OTPSerializer(data = request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email = email).first()
            if user:
                otp_tracker, _ = OTPRequestTracker.objects.get_or_create(user = user)

                if otp_tracker.can_request_otp():
                    OTP.objects.filter(user = user , is_verified = False).delete()

                    """ Generate OTP and update counter """
                    otp = OTP.objects.create(user = user, otp = generate_otp())

                    otp_tracker.increment_request_count()

                    """ Sending Email """
                    send_email(
                        subject = 'Your OTP Code.',
                        message = f"Hello {user.username}, \n\nYour OTP code is {otp.otp}. It expires in 150 seconds.",
                        to_email=user.email
                    )

                    return Response({'message' : 'OTP resent to your email. '}, status = status.HTTP_200_OK)
                else:
                    return Response(
                        {'error' : "Maximum OTP resend attempts exceeded. Try again after 24 hours."},
                        status = status.HTTP_429_TOO_MANY_REQUESTS
                    )

            else:
                return Response(
                    {'error' : "User with this email does not exist."}, status = status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(
                serializer.errors, status = status.HTTP_400_BAD_REQUEST
            )

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                relative_link = reverse(
                    'password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token}
                )
                abslink = f"http://localhost:5173{relative_link}"
                print("gmail link : ", abslink)
                send_email(
                    'Password Reset Request',
                    f'Hello {user.username}, \n\nUse this link to reset your password: {abslink}. The link expires in 15 minutes.',
                    user.email
                )
                return Response({'message': 'Password reset link sent to your email.'}, status=status.HTTP_200_OK)
            return Response({'error': "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmationView(APIView):
    permission_classes = [AllowAny]

    def post(self,request, uidb64, token):
        data = {
            'uidb64' : uidb64,
            'token' : token,
            'password' : request.data.get('password'),
            'password2' : request.data.get('password2')

        }

        serializer = PasswordResetConfirmSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message' : 'Password reset successful.'}, status = status.HTTP_200_OK)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)