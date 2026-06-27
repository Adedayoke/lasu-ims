from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('users/', views.users, name='users'),
    path('users/new/', views.user_create, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/toggle/', views.user_deactivate, name='user_deactivate'),
    path('departments/', views.departments, name='departments'),
    path('departments/new/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('settings/', views.settings_view, name='settings'),
]
