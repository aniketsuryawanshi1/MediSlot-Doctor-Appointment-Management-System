from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from django.core.validators import validate_email
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils import timezone


""" User Register Service """
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['id','username', 'email', 'password', 'password2', 'first_name', 'last_name', 'role', "is_verified"]

    """Validate fields for user registration"""

    # Validate username.
    def validate_username(self, value):
        if not value.isalnum():
            raise serializers.ValidationError("Username should only contain letters and numbers.")
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    # Validate email.
    def validate_email(self, value):
        try:
            validate_email(value)
        except serializers.ValidationError:
            raise serializers.ValidationError("Invalid email format.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    # Validate first name.
    def validate_first_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("First name should only contain alphabets.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters long.")
        return value.strip()

    # Validate last name.
    def validate_last_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("Last name should only contain alphabets.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters long.")
        return value.strip()

    # Validate role - FIXED to match ROLES in models.py
    def validate_role(self, value):
        allowed_roles = ['is_doctor', 'is_superuser', 'is_patient']
        if value not in allowed_roles:
            raise serializers.ValidationError(f"Role must be one of {allowed_roles}.")
        return value

    # Validate password and password2.
    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Validate password strength
        validate_password(password)
        return data

    # Create user instance.
    def create(self, validated_data):
        validated_data.pop('password2')  # Remove password2 before user creation

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data['role'],
            # is_verified Passed as False by default for handle email verification manually from frontend.
            is_verified=validated_data.get('is_verified', True)
        )
        return user

"""Update User Service"""
class UpdateUserSerializer(serializers.ModelSerializer):
    last_login = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'password', 'last_login']

    def get_last_login(self, obj):
        if obj.last_login:
            local_dt = timezone.localtime(obj.last_login)
            return local_dt.strftime("%d-%m-%Y %H:%M")
        return None

    def validate_email(self, value):
        user = self.instance
        if User.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value

    def validate_username(self, value):
        user = self.instance
        if User.objects.exclude(id=user.id).filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)

        password = validated_data.get('password', None)
        if password:
            validate_password(password)
            instance.set_password(password)

        instance.save()
        return instance
    

""" User Login """
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(max_length=255, read_only=True)
    full_name = serializers.CharField(max_length=255, read_only=True)
    role = serializers.CharField(max_length=20, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed('No account found with this email.')

        user = authenticate(username=user.username, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again.')

        if not user.is_verified:
            raise AuthenticationFailed('User is not verified. Please verify your email.')

        if not user.is_active:
            raise AuthenticationFailed('This account is inactive. Contact support.')

        tokens = user.tokens()

        return {
            'email': user.email,
            'username': user.username,
            'full_name': user.get_full_name,  
            'role': user.role, 
            'access_token': tokens.get('access'),
            'refresh_token': tokens.get('refresh'),
        }
        
""" User Logout """
class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Token is expired or invalid.'
    }

    def validate(self, attrs):
        self.token = attrs['refresh_token']
        return attrs

    def save(self, **kwargs):
        try:
            refresh_token = RefreshToken(self.token)
            refresh_token.blacklist()
        except TokenError:
            self.fail('bad_token')

""" OTP Resend Service """
class OTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

""" OTP Verification service"""
class VerifyOTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)

""" Password reset request service"""
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

""" Password reset confirm service """
class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)
    token = serializers.CharField(max_length=255, write_only=True)
    uidb64 = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        fields = ['id','password', 'password2', 'token', 'uidb64']
        
    
    """ Password Validation """
    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        token = data.get('token')
        uidb64 = data.get('uidb64')

        if password != password2:
            raise serializers.ValidationError('Passwords do not match.')
        
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Reset link is invalid or has expired", 401)
            
            data['user'] = user

            return data
        
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid User.")
        except Exception:
            raise AuthenticationFailed("Link is invalid or has expired")
        
    """ Save Password in Database"""
    def save(self, **kwargs):
        user = self.validated_data['user']
        password = self.validated_data['password']

        user.set_password(password)
        user.save()

        return user