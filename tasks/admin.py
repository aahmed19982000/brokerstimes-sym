from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('writer', 'article_title', 'publish_site', 'publish_date','article_type_W_R_A_B',)
    search_fields = ('article_title', 'publish_site')
