from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.maintenance_list, name='list'),
    path('report/', views.report_maintenance, name='report'),
    path('condemned/', views.condemned_list, name='condemned'),
    path('<int:pk>/', views.maintenance_detail, name='detail'),
    path('<int:pk>/update/', views.maintenance_update, name='update'),
]
