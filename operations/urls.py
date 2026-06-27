from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    path('issue/', views.issue, name='issue'),
    path('return/', views.return_asset, name='return'),
    path('transfer/', views.transfer, name='transfer'),
    path('history/', views.history, name='history'),
]
