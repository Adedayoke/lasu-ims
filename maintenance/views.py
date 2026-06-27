from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from core.models import Asset, MaintenanceLog, Transaction, AuditLog


def _get_ip(request):
    x = request.META.get('HTTP_X_FORWARDED_FOR')
    return x.split(',')[0].strip() if x else request.META.get('REMOTE_ADDR', '')


@login_required
def maintenance_list(request):
    qs = MaintenanceLog.objects.select_related('asset', 'reported_by').order_by('-reported_at')
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'maintenance/list.html', {
        'page_obj': page,
        'status_choices': MaintenanceLog.STATUS_CHOICES,
        'current_status': status,
    })


@login_required
def report_maintenance(request):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied

    asset = None
    asset_id = request.GET.get('asset') or request.POST.get('asset_id')
    if asset_id:
        asset = Asset.objects.filter(asset_id=asset_id).first()

    if request.method == 'POST' and 'confirm' in request.POST:
        a_id = request.POST.get('asset_id')
        asset = get_object_or_404(Asset, asset_id=a_id)
        description = request.POST.get('issue_description', '').strip()
        technician = request.POST.get('assigned_technician', '').strip()

        if not description:
            messages.error(request, 'Issue description is required.')
        else:
            log = MaintenanceLog.objects.create(
                asset=asset,
                issue_description=description,
                reported_by=request.user,
                assigned_technician=technician,
                status='reported',
            )
            asset.status = 'under_repair'
            asset._current_user = request.user
            asset.save()

            AuditLog.objects.create(
                user=request.user,
                action=f'Reported maintenance for {asset.asset_id}: {description[:80]}',
                model_name='MaintenanceLog',
                object_id=str(log.pk),
                ip_address=_get_ip(request),
            )
            messages.success(request, f'Maintenance reported for {asset.asset_id}.')
            return redirect('maintenance:detail', pk=log.pk)

    return render(request, 'maintenance/report.html', {
        'asset': asset,
        'assets': Asset.objects.order_by('asset_id'),
    })


@login_required
def maintenance_detail(request, pk):
    log = get_object_or_404(MaintenanceLog.objects.select_related('asset', 'reported_by'), pk=pk)
    return render(request, 'maintenance/detail.html', {'log': log})


@login_required
def maintenance_update(request, pk):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied

    log = get_object_or_404(MaintenanceLog, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('status', log.status)
        repair_notes = request.POST.get('repair_notes', '').strip()
        technician = request.POST.get('assigned_technician', log.assigned_technician).strip()
        repair_cost = request.POST.get('repair_cost', '').strip()

        log.status = new_status
        log.repair_notes = repair_notes
        log.assigned_technician = technician
        if repair_cost:
            try:
                log.repair_cost = float(repair_cost)
            except ValueError:
                pass
        if new_status == 'completed' and not log.completed_at:
            log.completed_at = timezone.now()
        log._current_user = request.user
        log.save()

        if new_status == 'completed':
            Transaction.objects.create(
                asset=log.asset,
                transaction_type='repaired',
                condition_before='poor',
                condition_after=request.POST.get('condition_after', 'good'),
                notes=repair_notes,
                performed_by=request.user,
            )
            log.asset.status = 'in_store'
            log.asset._current_user = request.user
            log.asset.save()

        AuditLog.objects.create(
            user=request.user,
            action=f'Updated maintenance log #{log.pk} for {log.asset.asset_id} — status: {new_status}',
            model_name='MaintenanceLog',
            object_id=str(log.pk),
            ip_address=_get_ip(request),
        )
        messages.success(request, 'Maintenance log updated.')
        return redirect('maintenance:detail', pk=pk)

    return render(request, 'maintenance/update.html', {
        'log': log,
        'status_choices': MaintenanceLog.STATUS_CHOICES,
        'condition_choices': Asset.CONDITION_CHOICES,
    })


@login_required
def condemned_list(request):
    assets = Asset.objects.filter(status='condemned').select_related('category', 'department').order_by('-updated_at')
    paginator = Paginator(assets, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'maintenance/condemned.html', {'page_obj': page})
