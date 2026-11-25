import json
import re
from django import forms
from django.utils import timezone
from django.utils.text import slugify
from portfolio.models import Profile, Project, Skill, Certification, Experience
from core.models import PortfolioSettings
from intelligence.models import AISettings, DailyArticle
from journal.models import BlogPost


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


class AISettingsForm(forms.ModelForm):
    class Meta:
        model = AISettings
        fields = [
            'chat_enabled',
            'daily_article_enabled',
            'article_publish_mode',
            'chat_daily_limit_per_visitor',
            'chat_rate_limit_per_minute',
            'article_generation_timezone',
            'preferred_model',
        ]
        widgets = {
            'chat_enabled': forms.CheckboxInput(attrs={'class': 'portal-switch'}),
            'daily_article_enabled': forms.CheckboxInput(attrs={'class': 'portal-switch'}),
            'article_publish_mode': forms.Select(attrs={'class': 'portal-select'}),
            'chat_daily_limit_per_visitor': forms.NumberInput(attrs={'class': 'portal-input', 'min': 1, 'max': 200}),
            'chat_rate_limit_per_minute': forms.NumberInput(attrs={'class': 'portal-input', 'min': 1, 'max': 60}),
            'article_generation_timezone': forms.TextInput(attrs={'class': 'portal-input'}),
            'preferred_model': forms.TextInput(attrs={'class': 'portal-input', 'placeholder': 'e.g. gemini-3.5-flash-lite'}),
        }

    def clean_preferred_model(self):
        val = (self.cleaned_data.get('preferred_model') or '').strip()
        if val and not re.fullmatch(r'[a-zA-Z0-9._\-]{3,64}', val):
            raise forms.ValidationError("Invalid model identifier format (alphanumeric, '.', '_', '-' only).")
        return val


class DailyArticleForm(forms.ModelForm):
    """Structured editor for NETWORK INTELLIGENCE articles in the Admin Portal."""
    what_is_it = forms.CharField(
        label="What Is the Concept?",
        widget=forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 4}),
    )
    how_it_works = forms.CharField(
        label="How Does It Work?",
        widget=forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 4}),
    )
    technical_explanation = forms.CharField(
        label="Technical Explanation",
        widget=forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 5}),
    )
    practical_example = forms.CharField(
        label="Practical Real-World Example",
        widget=forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 4}),
    )
    commands_json = forms.CharField(
        label="Relevant Commands & Configurations (JSON Array)",
        required=False,
        help_text='JSON list of objects: [{"explanation": "...", "command": "...", "environment_note": "Lab Example"}]',
        widget=forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 6, 'style': 'font-family: var(--font-mono); font-size: 0.82rem;'}),
    )
    security_implications = forms.CharField(
        label="Security Implications",
        widget=forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 4}),
    )
    common_mistakes_text = forms.CharField(
        label="Common Mistakes (One per line)",
        required=False,
        widget=forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 4, 'placeholder': 'One mistake per line'}),
    )
    best_practices_text = forms.CharField(
        label="Prevention & Best Practices (One per line)",
        required=False,
        widget=forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 4, 'placeholder': 'One best practice per line'}),
    )
    key_takeaways_text = forms.CharField(
        label="Key Takeaways (One per line)",
        required=False,
        widget=forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 4, 'placeholder': 'One takeaway per line'}),
    )
    further_learning_text = forms.CharField(
        label="Suggested Further Learning (One per line)",
        required=False,
        widget=forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 3, 'placeholder': 'One study topic per line'}),
    )

    class Meta:
        model = DailyArticle
        fields = [
            'title', 'slug', 'subtitle', 'category', 'status',
            'scheduled_date', 'reading_time', 'tags', 'cover_image',
            'is_featured', 'introduction',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'portal-input'}),
            'slug': forms.TextInput(attrs={'class': 'portal-input', 'placeholder': 'Leave blank to auto-generate'}),
            'subtitle': forms.TextInput(attrs={'class': 'portal-input'}),
            'category': forms.Select(attrs={'class': 'portal-select'}),
            'status': forms.Select(attrs={'class': 'portal-select'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'portal-input', 'type': 'date'}),
            'reading_time': forms.NumberInput(attrs={'class': 'portal-input', 'min': 1, 'max': 60}),
            'tags': forms.TextInput(attrs={'class': 'portal-input', 'placeholder': 'Comma-separated tags'}),
            'cover_image': forms.FileInput(attrs={'class': 'portal-file-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'portal-switch'}),
            'introduction': forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        if self.instance and self.instance.pk and isinstance(self.instance.content, dict):
            c = self.instance.content
            self.fields['what_is_it'].initial = c.get('what_is_it', '')
            self.fields['how_it_works'].initial = c.get('how_it_works', '')
            self.fields['technical_explanation'].initial = c.get('technical_explanation', '')
            self.fields['practical_example'].initial = c.get('practical_example', '')
            self.fields['commands_json'].initial = json.dumps(c.get('commands_and_configs', []), indent=2)
            self.fields['security_implications'].initial = c.get('security_implications', '')
            self.fields['common_mistakes_text'].initial = '\n'.join(c.get('common_mistakes', []))
            self.fields['best_practices_text'].initial = '\n'.join(c.get('prevention_best_practices', []))
            self.fields['key_takeaways_text'].initial = '\n'.join(c.get('key_takeaways', []))
            self.fields['further_learning_text'].initial = '\n'.join(c.get('further_learning', []))

    def clean_commands_json(self):
        raw = (self.cleaned_data.get('commands_json') or '').strip()
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError(f"Invalid JSON in Commands & Configurations: {exc}")
        if not isinstance(parsed, list):
            raise forms.ValidationError("Commands & Configurations must be a JSON array [...].")
        clean_list = []
        for item in parsed:
            if isinstance(item, dict):
                clean_list.append({
                    'explanation': str(item.get('explanation', '')).strip(),
                    'command': str(item.get('command', '')).strip(),
                    'environment_note': str(item.get('environment_note', 'Lab / Educational Example')).strip(),
                })
        return clean_list

    def save(self, commit=True):
        article = super().save(commit=False)
        if not article.slug:
            base = slugify(article.title)[:220] or 'network-intelligence'
            slug_cand = base
            idx = 2
            while DailyArticle.objects.filter(slug=slug_cand).exclude(pk=article.pk).exists():
                slug_cand = f"{base[:210]}-{idx}"
                idx += 1
            article.slug = slug_cand

        def _lines(key):
            return [line.strip() for line in (self.cleaned_data.get(key) or '').splitlines() if line.strip()]

        article.content = {
            'what_is_it': self.cleaned_data.get('what_is_it', '').strip(),
            'how_it_works': self.cleaned_data.get('how_it_works', '').strip(),
            'technical_explanation': self.cleaned_data.get('technical_explanation', '').strip(),
            'practical_example': self.cleaned_data.get('practical_example', '').strip(),
            'commands_and_configs': self.cleaned_data.get('commands_json', []),
            'security_implications': self.cleaned_data.get('security_implications', '').strip(),
            'common_mistakes': _lines('common_mistakes_text'),
            'prevention_best_practices': _lines('best_practices_text'),
            'key_takeaways': _lines('key_takeaways_text'),
            'further_learning': _lines('further_learning_text'),
        }
        article.content_hash = article.compute_content_hash()
        if article.status == 'published' and not article.published_at:
            article.published_at = timezone.now()
        if commit:
            if article.is_featured and article.status == 'published':
                DailyArticle.objects.exclude(pk=article.pk).filter(is_featured=True).update(is_featured=False)
            article.save()
        return article


class ArticleImportForm(forms.Form):
    scheduled_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'portal-input', 'type': 'date'}),
        help_text="Optional calendar date to assign (YYYY-MM-DD)."
    )
    status = forms.ChoiceField(
        choices=DailyArticle.STATUS_CHOICES,
        initial='pending_review',
        widget=forms.Select(attrs={'class': 'portal-select'}),
    )
    json_payload = forms.CharField(
        label="Article JSON Content",
        widget=forms.Textarea(attrs={
            'class': 'portal-textarea',
            'rows': 12,
            'style': 'font-family: var(--font-mono); font-size: 0.82rem;',
            'placeholder': 'Paste structured article JSON exported by `python manage.py generate_daily_article --export-json ...`'
        }),
    )


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'slug', 'category', 'summary', 'content', 'tags', 'read_time_minutes', 'published_date', 'is_published', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'portal-input'}),
            'slug': forms.TextInput(attrs={'class': 'portal-input'}),
            'category': forms.Select(attrs={'class': 'portal-select'}),
            'summary': forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 3}),
            'content': forms.Textarea(attrs={'class': 'portal-textarea', 'rows': 8}),
            'tags': forms.TextInput(attrs={'class': 'portal-input', 'placeholder': 'Comma-separated tags'}),
            'read_time_minutes': forms.NumberInput(attrs={'class': 'portal-input'}),
            'published_date': forms.DateInput(attrs={'class': 'portal-input', 'type': 'date'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'portal-switch'}),
            'order': forms.NumberInput(attrs={'class': 'portal-input'}),
        }
