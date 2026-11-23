from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import home_view, download_resume_view, custom_404_view, custom_500_view
from portal.views import portal_login_view, portal_logout_view, dashboard_view

# Configure Django Admin Branding
admin.site.site_header = "Abhiram Anil // Infrastructure NOC & Security Admin"
admin.site.site_title = "NOC Operations Portal"
admin.site.index_title = "Infrastructure & Portfolio Control Center"

urlpatterns = [
    # 1. Block and intercept default Django admin login, replacing with custom NOC GUI Portal
    path('admin/login/', portal_login_view, name='admin_login_redirect'),
    path('admin/logout/', portal_logout_view, name='admin_logout_redirect'),
    path('admin/', dashboard_view, name='admin_root_dashboard'),

    # 2. Obfuscated low-level Django ORM admin (accessible only if required)
    path('sys-admin/', admin.site.urls),

    # 3. NOC Operations Portal & CMS
    path('portal/', include('portal.urls', namespace='portal')),

    # 4. Public Portfolio Routes
    path('', home_view, name='home'),
    path('resume/download/', download_resume_view, name='download_resume'),
    path('portfolio/', include('portfolio.urls', namespace='portfolio')),
    path('lab/', include('lab.urls', namespace='lab')),
    path('journal/', include('journal.urls', namespace='journal')),
    path('contact/', include('contact.urls', namespace='contact')),
]

# Error Handlers
handler404 = 'core.views.custom_404_view'
handler500 = 'core.views.custom_500_view'

# Static & Media handling during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
