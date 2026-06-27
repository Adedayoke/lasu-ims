import csv
import io
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils import timezone
from django.conf import settings

from core.models import Asset, AssetCategory, Department, AuditLog
from accounts.models import User
from .forms import AssetForm, CSVImportForm


def _get_ip(request):
    x = request.META.get('HTTP_X_FORWARDED_FOR')
    return x.split(',')[0].strip() if x else request.META.get('REMOTE_ADDR', '')


@login_required
def asset_list(request):
    qs = Asset.objects.select_related('category', 'department', 'custodian').order_by('-created_at')

    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    category = request.GET.get('category', '')
    department = request.GET.get('department', '')

    if q:
        qs = qs.filter(
            Q(asset_id__icontains=q) | Q(name__icontains=q) |
            Q(serial_number__icontains=q) | Q(barcode_number__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)
    if category:
        qs = qs.filter(category_id=category)
    if department:
        qs = qs.filter(department_id=department)

    # HODs only see their own dept
    if request.user.role == 'hod' and request.user.department:
        qs = qs.filter(department=request.user.department)

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page,
        'categories': AssetCategory.objects.all(),
        'departments': Department.objects.all(),
        'status_choices': Asset.STATUS_CHOICES,
        'current_filters': {'q': q, 'status': status, 'category': category, 'department': department},
    }
    return render(request, 'assets/list.html', context)


@login_required
def asset_detail(request, asset_id):
    asset = get_object_or_404(Asset, asset_id=asset_id)
    if request.user.role == 'hod' and request.user.department and asset.department != request.user.department:
        raise PermissionDenied
    transactions = asset.transactions.select_related('performed_by', 'to_department', 'from_department').order_by('-created_at')
    maintenance = asset.maintenance_logs.order_by('-reported_at')
    in_print_queue = request.session.get('print_queue', [])
    return render(request, 'assets/detail.html', {
        'asset': asset,
        'transactions': transactions,
        'maintenance_logs': maintenance,
        'in_print_queue': asset.asset_id in in_print_queue,
    })


@login_required
def asset_register(request):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied

    form = AssetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        asset = form.save(commit=False)
        asset.created_by = request.user
        asset._current_user = request.user
        asset.save()
        AuditLog.objects.create(
            user=request.user,
            action=f'Registered new asset {asset.asset_id} — {asset.name}',
            model_name='Asset',
            object_id=str(asset.pk),
            ip_address=_get_ip(request),
        )
        messages.success(request, f'Asset {asset.asset_id} registered successfully.')
        return redirect('assets:detail', asset_id=asset.asset_id)

    return render(request, 'assets/register.html', {'form': form})


@login_required
def asset_edit(request, asset_id):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied
    asset = get_object_or_404(Asset, asset_id=asset_id)
    form = AssetForm(request.POST or None, instance=asset)
    if request.method == 'POST' and form.is_valid():
        asset = form.save(commit=False)
        asset._current_user = request.user
        asset.save()
        AuditLog.objects.create(
            user=request.user,
            action=f'Updated asset {asset.asset_id} — {asset.name}',
            model_name='Asset',
            object_id=str(asset.pk),
            ip_address=_get_ip(request),
        )
        messages.success(request, f'Asset {asset.asset_id} updated.')
        return redirect('assets:detail', asset_id=asset.asset_id)
    return render(request, 'assets/edit.html', {'form': form, 'asset': asset})


@login_required
def barcode_image(request, asset_id):
    asset = get_object_or_404(Asset, asset_id=asset_id)
    if asset.barcode_image:
        with open(asset.barcode_image.path, 'rb') as f:
            return HttpResponse(f.read(), content_type='image/png')
    return HttpResponse(status=404)


@login_required
def print_queue(request):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied
    queue = request.session.get('print_queue', [])
    if request.method == 'POST':
        action = request.POST.get('action')
        asset_id = request.POST.get('asset_id')
        if action == 'add' and asset_id:
            if asset_id not in queue:
                queue.append(asset_id)
            request.session['print_queue'] = queue
            messages.success(request, f'Added {asset_id} to print queue.')
        elif action == 'remove' and asset_id:
            queue = [x for x in queue if x != asset_id]
            request.session['print_queue'] = queue
        elif action == 'clear':
            request.session['print_queue'] = []
            queue = []
            messages.success(request, 'Print queue cleared.')
        return redirect(request.META.get('HTTP_REFERER', 'assets:print_queue'))

    assets = Asset.objects.filter(asset_id__in=queue) if queue else []
    return render(request, 'assets/print_queue.html', {'assets': assets, 'queue': queue})


@login_required
def condemn_asset(request, asset_id):
    if request.user.role not in ('superadmin',):
        raise PermissionDenied
    asset = get_object_or_404(Asset, asset_id=asset_id)
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, 'A reason is required to condemn an asset.')
            return redirect('assets:detail', asset_id=asset_id)

        from core.models import Transaction
        Transaction.objects.create(
            asset=asset,
            transaction_type='condemned',
            condition_before=asset.condition,
            condition_after='poor',
            notes=reason,
            performed_by=request.user,
        )
        asset.status = 'condemned'
        asset.custodian = None
        asset._current_user = request.user
        asset.save()

        AuditLog.objects.create(
            user=request.user,
            action=f'Condemned asset {asset.asset_id} — Reason: {reason[:100]}',
            model_name='Asset',
            object_id=str(asset.pk),
            ip_address=_get_ip(request),
        )
        messages.warning(request, f'Asset {asset.asset_id} has been condemned.')
        return redirect('assets:detail', asset_id=asset_id)

    return render(request, 'assets/condemn.html', {'asset': asset})


@login_required
def csv_import(request):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied

    form = CSVImportForm(request.POST or None, request.FILES or None)
    errors = []
    imported = 0

    if request.method == 'POST' and form.is_valid():
        f = form.cleaned_data['csv_file']
        try:
            decoded = f.read().decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(decoded))
            for i, row in enumerate(reader, start=2):
                try:
                    cat, _ = AssetCategory.objects.get_or_create(name=row.get('category', 'General').strip())
                    dept, _ = Department.objects.get_or_create(
                        name=row.get('department', 'General').strip(),
                        defaults={'code': row.get('department', 'GEN').strip()[:20]},
                    )
                    asset = Asset(
                        name=row['name'].strip(),
                        category=cat,
                        department=dept,
                        status=row.get('status', 'in_store').strip() or 'in_store',
                        condition=row.get('condition', 'good').strip() or 'good',
                        serial_number=row.get('serial_number', '').strip(),
                        supplier_name=row.get('supplier_name', '').strip(),
                        location_description=row.get('location', '').strip(),
                        notes=row.get('notes', '').strip(),
                        created_by=request.user,
                    )
                    cost = row.get('purchase_cost', '').strip()
                    if cost:
                        try:
                            asset.purchase_cost = float(cost.replace(',', ''))
                        except ValueError:
                            pass
                    purchase_date = row.get('purchase_date', '').strip()
                    if purchase_date:
                        from datetime import date as ddate
                        try:
                            parts = purchase_date.split('-')
                            asset.purchase_date = ddate(int(parts[0]), int(parts[1]), int(parts[2]))
                        except Exception:
                            pass
                    asset.save()
                    imported += 1
                except Exception as e:
                    errors.append(f'Row {i}: {e}')
        except Exception as e:
            errors.append(str(e))

        if imported:
            messages.success(request, f'Imported {imported} asset(s) successfully.')
        if errors:
            messages.warning(request, f'{len(errors)} row(s) failed. See details below.')

    return render(request, 'assets/csv_import.html', {'form': form, 'errors': errors, 'imported': imported})


def _pdf_link_callback(uri, rel):
    """Resolve static/media URLs to absolute file paths for xhtml2pdf."""
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri[len(settings.MEDIA_URL):])
        return path
    if uri.startswith(settings.STATIC_URL):
        rel_path = uri[len(settings.STATIC_URL):]
        for d in getattr(settings, 'STATICFILES_DIRS', []):
            path = os.path.join(str(d), rel_path)
            if os.path.isfile(path):
                return path
        if settings.STATIC_ROOT:
            path = os.path.join(str(settings.STATIC_ROOT), rel_path)
            if os.path.isfile(path):
                return path
    return uri


def _render_label_pdf(request, assets):
    try:
        from xhtml2pdf import pisa
    except ImportError:
        return HttpResponse('xhtml2pdf is not installed.', status=500)

    assets_list = list(assets)
    if len(assets_list) % 2 == 1:
        assets_list.append(None)
    label_rows = [assets_list[i:i + 2] for i in range(0, len(assets_list), 2)]

    html = render(request, 'assets/label_pdf.html', {
        'label_rows': label_rows,
        'generated_at': timezone.now(),
    }).content.decode('utf-8')

    buf = io.BytesIO()
    pisa.CreatePDF(html, dest=buf, link_callback=_pdf_link_callback)
    buf.seek(0)
    return buf


@login_required
def print_queue_pdf(request):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied
    queue = request.session.get('print_queue', [])
    assets = Asset.objects.filter(asset_id__in=queue).select_related('department', 'category') if queue else []
    buf = _render_label_pdf(request, assets)
    if isinstance(buf, HttpResponse):
        return buf
    ts = timezone.now().strftime('%Y%m%d_%H%M')
    response = HttpResponse(buf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="lasu_labels_{ts}.pdf"'
    return response


@login_required
def asset_label_pdf(request, asset_id):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied
    asset = get_object_or_404(Asset, asset_id=asset_id)
    buf = _render_label_pdf(request, [asset])
    if isinstance(buf, HttpResponse):
        return buf
    response = HttpResponse(buf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="label_{asset_id}.pdf"'
    return response


@login_required
def asset_lookup(request):
    """AJAX endpoint: look up asset by barcode number."""
    barcode = request.GET.get('barcode', '').strip()
    if not barcode:
        return HttpResponse('<p class="text-muted">Enter a barcode to search.</p>')
    try:
        asset = Asset.objects.select_related('department', 'custodian', 'category').get(barcode_number=barcode)
        return render(request, 'assets/partials/asset_card.html', {'asset': asset})
    except Asset.DoesNotExist:
        try:
            asset = Asset.objects.select_related('department', 'custodian', 'category').get(asset_id=barcode)
            return render(request, 'assets/partials/asset_card.html', {'asset': asset})
        except Asset.DoesNotExist:
            return HttpResponse('<p class="text-danger" style="padding:8px 0;">No asset found for that barcode.</p>')
