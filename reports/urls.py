from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('stock/', views.stock_report, name='stock'),
    path('audit-log/', views.audit_log, name='audit_log'),
    path('reconciliation/', views.reconciliation, name='reconciliation'),
    path('export/', views.export_centre, name='export_centre'),
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]
