from django.db import models
from django.core.validators import FileExtensionValidator


class PortfolioSettings(models.Model):
    site_title = models.CharField(
        max_length=120,
        default="Abhiram Anil | IT Infrastructure & Cybersecurity Portfolio"
    )
    brand_tagline = models.CharField(
        max_length=200,
        default="Building, connecting and securing digital infrastructure."
    )
    noc_status_text = models.CharField(
        max_length=100,
        default="SYS_OPERATIONAL // NOC MONITORING ACTIVE"
    )
    location_label = models.CharField(
        max_length=100,
        default="Kerala, India [UTC+05:30]"
    )
    resume_file = models.FileField(
        upload_to='resumes/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])],
        help_text="Upload your resume document (PDF or DOCX)."
    )
    resume_download_name = models.CharField(
        max_length=100,
        default="Abhiram_Anil_Resume.pdf",
        help_text="Filename suggested when visitor downloads your resume."
    )
    show_lab_section = models.BooleanField(default=True)
    show_journal_section = models.BooleanField(default=True)
    show_terminal_feature = models.BooleanField(default=True)
    show_certifications = models.BooleanField(default=True)
    show_activity_wall = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Portfolio Settings"
        verbose_name_plural = "Portfolio Settings"

    def __str__(self):
        return f"{self.site_title} (Active Settings)"

    def save(self, *args, **kwargs):
        # Ensure singleton: only one settings instance exists
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
