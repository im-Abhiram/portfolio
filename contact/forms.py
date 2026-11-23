from django import forms
from django.core.exceptions import ValidationError
from .models import ContactMessage
import re


class ContactForm(forms.ModelForm):
    # Honeypot field: bots fill this, humans don't see it (hidden via CSS/inline)
    website_url = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'tabindex': '-1',
            'style': 'position: absolute; left: -9999px; width: 1px; height: 1px; opacity: 0;'
        })
    )

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control noc-input',
                'placeholder': 'Your Full Name or Handle',
                'maxlength': '100',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control noc-input',
                'placeholder': 'your.email@organization.com',
                'maxlength': '150',
                'required': True,
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control noc-input',
                'placeholder': 'Infrastructure Consultation / Incident Inquiry / Collaboration',
                'maxlength': '150',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control noc-input',
                'placeholder': 'Provide mission details, technical context, or message payload...',
                'rows': 5,
                'maxlength': '3000',
                'required': True,
            }),
        }

    def clean_website_url(self):
        val = self.cleaned_data.get('website_url', '').strip()
        if val:
            raise ValidationError("Automated transmission rejected by security filter.")
        return val

    def clean_name(self):
        raw_name = self.cleaned_data.get('name', '').strip()
        if len(raw_name) < 2:
            raise ValidationError("Name must be at least 2 characters.")
        if len(raw_name) > 100:
            raise ValidationError("Name cannot exceed 100 characters.")
        # Reject header injection / control characters
        if any(c in raw_name for c in ('\r', '\n', '\0')):
            raise ValidationError("Control characters are strictly prohibited.")
        # Strip and reject HTML/script tags
        cleaned = re.sub(r'<[^>]*>', '', raw_name)
        if re.search(r'(<script|javascript:|eval\(|onerror=|onload=)', raw_name, re.IGNORECASE):
            raise ValidationError("Invalid input characters detected.")
        return cleaned

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError("Email is required.")
        # Header injection defense
        if any(c in email for c in ('\r', '\n', '\0')):
            raise ValidationError("Invalid characters detected in email.")
        return email

    def clean_subject(self):
        raw_subject = self.cleaned_data.get('subject', '').strip()
        if len(raw_subject) < 3:
            raise ValidationError("Subject must be at least 3 characters.")
        if len(raw_subject) > 150:
            raise ValidationError("Subject cannot exceed 150 characters.")
        # Reject header injection
        if any(c in raw_subject for c in ('\r', '\n', '\0')):
            raise ValidationError("Control characters are prohibited in subject line.")
        cleaned = re.sub(r'<[^>]*>', '', raw_subject)
        if re.search(r'(<script|javascript:|eval\(|onerror=|onload=)', raw_subject, re.IGNORECASE):
            raise ValidationError("Invalid characters detected in subject.")
        return cleaned

    def clean_message(self):
        raw_message = self.cleaned_data.get('message', '').strip()
        if len(raw_message) < 10:
            raise ValidationError("Message payload must contain at least 10 characters.")
        if len(raw_message) > 3000:
            raise ValidationError("Message payload cannot exceed 3000 characters.")
        if '\0' in raw_message:
            raise ValidationError("Null byte characters are prohibited.")
        if re.search(r'(<script|javascript:|eval\(|onerror=|onload=)', raw_message, re.IGNORECASE):
            raise ValidationError("Suspicious script tags are prohibited.")
        cleaned = re.sub(r'<[^>]*>', '', raw_message)
        return cleaned
