from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from core.models import Asset, Transaction, Department, AuditLog
from accounts.models import User


def _get_ip(request):
    x = request.META.get('HTTP_X_FORWARDED_FOR')
    return x.split(',')[0].strip() if x else request.META.get('REMOTE_ADDR', '')


def _lookup_asset(val):
    try:
        return Asset.objects.select_related('department', 'custodian', 'category').get(barcode_number=val)
    except Asset.DoesNotExist:
        pass
    try:
        return Asset.objects.select_related('department', 'custodian', 'category').get(asset_id=val)
    except Asset.DoesNotExist:
        return None


@login_required
def issue(request):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied

    asset = None
    lookup_val = request.POST.get('barcode') or request.GET.get('barcode', '')
    if lookup_val:
        asset = _lookup_asset(lookup_val)

    if request.method == 'POST' and asset and 'confirm_issue' in request.POST:
        to_dept_id = request.POST.get('to_department')
        to_custodian_id = request.POST.get('to_custodian')
        notes = request.POST.get('notes', '')

        if asset.status == 'condemned':
            messages.error(request, 'Cannot issue a condemned asset.')
        else:
            to_dept = get_object_or_404(Department, pk=to_dept_id) if to_dept_id else asset.department
            to_custodian = User.objects.filter(pk=to_custodian_id).first() if to_custodian_id else None

            Transaction.objects.create(
                asset=asset,
                transaction_type='issued',
                from_department=asset.department,
                to_department=to_dept,
                from_custodian=asset.custodian,
                to_custodian=to_custodian,
                condition_before=asset.condition,
                condition_after=asset.condition,
                notes=notes,
                performed_by=request.user,
            )
            asset.status = 'active'
            asset.department = to_dept
            asset.custodian = to_custodian
            asset._current_user = request.user
            asset.save()

            AuditLog.objects.create(
                user=request.user,
                action=f'Issued asset {asset.asset_id} to {to_custodian.get_full_name() if to_custodian else to_dept.name}',
                model_name='Asset',
                object_id=str(asset.pk),
                ip_address=_get_ip(request),
            )
            messages.success(request, f'Asset {asset.asset_id} issued successfully.')
            return redirect('assets:detail', asset_id=asset.asset_id)

    context = {
        'asset': asset,
        'departments': Department.objects.order_by('name'),
        'users': User.objects.filter(is_active=True).order_by('first_name'),
        'lookup_val': lookup_val,
    }
    return render(request, 'operations/issue.html', context)


@login_required
def return_asset(request):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied

    asset = None
    lookup_val = request.POST.get('barcode') or request.GET.get('barcode', '')
    if lookup_val:
        asset = _lookup_asset(lookup_val)

    if request.method == 'POST' and asset and 'confirm_return' in request.POST:
        condition = request.POST.get('condition', asset.condition)
        notes = request.POST.get('notes', '')

        Transaction.objects.create(
            asset=asset,
            transaction_type='returned',
            from_department=asset.department,
            from_custodian=asset.custodian,
            condition_before=asset.condition,
            condition_after=condition,
            notes=notes,
            performed_by=request.user,
        )
        asset.status = 'in_store'
        asset.custodian = None
        asset.condition = condition
        asset._current_user = request.user
        asset.save()

        AuditLog.objects.create(
            user=request.user,
            action=f'Returned asset {asset.asset_id} to store',
            model_name='Asset',
            object_id=str(asset.pk),
            ip_address=_get_ip(request),
        )
        messages.success(request, f'Asset {asset.asset_id} returned to store.')
        return redirect('assets:detail', asset_id=asset.asset_id)

    context = {
        'asset': asset,
        'condition_choices': Asset.CONDITION_CHOICES,
        'lookup_val': lookup_val,
    }
    return render(request, 'operations/return.html', context)


@login_required
def transfer(request):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied

    asset = None
    lookup_val = request.POST.get('barcode') or request.GET.get('barcode', '')
    if lookup_val:
        asset = _lookup_asset(lookup_val)

    if request.method == 'POST' and asset and 'confirm_transfer' in request.POST:
        to_dept_id = request.POST.get('to_department')
        notes = request.POST.get('notes', '')
        to_dept = get_object_or_404(Department, pk=to_dept_id)

        Transaction.objects.create(
            asset=asset,
            transaction_type='transferred',
            from_department=asset.department,
            to_department=to_dept,
            from_custodian=asset.custodian,
            condition_before=asset.condition,
            condition_after=asset.condition,
            notes=notes,
            performed_by=request.user,
        )
        asset.department = to_dept
        asset._current_user = request.user
        asset.save()

        AuditLog.objects.create(
            user=request.user,
            action=f'Transferred asset {asset.asset_id} to {to_dept.name}',
            model_name='Asset',
            object_id=str(asset.pk),
            ip_address=_get_ip(request),
        )
        messages.success(request, f'Asset {asset.asset_id} transferred to {to_dept.name}.')
        return redirect('assets:detail', asset_id=asset.asset_id)

    context = {
        'asset': asset,
        'departments': Department.objects.exclude(pk=asset.department_id if asset else None).order_by('name'),
        'lookup_val': lookup_val,
    }
    return render(request, 'operations/transfer.html', context)


@login_required
def history(request):
    qs = Transaction.objects.select_related(
        'asset', 'performed_by', 'to_department', 'from_department'
    ).order_by('-created_at')

    q = request.GET.get('q', '').strip()
    txn_type = request.GET.get('type', '')

    if q:
        qs = qs.filter(Q(asset__asset_id__icontains=q) | Q(asset__name__icontains=q) | Q(transaction_id__icontains=q))
    if txn_type:
        qs = qs.filter(transaction_type=txn_type)

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'operations/history.html', {
        'page_obj': page,
        'type_choices': Transaction.TYPE_CHOICES,
        'current_filters': {'q': q, 'type': txn_type},
    })
