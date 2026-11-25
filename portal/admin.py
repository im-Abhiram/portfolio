from django.contrib import admin
from .models import LoginAttemptLog


@admin.register(LoginAttemptLog)
class LoginAttemptLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'ip_address', 'username_attempted', 'succeeded')
    list_filter = ('succeeded', 'created_at')
    search_fields = ('ip_address', 'username_attempted')
    readonly_fields = ('ip_address', 'username_attempted', 'succeeded', 'created_at')

    def has_add_permission(self, request):
        return False
