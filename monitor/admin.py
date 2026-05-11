from django.contrib import admin

from .models import DrowsinessLog


@admin.register(DrowsinessLog)
class DrowsinessLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'status', 'ear_value')
    list_filter = ('status',)
    search_fields = ('status',)
