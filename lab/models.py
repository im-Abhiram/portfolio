from django.db import models


class NetworkKnowledgeTopic(models.Model):
    CATEGORY_CHOICES = [
        ('foundations', 'Foundations & Architecture'),
        ('addressing', 'Addressing & Subnetting'),
        ('switching_routing', 'Switching & Routing'),
        ('services_security', 'Services & Security'),
        ('operations', 'Operations & Diagnostics'),
    ]

    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='foundations')
    short_explanation = models.TextField()
    how_it_works = models.TextField()
    practical_use = models.TextField()
    troubleshooting_tip = models.TextField()
    relevant_tools = models.CharField(max_length=200, help_text="e.g. Wireshark, tcpdump, ping, traceroute, pfSense GUI")
    badge_tag = models.CharField(max_length=50, default="Core Protocol")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Networking Knowledge Topic"
        verbose_name_plural = "Networking Knowledge Topics"

    def __str__(self):
        return self.title

    def get_tools_list(self):
        return [t.strip() for t in self.relevant_tools.split(',') if t.strip()]


class SecurityTool(models.Model):
    CATEGORY_CHOICES = [
        ('recon', 'Reconnaissance & Discovery'),
        ('traffic', 'Packet & Traffic Analysis'),
        ('web', 'Web Application Security'),
        ('exploit', 'Controlled Exploitation & Auditing'),
        ('siem', 'Log Analysis & SIEM'),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='recon')
    purpose = models.TextField()
    how_i_used_it = models.TextField(
        help_text="Hands-on application based strictly on resume experience and labs"
    )
    typical_syntax = models.CharField(max_length=200, blank=True, help_text="Typical CLI invocation command")
    icon_class = models.CharField(max_length=50, default="bi-shield-check")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Cybersecurity Tool"
        verbose_name_plural = "Cybersecurity Tools"

    def __str__(self):
        return self.name


class SecurityConcept(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    vulnerability_type = models.CharField(max_length=100, default="Web Application Vulnerability")
    what_it_is = models.TextField()
    why_it_occurs = models.TextField()
    impact = models.TextField()
    prevention = models.TextField()
    defensive_detection_idea = models.TextField()
    owasp_reference = models.CharField(max_length=50, blank=True, default="OWASP Top 10")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Security Concept (Defensive)"
        verbose_name_plural = "Security Concepts (Defensive)"

    def __str__(self):
        return self.title
