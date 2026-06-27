import os
import io
from datetime import date
from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile


class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    faculty = models.CharField(max_length=200, blank=True)
    hod = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='headed_departments',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class AssetCategory(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    depreciation_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)

    class Meta:
        verbose_name_plural = 'Asset Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Asset(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('under_repair', 'Under Repair'),
        ('condemned', 'Condemned'),
        ('in_store', 'In Store'),
        ('lost', 'Lost'),
    ]
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]

    asset_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT, related_name='assets')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='assets')
    custodian = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='custodied_assets',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_store')
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='new')
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    supplier_name = models.CharField(max_length=300, blank=True)
    barcode_number = models.CharField(max_length=100, unique=True, editable=False)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True)
    qr_code_image = models.ImageField(upload_to='qrcodes/', blank=True)
    serial_number = models.CharField(max_length=200, blank=True)
    location_description = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_assets',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.asset_id} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.asset_id:
            self.asset_id = self._generate_asset_id()
        if not self.barcode_number:
            self.barcode_number = self._generate_barcode_number()
        super().save(*args, **kwargs)
        if not self.barcode_image:
            self._generate_barcode_image()
            Asset.objects.filter(pk=self.pk).update(
                barcode_image=self.barcode_image,
                qr_code_image=self.qr_code_image,
            )

    def _generate_asset_id(self):
        year = date.today().year
        last = Asset.objects.filter(asset_id__startswith=f'LASU-{year}-').order_by('-asset_id').first()
        if last:
            try:
                seq = int(last.asset_id.split('-')[-1]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f'LASU-{year}-{seq:05d}'

    def _generate_barcode_number(self):
        import random
        import string
        year = date.today().year
        rand = ''.join(random.choices(string.digits, k=8))
        return f'{year}{rand}'

    def _generate_barcode_image(self):
        try:
            import barcode
            from barcode.writer import ImageWriter

            bc = barcode.get('code128', self.barcode_number, writer=ImageWriter())
            buf = io.BytesIO()
            bc.write(buf, options={'write_text': True, 'module_height': 8, 'font_size': 6})
            buf.seek(0)
            filename = f'barcode_{self.asset_id}.png'
            self.barcode_image.save(filename, ContentFile(buf.read()), save=False)
        except Exception:
            pass

        try:
            import qrcode
            request_url = f'/assets/{self.asset_id}/'
            qr = qrcode.QRCode(version=1, box_size=4, border=2)
            qr.add_data(request_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            buf = io.BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            filename = f'qr_{self.asset_id}.png'
            self.qr_code_image.save(filename, ContentFile(buf.read()), save=False)
        except Exception:
            pass

    def get_status_badge(self):
        mapping = {
            'active': 'success',
            'under_repair': 'warning',
            'condemned': 'danger',
            'in_store': 'info',
            'lost': 'danger',
        }
        return mapping.get(self.status, 'neutral')

    def get_condition_badge(self):
        mapping = {'new': 'success', 'good': 'info', 'fair': 'warning', 'poor': 'danger'}
        return mapping.get(self.condition, 'neutral')


class Requisition(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('fulfilled', 'Fulfilled'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
    ]

    req_number = models.CharField(max_length=20, unique=True, editable=False)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='requisitions',
    )
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='requisitions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='approved_requisitions',
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    reject_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.req_number} — {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.req_number:
            self.req_number = self._generate_req_number()
        super().save(*args, **kwargs)

    def _generate_req_number(self):
        year = date.today().year
        last = Requisition.objects.filter(req_number__startswith=f'REQ-{year}-').order_by('-req_number').first()
        seq = 1
        if last:
            try:
                seq = int(last.req_number.split('-')[-1]) + 1
            except ValueError:
                pass
        return f'REQ-{year}-{seq:05d}'

    def get_status_badge(self):
        mapping = {
            'draft': 'neutral',
            'submitted': 'info',
            'approved': 'success',
            'rejected': 'danger',
            'fulfilled': 'success',
        }
        return mapping.get(self.status, 'neutral')

    def get_priority_badge(self):
        return {'low': 'neutral', 'normal': 'info', 'urgent': 'danger'}.get(self.priority, 'neutral')


class RequisitionItem(models.Model):
    requisition = models.ForeignKey(Requisition, on_delete=models.CASCADE, related_name='items')
    asset_category = models.ForeignKey(AssetCategory, on_delete=models.PROTECT)
    quantity_requested = models.PositiveIntegerField()
    quantity_approved = models.PositiveIntegerField(null=True, blank=True)
    purpose = models.TextField()

    def __str__(self):
        return f"{self.asset_category} x{self.quantity_requested}"


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('issued', 'Issued'),
        ('returned', 'Returned'),
        ('transferred', 'Transferred'),
        ('condemned', 'Condemned'),
        ('repaired', 'Repaired'),
    ]

    transaction_id = models.CharField(max_length=20, unique=True, editable=False)
    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    from_department = models.ForeignKey(
        Department, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='outgoing_transactions',
    )
    to_department = models.ForeignKey(
        Department, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='incoming_transactions',
    )
    from_custodian = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='outgoing_transactions',
    )
    to_custodian = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='incoming_transactions',
    )
    condition_before = models.CharField(max_length=10, blank=True)
    condition_after = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='performed_transactions',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_id} — {self.get_transaction_type_display()}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self._generate_txn_id()
        super().save(*args, **kwargs)

    def _generate_txn_id(self):
        year = date.today().year
        last = Transaction.objects.filter(transaction_id__startswith=f'TXN-{year}-').order_by('-transaction_id').first()
        seq = 1
        if last:
            try:
                seq = int(last.transaction_id.split('-')[-1]) + 1
            except ValueError:
                pass
        return f'TXN-{year}-{seq:05d}'

    def get_type_badge(self):
        mapping = {
            'issued': 'info',
            'returned': 'success',
            'transferred': 'warning',
            'condemned': 'danger',
            'repaired': 'success',
        }
        return mapping.get(self.transaction_type, 'neutral')


class MaintenanceLog(models.Model):
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.PROTECT, related_name='maintenance_logs')
    issue_description = models.TextField()
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='reported_maintenance',
    )
    assigned_technician = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    repair_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    repair_notes = models.TextField(blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-reported_at']

    def __str__(self):
        return f"Maintenance: {self.asset} — {self.get_status_display()}"

    def get_status_badge(self):
        mapping = {
            'reported': 'warning',
            'in_progress': 'info',
            'completed': 'success',
            'cancelled': 'neutral',
        }
        return mapping.get(self.status, 'neutral')


class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='audit_logs',
    )
    action = models.TextField()
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} — {self.action[:60]}"
