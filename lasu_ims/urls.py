from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

admin.site.site_header = 'LASU IMS Control Panel'
admin.site.site_title = 'LASU IMS'
admin.site.index_title = 'Administration'

urlpatterns = [
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
    path('lasu-control/', admin.site.urls),
    path('', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('assets/', include('assets.urls')),
    path('requisitions/', include('requisitions.urls')),
    path('operations/', include('operations.urls')),
    path('maintenance/', include('maintenance.urls')),
    path('reports/', include('reports.urls')),
    path('admin-panel/', include('admin_panel.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
