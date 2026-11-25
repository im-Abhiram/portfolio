from django.db import models
from django.utils import timezone


class ChatUsageLog(models.Model):
    """
    Anonymized rate-limiting and daily quota ledger for NEXUS AI.
    Intentionally does NOT store visitor prompts, messages, or AI replies.
    """
    ip_address = models.GenericIPAddressField(db_index=True)
    session_hash = models.CharField(max_length=32, db_index=True)
    usage_date = models.DateField(default=timezone.localdate, db_index=True)
    status = models.CharField(max_length=30, default='ok')
    model_used = models.CharField(max_length=80, blank=True)
    total_tokens = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "NEXUS AI Usage Log"
        verbose_name_plural = "NEXUS AI Usage Logs"

    def __str__(self):
        return f"{self.usage_date} | {self.ip_address} | {self.status}"
