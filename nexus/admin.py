from django.contrib import admin
from .models import ChatUsageLog


@admin.register(ChatUsageLog)
class ChatUsageLogAdmin(admin.ModelAdmin):
    list_display = ('usage_date', 'ip_address', 'status', 'model_used', 'total_tokens', 'created_at')
    list_filter = ('status', 'usage_date', 'model_used')
    search_fields = ('ip_address', 'session_hash', 'model_used')
    readonly_fields = ('ip_address', 'session_hash', 'usage_date', 'status', 'model_used', 'total_tokens', 'created_at')

    def has_add_permission(self, request):
        return False
