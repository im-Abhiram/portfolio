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
        val = self.cleaned_data.get('website_url')
        if val:
            raise ValidationError("Automated transmission rejected by security filter.")
        return val

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise ValidationError("Name must be at least 2 characters.")
        # Reject simple script injection patterns
        if re.search(r'<script|javascript:|eval\(', name, re.IGNORECASE):
            raise ValidationError("Invalid input characters detected.")
        return name

    def clean_message(self):
        message = self.cleaned_data.get('message', '').strip()
        if len(message) < 10:
            raise ValidationError("Message payload must contain at least 10 characters.")
        if re.search(r'<script|javascript:|eval\(', message, re.IGNORECASE):
            raise ValidationError("Suspicious script tags are prohibited.")
        return message
