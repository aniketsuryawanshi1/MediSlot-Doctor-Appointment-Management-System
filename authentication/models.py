
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
import uuid


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True 

AUTH_PROVIDERS = {
    'email': 'email'
}

ROLES = (
    ('is_doctor', 'Doctor'),
    ('is_superuser', 'Superuser'),
    ('is_patient', 'Patient'),
)

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError('Please provide an email address')
        if not username:
            raise ValueError('Please provide a username')
        if not role:
            raise ValueError('Please provide a user role')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, role=None, **extra_fields):
        if not role:
            raise ValueError('Superuser must have a role')
        if role != 'is_admin':
            raise ValueError('Superuser role must be "is_admin" only')

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('can_create', True)
        extra_fields.setdefault('can_update', True)
        extra_fields.setdefault('can_delete', True)
        extra_fields.setdefault('can_read', True)
        extra_fields.setdefault('is_verified', True)

        return self.create_user(username, email, password, role, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    role = models.CharField(max_length=20, choices=ROLES)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    auth_provider = models.CharField(max_length=50, default=AUTH_PROVIDERS.get('email'))
    can_create = models.BooleanField(default=False)
    can_read = models.BooleanField(default=True)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'role']

    objects = UserManager()

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def is_admin_role(self):
        return self.role == 'is_admin'

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
    )


class OTP(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        OTP_EXPIRY_TIME = timedelta(seconds=60)
        return timezone.now() > self.created_at + OTP_EXPIRY_TIME

    def __str__(self):
        return f"OTP(user = {self.user}, otp = {self.otp}, is_verified = {self.is_verified})"


class OTPRequestTracker(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_request_time = models.DateTimeField(auto_now_add=True)
    request_count = models.PositiveIntegerField(default=0)

    def reset_request_count(self):
        self.request_count = 0
        self.save()

    def can_request_otp(self):
        if self.last_request_time < timezone.now() - timedelta(hours=24):
            self.reset_request_count()
        return self.request_count < 3

    def increment_request_count(self):
        self.request_count += 1
        self.save()

    def __str__(self):
        return f"OTPRequestTracker(user = {self.user}, request_count = {self.request_count})"


class PasswordResetToken(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    token = models.CharField(max_length=64)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)

    def __str__(self):
        return f"PasswordResetToken(user = {self.user}, token = {self.token})"