from django.contrib import admin
from .models import BlogCategory, BlogPost, SecurityNote


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_date', 'read_time_minutes', 'is_published', 'order')
    list_filter = ('category', 'is_published', 'published_date')
    search_fields = ('title', 'summary', 'content', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published', 'order')


@admin.register(SecurityNote)
class SecurityNoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_recorded', 'is_published', 'order')
    list_filter = ('category', 'is_published')
    search_fields = ('title', 'summary', 'key_takeaways')
    list_editable = ('is_published', 'order')
