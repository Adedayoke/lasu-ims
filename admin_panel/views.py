from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied

from accounts.models import User
from accounts.forms import UserCreateForm, UserEditForm
from core.models import Department, AuditLog


def _superadmin_required(request):
    if request.user.role != 'superadmin':
        raise PermissionDenied


def _get_ip(request):
    x = request.META.get('HTTP_X_FORWARDED_FOR')
    return x.split(',')[0].strip() if x else request.META.get('REMOTE_ADDR', '')


@login_required
def users(request):
    _superadmin_required(request)
    qs = User.objects.select_related('department').order_by('username')
    q = request.GET.get('q', '').strip()
    if q:
        from django.db.models import Q
        qs = qs.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q))

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_panel/users.html', {'page_obj': page, 'q': q})


@login_required
def user_create(request):
    _superadmin_required(request)
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.must_change_password = True
        user.save()
        AuditLog.objects.create(
            user=request.user,
            action=f'Created user {user.username} with role {user.role}',
            model_name='User',
            object_id=str(user.pk),
            ip_address=_get_ip(request),
        )
        messages.success(request, f'User {user.username} created. They will be prompted to change their password on first login.')
        return redirect('admin_panel:users')
    return render(request, 'admin_panel/user_form.html', {'form': form, 'action': 'Create'})


@login_required
def user_edit(request, pk):
    _superadmin_required(request)
    user = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        AuditLog.objects.create(
            user=request.user,
            action=f'Updated user {user.username}',
            model_name='User',
            object_id=str(user.pk),
            ip_address=_get_ip(request),
        )
        messages.success(request, f'User {user.username} updated.')
        return redirect('admin_panel:users')
    return render(request, 'admin_panel/user_form.html', {'form': form, 'action': 'Edit', 'target_user': user})


@login_required
def user_deactivate(request, pk):
    _superadmin_required(request)
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, 'You cannot deactivate your own account.')
        else:
            user.is_active = not user.is_active
            user.save()
            verb = 'activated' if user.is_active else 'deactivated'
            AuditLog.objects.create(
                user=request.user,
                action=f'{verb.capitalize()} user {user.username}',
                model_name='User',
                object_id=str(user.pk),
                ip_address=_get_ip(request),
            )
            messages.success(request, f'User {user.username} {verb}.')
    return redirect('admin_panel:users')


@login_required
def departments(request):
    _superadmin_required(request)
    depts = Department.objects.select_related('hod').order_by('name')
    return render(request, 'admin_panel/departments.html', {'departments': depts})


@login_required
def department_create(request):
    _superadmin_required(request)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        faculty = request.POST.get('faculty', '').strip()
        hod_id = request.POST.get('hod', '')

        if not name or not code:
            messages.error(request, 'Name and code are required.')
        else:
            dept = Department.objects.create(
                name=name, code=code, faculty=faculty,
                hod=User.objects.filter(pk=hod_id).first() if hod_id else None,
            )
            messages.success(request, f'Department {dept.name} created.')
            return redirect('admin_panel:departments')

    users = User.objects.filter(is_active=True, role='hod').order_by('first_name')
    return render(request, 'admin_panel/department_form.html', {'action': 'Create', 'users': users})


@login_required
def department_edit(request, pk):
    _superadmin_required(request)
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.name = request.POST.get('name', dept.name).strip()
        dept.code = request.POST.get('code', dept.code).strip()
        dept.faculty = request.POST.get('faculty', dept.faculty).strip()
        hod_id = request.POST.get('hod', '')
        dept.hod = User.objects.filter(pk=hod_id).first() if hod_id else None
        dept.save()
        messages.success(request, f'Department {dept.name} updated.')
        return redirect('admin_panel:departments')

    hod_users = User.objects.filter(is_active=True).order_by('first_name')
    return render(request, 'admin_panel/department_form.html', {'action': 'Edit', 'dept': dept, 'users': hod_users})


@login_required
def settings_view(request):
    _superadmin_required(request)
    from accounts.models import User as UserModel
    from core.models import Asset
    from django.contrib.sessions.models import Session
    from django.utils import timezone

    context = {
        'total_users': UserModel.objects.count(),
        'active_users': UserModel.objects.filter(is_active=True).count(),
        'total_assets': Asset.objects.count(),
        'active_sessions': Session.objects.filter(expire_date__gte=timezone.now()).count(),
    }
    return render(request, 'admin_panel/settings.html', context)
