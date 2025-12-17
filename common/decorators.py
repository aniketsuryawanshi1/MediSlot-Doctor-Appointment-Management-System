from functools import wraps
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


class AuthDecoratorSingleton:
    """Singleton for authentication checks (GOF: Singleton to share auth logic across requests)."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def check_auth(self, user):
        return user.is_authenticated


auth_singleton = AuthDecoratorSingleton()


def require_auth(view_func):
    """Decorator to ensure user is authenticated (uses Singleton for efficiency)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not auth_singleton.check_auth(request.user):
            return JsonResponse(
                {"error": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def require_role(role):
    """Decorator to check user role (e.g., 'doctor' or 'patient')."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'role') or request.user.role != role:
                return JsonResponse(
                    {"error": f"Access denied. Requires {role} role."},
                    status=status.HTTP_403_FORBIDDEN
                )
            return view_func(request, *args, **kwargs)
        return decorator
    return decorator