from django.db import models


class LoginAttemptLog(models.Model):
    """
    Lightweight SQLite ledger for tracking authentication attempts
    and enforcing brute-force rate limits on Operator Portal logins.
    Never logs passwords, session tokens, or secrets.
    """
    ip_address = models.GenericIPAddressField(db_index=True)
    username_attempted = models.CharField(max_length=150, db_index=True)
    succeeded = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Login Attempt Log"
        verbose_name_plural = "Login Attempt Logs"

    def __str__(self):
        outcome = "OK" if self.succeeded else "FAIL"
        return f"[{outcome}] {self.ip_address} ({self.username_attempted})"
