"""
Access control decorators and mixins for MediScan.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def approved_required(view_func):
    """Allow only authenticated AND approved users."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_approved:
            messages.error(request, '⏳ Your account is pending admin approval.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Allow only admin-role users."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_approved:
            messages.error(request, '⏳ Your account is pending admin approval.')
            return redirect('login')
        if request.user.role != 'admin':
            messages.error(request, '🔒 Admin access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_client_ip(request) -> str:
    """Extract client IP from request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')
