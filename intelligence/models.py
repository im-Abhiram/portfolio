import hashlib
import os
from django.db import models
from django.utils import timezone


class AISettings(models.Model):
    """
    Singleton non-secret AI configuration manageable via Admin.
    NEVER stores API keys or credentials.
    """
    PUBLISH_MODES = [
        ('auto', 'Automatic Publishing'),
        ('review', 'Review Before Publishing'),
        ('manual', 'Manual Publishing (Save as Draft)'),
    ]

    chat_enabled = models.BooleanField(
        default=True,
        help_text="Master toggle for NEXUS AI Chatbot widget."
    )
    daily_article_enabled = models.BooleanField(
        default=True,
        help_text="Enable Network Intelligence daily AI article publisher."
    )
    article_publish_mode = models.CharField(
        max_length=20,
        choices=PUBLISH_MODES,
        default='review',
        help_text="Controls initial status of AI-generated daily articles."
    )
    chat_daily_limit_per_visitor = models.PositiveIntegerField(
        default=10,
        help_text="Max daily NEXUS AI messages allowed per visitor IP/session."
    )
    chat_rate_limit_per_minute = models.PositiveIntegerField(
        default=6,
        help_text="Max NEXUS AI requests per minute per IP."
    )
    article_generation_timezone = models.CharField(
        max_length=50,
        default='Asia/Kolkata',
        help_text="IANA timezone used to determine daily schedule dates."
    )
    preferred_model = models.CharField(
        max_length=80,
        blank=True,
        default='',
        help_text="Optional Flash model override (e.g. gemini-3.5-flash-lite). Leave blank to use GEMINI_MODEL env var."
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "AI Configuration (Non-Secret)"
        verbose_name_plural = "AI Configuration (Non-Secret)"

    def __str__(self):
        return "Global AI Feature Settings"

    @property
    def api_key_configured(self) -> bool:
        return bool(os.environ.get('GEMINI_API_KEY', '').strip())

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        env_chat = os.environ.get('GEMINI_CHAT_ENABLED', 'True').strip().lower() in ('true', '1', 'yes')
        env_art = os.environ.get('GEMINI_DAILY_ARTICLE_ENABLED', 'True').strip().lower() in ('true', '1', 'yes')
        env_mode = os.environ.get('GEMINI_ARTICLE_PUBLISH_MODE', 'review').strip().lower()
        if env_mode not in ('auto', 'review', 'manual'):
            env_mode = 'review'
        try:
            env_limit = max(1, int(os.environ.get('GEMINI_DAILY_REQUEST_LIMIT', '10') or 10))
        except ValueError:
            env_limit = 10

        obj, created = cls.objects.get_or_create(
            pk=1,
            defaults={
                'chat_enabled': env_chat,
                'daily_article_enabled': env_art,
                'article_publish_mode': env_mode,
                'chat_daily_limit_per_visitor': env_limit,
            }
        )
        return obj


class DailyArticle(models.Model):
    """
    Structured technical publication model for NETWORK INTELLIGENCE.
    Stores validated content blocks safely in JSON without blindly trusting raw AI HTML.
    """
    CATEGORY_CHOICES = [
        ('Networking', 'Networking'),
        ('Network Security', 'Network Security'),
        ('Cybersecurity', 'Cybersecurity'),
        ('System Administration', 'System Administration'),
        ('Web Application Security', 'Web Application Security'),
        ('IT Infrastructure', 'IT Infrastructure'),
        ('Python & Development', 'Python & Development'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending Review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=260, unique=True)
    subtitle = models.CharField(max_length=320)
    introduction = models.TextField()
    content = models.JSONField(
        default=dict,
        help_text="Structured validated sections: what_is_it, how_it_works, technical_explanation, practical_example, commands_and_configs, security_implications, common_mistakes, prevention_best_practices, key_takeaways, further_learning."
    )
    category = models.CharField(max_length=80, choices=CATEGORY_CHOICES, default='Networking', db_index=True)
    tags = models.CharField(max_length=300, blank=True, help_text="Comma-separated tags")
    cover_image = models.ImageField(upload_to='intelligence/covers/', blank=True, null=True)
    reading_time = models.PositiveIntegerField(default=6, help_text="Estimated reading time in minutes")

    scheduled_date = models.DateField(
        null=True,
        blank=True,
        unique=True,
        help_text="Prevents duplicate daily generation for the same calendar date."
    )
    topic_key = models.CharField(max_length=150, blank=True, db_index=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_review', db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    ai_generated = models.BooleanField(default=True)
    content_hash = models.CharField(max_length=64, unique=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-generated_at']
        verbose_name = "Daily Intelligence Article"
        verbose_name_plural = "Daily Intelligence Articles"

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title}"

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    def compute_content_hash(self) -> str:
        body_part = str(self.content.get('what_is_it', '')) + str(self.content.get('technical_explanation', ''))
        normalized = ' '.join(f"{self.title} {self.introduction} {body_part}".lower().split())
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        if not self.content_hash:
            self.content_hash = self.compute_content_hash()
        if self.status == 'published' and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)


class ArticleGenerationLog(models.Model):
    """Audit trail for daily article generation attempts without storing secrets."""
    LOG_STATUS_CHOICES = [
        ('success', 'Success'),
        ('skipped', 'Skipped (Already Exists)'),
        ('failed', 'Failed'),
        ('duplicate_blocked', 'Duplicate Blocked'),
    ]

    generation_date = models.DateField(db_index=True)
    selected_topic = models.CharField(max_length=255)
    status = models.CharField(max_length=30, choices=LOG_STATUS_CHOICES, db_index=True)
    error_message = models.TextField(blank=True)
    generated_article = models.ForeignKey(
        DailyArticle,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generation_logs'
    )
    token_usage = models.JSONField(default=dict, blank=True)
    model_used = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Article Generation Log"
        verbose_name_plural = "Article Generation Logs"

    def __str__(self):
        return f"{self.generation_date} | {self.selected_topic} [{self.status}]"


class IntelSubscriber(models.Model):
    """
    Local watchlist registry for Network Intelligence updates.
    Stored only in local SQLite; does not dispatch automated outbound emails without SMTP setup.
    """
    email = models.EmailField(max_length=180, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Intelligence Watchlist Subscriber"
        verbose_name_plural = "Intelligence Watchlist Subscribers"

    def __str__(self):
        return self.email
