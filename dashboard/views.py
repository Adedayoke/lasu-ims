from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from core.models import Asset, Requisition, Transaction, MaintenanceLog, AuditLog, Department


@login_required
def home(request):
    user = request.user
    role = user.role

    if role == 'store_officer':
        return _store_officer_dashboard(request)
    elif role == 'hod':
        return _hod_dashboard(request)
    elif role == 'auditor':
        return _auditor_dashboard(request)
    elif role == 'bursar':
        return _bursar_dashboard(request)
    else:  # superadmin
        return _superadmin_dashboard(request)


def _store_officer_dashboard(request):
    assets = Asset.objects.all()
    context = {
        'role_template': 'dashboard/store_officer.html',
        'total_assets': assets.count(),
        'in_store': assets.filter(status='in_store').count(),
        'issued': assets.filter(status='active').count(),
        'under_repair': assets.filter(status='under_repair').count(),
        'condemned': assets.filter(status='condemned').count(),
        'recent_transactions': Transaction.objects.select_related('asset', 'performed_by', 'to_department').order_by('-created_at')[:10],
        'pending_requisitions': Requisition.objects.filter(status='submitted').order_by('-created_at')[:5],
    }
    from core.models import AssetCategory
    low_stock = []
    for cat in AssetCategory.objects.all():
        count = Asset.objects.filter(category=cat, status='in_store').count()
        if count < 5:
            low_stock.append({'category': cat, 'count': count})
    context['low_stock'] = low_stock[:6]
    return render(request, 'dashboard/base_dashboard.html', context)


def _hod_dashboard(request):
    dept = request.user.department
    assets = Asset.objects.filter(department=dept) if dept else Asset.objects.none()
    context = {
        'role_template': 'dashboard/hod.html',
        'dept': dept,
        'total_assets': assets.count(),
        'active': assets.filter(status='active').count(),
        'in_store': assets.filter(status='in_store').count(),
        'under_repair': assets.filter(status='under_repair').count(),
        'dept_assets': assets.order_by('-updated_at')[:10],
        'dept_requisitions': Requisition.objects.filter(department=dept).order_by('-created_at')[:5] if dept else [],
    }
    return render(request, 'dashboard/base_dashboard.html', context)


def _auditor_dashboard(request):
    context = {
        'role_template': 'dashboard/auditor.html',
        'total_assets': Asset.objects.count(),
        'active': Asset.objects.filter(status='active').count(),
        'in_store': Asset.objects.filter(status='in_store').count(),
        'under_repair': Asset.objects.filter(status='under_repair').count(),
        'condemned': Asset.objects.filter(status='condemned').count(),
        'lost': Asset.objects.filter(status='lost').count(),
        'recent_audit': AuditLog.objects.select_related('user').order_by('-timestamp')[:15],
    }
    return render(request, 'dashboard/base_dashboard.html', context)


def _bursar_dashboard(request):
    total_value = Asset.objects.exclude(status='condemned').aggregate(v=Sum('purchase_cost'))['v'] or 0
    condemned_value = Asset.objects.filter(status='condemned').aggregate(v=Sum('purchase_cost'))['v'] or 0
    current_year = timezone.now().year

    dept_values = (
        Department.objects.annotate(
            asset_value=Sum('assets__purchase_cost', filter=Q(assets__purchase_cost__isnull=False))
        ).values('name', 'asset_value').order_by('-asset_value')[:8]
    )

    context = {
        'role_template': 'dashboard/bursar.html',
        'total_value': total_value,
        'condemned_value': condemned_value,
        'total_assets': Asset.objects.count(),
        'assets_this_year': Asset.objects.filter(created_at__year=current_year).count(),
        'assets_last_year': Asset.objects.filter(created_at__year=current_year - 1).count(),
        'dept_values': list(dept_values),
    }
    return render(request, 'dashboard/base_dashboard.html', context)


def _superadmin_dashboard(request):
    from django.contrib.sessions.models import Session
    from accounts.models import User

    active_sessions = Session.objects.filter(expire_date__gte=timezone.now()).count()
    current_year = timezone.now().year

    dept_values = (
        Department.objects.annotate(
            asset_value=Sum('assets__purchase_cost', filter=Q(assets__purchase_cost__isnull=False))
        ).values('name', 'asset_value').order_by('-asset_value')[:8]
    )

    context = {
        'role_template': 'dashboard/superadmin.html',
        'total_assets': Asset.objects.count(),
        'active': Asset.objects.filter(status='active').count(),
        'in_store': Asset.objects.filter(status='in_store').count(),
        'under_repair': Asset.objects.filter(status='under_repair').count(),
        'condemned': Asset.objects.filter(status='condemned').count(),
        'total_value': Asset.objects.aggregate(v=Sum('purchase_cost'))['v'] or 0,
        'total_users': User.objects.count(),
        'active_sessions': active_sessions,
        'recent_audit': AuditLog.objects.select_related('user').order_by('-timestamp')[:10],
        'pending_requisitions': Requisition.objects.filter(status='submitted').count(),
        'recent_transactions': Transaction.objects.select_related('asset', 'performed_by').order_by('-created_at')[:8],
        'dept_values': list(dept_values),
        'assets_this_year': Asset.objects.filter(created_at__year=current_year).count(),
        'assets_last_year': Asset.objects.filter(created_at__year=current_year - 1).count(),
    }
    return render(request, 'dashboard/base_dashboard.html', context)
