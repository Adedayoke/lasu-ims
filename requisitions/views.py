from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from core.models import Requisition, RequisitionItem, AssetCategory, Department, AuditLog


def _get_ip(request):
    x = request.META.get('HTTP_X_FORWARDED_FOR')
    return x.split(',')[0].strip() if x else request.META.get('REMOTE_ADDR', '')


@login_required
def req_list(request):
    if request.user.role == 'hod':
        qs = Requisition.objects.filter(department=request.user.department)
    elif request.user.role == 'bursar':
        qs = Requisition.objects.all()
    else:
        qs = Requisition.objects.all()

    qs = qs.select_related('requested_by', 'department').order_by('-created_at')
    status = request.GET.get('status', '')
    if status:
        qs = qs.filter(status=status)

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'requisitions/list.html', {
        'page_obj': page,
        'status_choices': Requisition.STATUS_CHOICES,
        'current_status': status,
    })


@login_required
def req_create(request):
    if request.user.role not in ('superadmin', 'store_officer', 'hod'):
        raise PermissionDenied

    categories = AssetCategory.objects.all()
    departments = Department.objects.all()

    if request.method == 'POST':
        dept_id = request.POST.get('department')
        notes = request.POST.get('notes', '')
        priority = request.POST.get('priority', 'normal')
        submit_action = request.POST.get('submit_action', 'save')

        dept = get_object_or_404(Department, pk=dept_id)

        if request.user.role == 'hod' and request.user.department and dept != request.user.department:
            messages.error(request, 'You can only create requisitions for your department.')
            return redirect('requisitions:create')

        req = Requisition.objects.create(
            requested_by=request.user,
            department=dept,
            priority=priority,
            notes=notes,
            status='draft',
        )
        req._current_user = request.user

        # Process items
        cat_ids = request.POST.getlist('category[]')
        quantities = request.POST.getlist('quantity[]')
        purposes = request.POST.getlist('purpose[]')

        for cat_id, qty, purpose in zip(cat_ids, quantities, purposes):
            if cat_id and qty:
                try:
                    cat = AssetCategory.objects.get(pk=cat_id)
                    RequisitionItem.objects.create(
                        requisition=req,
                        asset_category=cat,
                        quantity_requested=int(qty),
                        purpose=purpose,
                    )
                except (AssetCategory.DoesNotExist, ValueError):
                    pass

        if submit_action == 'submit':
            req.status = 'submitted'
            req.save()
            AuditLog.objects.create(
                user=request.user,
                action=f'Submitted requisition {req.req_number}',
                model_name='Requisition',
                object_id=str(req.pk),
                ip_address=_get_ip(request),
            )
            messages.success(request, f'Requisition {req.req_number} submitted for approval.')
        else:
            messages.success(request, f'Requisition {req.req_number} saved as draft.')

        return redirect('requisitions:detail', pk=req.pk)

    context = {
        'categories': categories,
        'departments': departments,
        'priority_choices': Requisition.PRIORITY_CHOICES,
        'user_dept': request.user.department,
    }
    return render(request, 'requisitions/create.html', context)


@login_required
def req_detail(request, pk):
    req = get_object_or_404(Requisition.objects.select_related('requested_by', 'department', 'approved_by'), pk=pk)

    # HODs can only see their dept's requisitions
    if request.user.role == 'hod' and request.user.department and req.department != request.user.department:
        raise PermissionDenied

    if request.method == 'POST' and 'submit_req' in request.POST:
        if req.status == 'draft' and (request.user == req.requested_by or request.user.role == 'superadmin'):
            req.status = 'submitted'
            req._current_user = request.user
            req.save()
            messages.success(request, f'Requisition {req.req_number} submitted.')

    return render(request, 'requisitions/detail.html', {'req': req})


@login_required
def req_approve(request, pk):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied

    req = get_object_or_404(Requisition, pk=pk)
    if req.status != 'submitted':
        messages.error(request, 'Only submitted requisitions can be approved.')
        return redirect('requisitions:detail', pk=pk)

    if request.method == 'POST':
        req.status = 'approved'
        req.approved_by = request.user
        req.approved_at = timezone.now()
        req._current_user = request.user
        req.save()

        # Update approved quantities
        for item in req.items.all():
            qty_key = f'qty_approved_{item.pk}'
            qty = request.POST.get(qty_key)
            if qty:
                try:
                    item.quantity_approved = int(qty)
                    item.save()
                except ValueError:
                    pass

        AuditLog.objects.create(
            user=request.user,
            action=f'Approved requisition {req.req_number}',
            model_name='Requisition',
            object_id=str(req.pk),
            ip_address=_get_ip(request),
        )
        messages.success(request, f'Requisition {req.req_number} approved.')
        return redirect('requisitions:detail', pk=pk)

    return render(request, 'requisitions/approve.html', {'req': req})


@login_required
def req_reject(request, pk):
    if request.user.role not in ('superadmin', 'store_officer'):
        raise PermissionDenied

    req = get_object_or_404(Requisition, pk=pk)
    if req.status not in ('submitted', 'approved'):
        messages.error(request, 'This requisition cannot be rejected.')
        return redirect('requisitions:detail', pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        req.status = 'rejected'
        req.reject_reason = reason
        req._current_user = request.user
        req.save()

        AuditLog.objects.create(
            user=request.user,
            action=f'Rejected requisition {req.req_number} — {reason[:80]}',
            model_name='Requisition',
            object_id=str(req.pk),
            ip_address=_get_ip(request),
        )
        messages.warning(request, f'Requisition {req.req_number} rejected.')
        return redirect('requisitions:detail', pk=pk)

    return render(request, 'requisitions/reject.html', {'req': req})
