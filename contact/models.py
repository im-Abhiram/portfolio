from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150)
    subject = models.CharField(max_length=150)
    message = models.TextField(max_length=3000)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True, help_text="Internal notes for admin reference")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        status = "READ" if self.is_read else "NEW"
        return f"[{status}] {self.subject} from {self.name} ({self.created_at.strftime('%Y-%m-%d')})"
