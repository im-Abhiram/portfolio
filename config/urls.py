from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core.views import home_view, download_resume_view, custom_404_view, custom_500_view

# Configure Django Admin Branding
admin.site.site_header = "Abhiram Anil // Infrastructure NOC & Security Admin"
admin.site.site_title = "NOC Operations Portal"
admin.site.index_title = "Infrastructure & Portfolio Control Center"

urlpatterns = [
    path('admin/', admin.site.urls),
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
