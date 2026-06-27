from django.contrib import admin
from .models import Department, AssetCategory, Asset, Requisition, RequisitionItem, Transaction, MaintenanceLog, AuditLog


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'faculty', 'hod']
    search_fields = ['name', 'code']


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'depreciation_rate']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_id', 'name', 'category', 'department', 'status', 'condition']
    list_filter = ['status', 'condition', 'category', 'department']
    search_fields = ['asset_id', 'name', 'serial_number', 'barcode_number']
    readonly_fields = ['asset_id', 'barcode_number', 'barcode_image', 'qr_code_image', 'created_at', 'updated_at']


@admin.register(Requisition)
class RequisitionAdmin(admin.ModelAdmin):
    list_display = ['req_number', 'requested_by', 'department', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'department']


admin.site.register(RequisitionItem)
admin.site.register(Transaction)
admin.site.register(MaintenanceLog)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'user', 'action', 'model_name', 'ip_address']
    list_filter = ['model_name']
    search_fields = ['action', 'user__username']
    readonly_fields = ['timestamp', 'user', 'action', 'model_name', 'object_id', 'ip_address']
