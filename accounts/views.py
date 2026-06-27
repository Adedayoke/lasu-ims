from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, ForcePasswordChangeForm
from core.models import AuditLog


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            AuditLog.objects.create(
                user=user,
                action=f'User {user.username} logged in',
                model_name='User',
                object_id=str(user.pk),
                ip_address=_get_ip(request),
            )
            if user.must_change_password:
                return redirect('accounts:force_password_change')
            return redirect(request.GET.get('next', 'dashboard:home'))

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    AuditLog.objects.create(
        user=request.user,
        action=f'User {request.user.username} logged out',
        model_name='User',
        object_id=str(request.user.pk),
        ip_address=_get_ip(request),
    )
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
def force_password_change(request):
    if not request.user.must_change_password:
        return redirect('dashboard:home')

    form = ForcePasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        user.must_change_password = False
        user.save(update_fields=['must_change_password'])
        update_session_auth_hash(request, user)
        messages.success(request, 'Password updated. Welcome to LASU IMS.')
        return redirect('dashboard:home')

    return render(request, 'accounts/change_password.html', {'form': form, 'forced': True})


@login_required
def change_password(request):
    form = ForcePasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password changed successfully.')
        return redirect('dashboard:home')
    return render(request, 'accounts/change_password.html', {'form': form, 'forced': False})


def _get_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')
