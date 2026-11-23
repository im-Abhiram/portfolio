from django.contrib import admin
from .models import (
    Profile, Education, SkillCategory, Skill, Experience, Project,
    ProjectImage, Certification, SocialLink
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'title', 'location', 'email', 'phone')
    fieldsets = (
        ('Personal Identity', {
            'fields': ('full_name', 'title', 'hero_badge_label', 'location', 'email', 'phone', 'education_summary', 'profile_image')
        }),
        ('Headlines & Statements', {
            'fields': ('headline', 'secondary_statement', 'about_text')
        }),
    )

    def has_add_permission(self, request):
        return not Profile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'institution', 'location', 'completion_date', 'order')
    list_editable = ('order',)


class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    fields = ('name', 'proficiency_tag', 'icon', 'is_featured', 'order')


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'order')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SkillInline]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency_tag', 'is_featured', 'order')
    list_filter = ('category', 'is_featured')
    search_fields = ('name', 'description')
    list_editable = ('order', 'is_featured')


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('company', 'role', 'duration', 'location', 'is_current', 'order')
    list_filter = ('is_current',)
    search_fields = ('company', 'role', 'responsibilities')
    list_editable = ('order', 'is_current')


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'badge_label', 'is_featured', 'order')
    list_filter = ('category', 'is_featured', 'has_interactive_preview')
    search_fields = ('title', 'summary', 'technologies')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectImageInline]
    list_editable = ('order', 'is_featured')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'issuer', 'issue_date', 'order')
    search_fields = ('title', 'issuer', 'skills_covered')
    list_editable = ('order',)


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'icon', 'is_active', 'order')
    list_editable = ('is_active', 'order')
