from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def superadmin_required(view_func):
    return role_required('superadmin')(view_func)


def store_officer_required(view_func):
    return role_required('superadmin', 'store_officer')(view_func)


def hod_required(view_func):
    return role_required('superadmin', 'hod')(view_func)


def auditor_required(view_func):
    return role_required('superadmin', 'auditor')(view_func)
