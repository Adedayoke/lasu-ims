from django.urls import path
from . import views

app_name = 'requisitions'

urlpatterns = [
    path('', views.req_list, name='list'),
    path('new/', views.req_create, name='create'),
    path('<int:pk>/', views.req_detail, name='detail'),
    path('<int:pk>/approve/', views.req_approve, name='approve'),
    path('<int:pk>/reject/', views.req_reject, name='reject'),
]
