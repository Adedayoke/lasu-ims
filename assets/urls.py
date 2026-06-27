from django.urls import path
from . import views

app_name = 'assets'

urlpatterns = [
    path('', views.asset_list, name='list'),
    path('register/', views.asset_register, name='register'),
    path('import/', views.csv_import, name='csv_import'),
    path('print-queue/', views.print_queue, name='print_queue'),
    path('print-queue/pdf/', views.print_queue_pdf, name='print_queue_pdf'),
    path('lookup/', views.asset_lookup, name='lookup'),
    path('<str:asset_id>/', views.asset_detail, name='detail'),
    path('<str:asset_id>/edit/', views.asset_edit, name='edit'),
    path('<str:asset_id>/barcode/', views.barcode_image, name='barcode_image'),
    path('<str:asset_id>/condemn/', views.condemn_asset, name='condemn'),
    path('<str:asset_id>/label-pdf/', views.asset_label_pdf, name='label_pdf'),
]
