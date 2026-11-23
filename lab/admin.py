from django.contrib import admin
from .models import NetworkKnowledgeTopic, SecurityTool, SecurityConcept


@admin.register(NetworkKnowledgeTopic)
class NetworkKnowledgeTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'badge_tag', 'relevant_tools', 'order')
    list_filter = ('category',)
    search_fields = ('title', 'short_explanation', 'how_it_works', 'troubleshooting_tip')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('order',)


@admin.register(SecurityTool)
class SecurityToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'typical_syntax', 'order')
    list_filter = ('category',)
    search_fields = ('name', 'purpose', 'how_i_used_it')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)


@admin.register(SecurityConcept)
class SecurityConceptAdmin(admin.ModelAdmin):
    list_display = ('title', 'vulnerability_type', 'owasp_reference', 'order')
    list_filter = ('vulnerability_type',)
    search_fields = ('title', 'what_it_is', 'prevention', 'defensive_detection_idea')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('order',)
