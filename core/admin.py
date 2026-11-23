from django.contrib import admin
from .models import PortfolioSettings


@admin.register(PortfolioSettings)
class PortfolioSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'noc_status_text', 'location_label', 'resume_download_name')
    fieldsets = (
        ('Branding & System HUD', {
            'fields': ('site_title', 'brand_tagline', 'noc_status_text', 'location_label')
        }),
        ('Resume Document', {
            'fields': ('resume_file', 'resume_download_name')
        }),
        ('Section Toggles', {
            'fields': (
                'show_lab_section',
                'show_journal_section',
                'show_terminal_feature',
                'show_certifications',
                'show_activity_wall'
            )
        }),
    )

    def has_add_permission(self, request):
        # Enforce singleton
        return not PortfolioSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
