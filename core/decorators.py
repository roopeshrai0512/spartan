"""Permission decorators for granular admin access."""
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def admin_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_admin_role:
            messages.error(request, "Admin access required.")
            return redirect("core:dashboard")
        return view(request, *args, **kwargs)
    return wrapper


def super_admin_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        if not request.user.is_super_admin:
            messages.error(request, "Super Admin access required.")
            return redirect("core:dashboard")
        return view(request, *args, **kwargs)
    return wrapper


def perm_required(perm_attr):
    """Require a specific granular permission flag (e.g. 'can_add_member')."""
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")
            if not request.user.is_admin_role:
                messages.error(request, "Admin access required.")
                return redirect("core:dashboard")
            if request.user.is_super_admin or getattr(request.user, perm_attr, False):
                return view(request, *args, **kwargs)
            messages.error(request, "You don't have permission to perform that action. Ask the Super Admin to grant access.")
            return redirect("core:admin_dashboard")
        return wrapper
    return decorator
