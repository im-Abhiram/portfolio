from django.contrib import admin
from django.utils import timezone
from .models import AISettings, ArticleGenerationLog, DailyArticle, IntelSubscriber


@admin.register(AISettings)
class AISettingsAdmin(admin.ModelAdmin):
    """Non-secret AI Settings admin. Never exposes GEMINI_API_KEY value."""
    list_display = (
        '__str__', 'chat_enabled', 'daily_article_enabled',
        'article_publish_mode', 'chat_daily_limit_per_visitor', 'api_key_status_badge'
    )
    readonly_fields = ('api_key_status_badge', 'updated_at')
    fieldsets = (
        ('API Key Health (Read-Only, Stored in Environment)', {
            'fields': ('api_key_status_badge',),
            'description': 'GEMINI_API_KEY is stored exclusively in server environment variables (.env / WSGI) and is never saved to or displayed from the database.'
        }),
        ('ramo.ai Chatbot Controls', {
            'fields': ('chat_enabled', 'chat_daily_limit_per_visitor', 'chat_rate_limit_per_minute', 'preferred_model')
        }),
        ('NETWORK INTELLIGENCE Publisher Controls', {
            'fields': ('daily_article_enabled', 'article_publish_mode', 'article_generation_timezone')
        }),
    )

    def api_key_status_badge(self, obj):
        return "CONFIGURED (Environment Variable Active)" if obj.api_key_configured else "MISSING (Set GEMINI_API_KEY in server env)"
    api_key_status_badge.short_description = "GEMINI_API_KEY Status"

    def has_add_permission(self, request):
        return not AISettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DailyArticle)
class DailyArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'scheduled_date', 'reading_time', 'is_featured', 'ai_generated', 'published_at')
    list_filter = ('status', 'category', 'is_featured', 'ai_generated', 'scheduled_date')
    search_fields = ('title', 'subtitle', 'introduction', 'tags', 'topic_key')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('generated_at', 'updated_at', 'content_hash')
    actions = ['publish_selected', 'unpublish_selected', 'archive_selected']

    def publish_selected(self, request, queryset):
        now = timezone.now()
        for article in queryset:
            article.status = 'published'
            if not article.published_at:
                article.published_at = now
            article.save()
    publish_selected.short_description = "Publish selected Network Intelligence articles"

    def unpublish_selected(self, request, queryset):
        queryset.update(status='draft', is_featured=False)
    unpublish_selected.short_description = "Move selected articles to Draft (Unpublish)"

    def archive_selected(self, request, queryset):
        queryset.update(status='archived', is_featured=False)
    archive_selected.short_description = "Archive selected articles"


@admin.register(ArticleGenerationLog)
class ArticleGenerationLogAdmin(admin.ModelAdmin):
    list_display = ('generation_date', 'selected_topic', 'status', 'model_used', 'generated_article', 'created_at')
    list_filter = ('status', 'generation_date', 'model_used')
    search_fields = ('selected_topic', 'error_message')
    readonly_fields = ('generation_date', 'selected_topic', 'status', 'error_message', 'generated_article', 'token_usage', 'model_used', 'created_at')

    def has_add_permission(self, request):
        return False


@admin.register(IntelSubscriber)
class IntelSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'ip_address', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('email', 'ip_address', 'created_at')
