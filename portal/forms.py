from django import forms
from portfolio.models import Profile, Project, Skill, Certification, Experience
from core.models import PortfolioSettings


class PortalLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'portal-input',
            'placeholder': 'Operator ID / Username',
            'autocomplete': 'username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'portal-input',
            'placeholder': 'Authorization Key / Password',
            'autocomplete': 'current-password',
        })
    )
    captcha = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'portal-input',
            'placeholder': 'Enter Security Code Shown Above',
            'autocomplete': 'off',
            'spellcheck': 'false',
        })
    )


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'full_name', 'title', 'hero_badge_label', 'headline',
            'secondary_statement', 'about_text', 'location', 'email',
            'phone', 'education_summary', 'profile_image'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'portal-input'}),
            'title': forms.TextInput(attrs={'class': 'portal-input'}),
            'hero_badge_label': forms.TextInput(attrs={'class': 'portal-input'}),
            'headline': forms.TextInput(attrs={'class': 'portal-input'}),
            'secondary_statement': forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 3}),
            'about_text': forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 6}),
            'location': forms.TextInput(attrs={'class': 'portal-input'}),
            'email': forms.EmailInput(attrs={'class': 'portal-input'}),
            'phone': forms.TextInput(attrs={'class': 'portal-input'}),
            'education_summary': forms.TextInput(attrs={'class': 'portal-input'}),
            'profile_image': forms.FileInput(attrs={'class': 'portal-file-input'}),
        }


class PortfolioSettingsEditForm(forms.ModelForm):
    class Meta:
        model = PortfolioSettings
        fields = [
            'site_title', 'brand_tagline', 'noc_status_text', 'location_label',
            'resume_file', 'resume_download_name', 'show_lab_section',
            'show_journal_section', 'show_terminal_feature', 'show_certifications',
            'show_activity_wall'
        ]
        widgets = {
            'site_title': forms.TextInput(attrs={'class': 'portal-input'}),
            'brand_tagline': forms.TextInput(attrs={'class': 'portal-input'}),
            'noc_status_text': forms.TextInput(attrs={'class': 'portal-input'}),
            'location_label': forms.TextInput(attrs={'class': 'portal-input'}),
            'resume_file': forms.FileInput(attrs={'class': 'portal-file-input'}),
            'resume_download_name': forms.TextInput(attrs={'class': 'portal-input'}),
            'show_lab_section': forms.CheckboxInput(attrs={'class': 'portal-switch'}),
            'show_journal_section': forms.CheckboxInput(attrs={'class': 'portal-switch'}),
            'show_terminal_feature': forms.CheckboxInput(attrs={'class': 'portal-switch'}),
            'show_certifications': forms.CheckboxInput(attrs={'class': 'portal-switch'}),
            'show_activity_wall': forms.CheckboxInput(attrs={'class': 'portal-switch'}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title', 'slug', 'category', 'badge_label', 'summary',
            'architecture', 'key_features', 'challenges_and_solutions',
            'technologies', 'github_url', 'demo_url', 'has_interactive_preview',
            'order', 'is_featured'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'portal-input'}),
            'slug': forms.TextInput(attrs={'class': 'portal-input'}),
            'category': forms.TextInput(attrs={'class': 'portal-input'}),
            'badge_label': forms.TextInput(attrs={'class': 'portal-input'}),
            'summary': forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 3}),
            'architecture': forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 4}),
            'key_features': forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 4, 'placeholder': 'One feature per line'}),
            'challenges_and_solutions': forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 3}),
            'technologies': forms.TextInput(attrs={'class': 'portal-input', 'placeholder': 'e.g. Python, Django, SQLite3, Bootstrap'}),
            'github_url': forms.URLInput(attrs={'class': 'portal-input', 'placeholder': 'https://github.com/...'}),
            'demo_url': forms.URLInput(attrs={'class': 'portal-input', 'placeholder': 'https://...'}),
            'has_interactive_preview': forms.CheckboxInput(attrs={'class': 'portal-switch'}),
            'order': forms.NumberInput(attrs={'class': 'portal-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'portal-switch'}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['category', 'name', 'proficiency_tag', 'icon', 'description', 'is_featured', 'order']
        widgets = {
            'category': forms.Select(attrs={'class': 'portal-select'}),
            'name': forms.TextInput(attrs={'class': 'portal-input'}),
            'proficiency_tag': forms.TextInput(attrs={'class': 'portal-input', 'placeholder': 'e.g. Core Competency, Specialized'}),
            'icon': forms.TextInput(attrs={'class': 'portal-input', 'placeholder': 'e.g. bi-shield-check'}),
            'description': forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 3}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'portal-switch'}),
            'order': forms.NumberInput(attrs={'class': 'portal-input'}),
        }


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['title', 'issuer', 'issue_date', 'credential_url', 'badge_icon', 'skills_covered', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'portal-input'}),
            'issuer': forms.TextInput(attrs={'class': 'portal-input'}),
            'issue_date': forms.TextInput(attrs={'class': 'portal-input', 'placeholder': 'e.g. Dec 2024'}),
            'credential_url': forms.URLInput(attrs={'class': 'portal-input', 'placeholder': 'https://...'}),
            'badge_icon': forms.TextInput(attrs={'class': 'portal-input', 'placeholder': 'e.g. bi-patch-check-fill'}),
            'skills_covered': forms.TextInput(attrs={'class': 'portal-input', 'placeholder': 'e.g. Penetration Testing, OWASP Top 10'}),
            'description': forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 3}),
            'order': forms.NumberInput(attrs={'class': 'portal-input'}),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['company', 'role', 'employment_type', 'duration', 'location', 'is_current', 'summary', 'responsibilities', 'technologies', 'order']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'portal-input'}),
            'role': forms.TextInput(attrs={'class': 'portal-input'}),
            'employment_type': forms.TextInput(attrs={'class': 'portal-input'}),
            'duration': forms.TextInput(attrs={'class': 'portal-input', 'placeholder': 'e.g. Nov 2025 – Present'}),
            'location': forms.TextInput(attrs={'class': 'portal-input'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'portal-switch'}),
            'summary': forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 3}),
            'responsibilities': forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 4, 'placeholder': 'One bullet point per line'}),
            'technologies': forms.TextInput(attrs={'class': 'portal-input', 'placeholder': 'Comma-separated list'}),
            'order': forms.NumberInput(attrs={'class': 'portal-input'}),
        }
