from django.db import models
from django.utils import timezone


class BlogCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)

    class Meta:
        verbose_name = "Journal Category"
        verbose_name_plural = "Journal Categories"

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    category = models.ForeignKey(BlogCategory, related_name='posts', on_delete=models.CASCADE)
    summary = models.TextField(help_text="Short abstract / teaser")
    content = models.TextField(help_text="Full technical writeup")
    read_time_minutes = models.PositiveIntegerField(default=5)
    tags = models.CharField(max_length=200, help_text="Comma-separated tags")
    published_date = models.DateField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-published_date']
        verbose_name = "Field Note / Article"
        verbose_name_plural = "Field Notes / Articles"

    def __str__(self):
        return self.title

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]


class SecurityNote(models.Model):
    CATEGORY_CHOICES = [
        ('hardening', 'Infrastructure Hardening'),
        ('recon', 'Reconnaissance & Mapping'),
        ('auditing', 'Network Auditing'),
        ('operations', 'Operations & Logging'),
        ('appsec', 'Web App Vulnerability Analysis'),
    ]

    title = models.CharField(max_length=150)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='hardening')
    summary = models.TextField()
    key_takeaways = models.TextField(help_text="Bullet points separated by newlines")
    date_recorded = models.DateField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', '-date_recorded']
        verbose_name = "Security Research Note"
        verbose_name_plural = "Security Research Notes"

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

    def get_takeaways_list(self):
        return [t.strip() for t in self.key_takeaways.split('\n') if t.strip()]
