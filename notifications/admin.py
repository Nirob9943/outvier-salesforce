from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'notification_type', 'application', 'is_sent', 'created_at']
    list_filter = ['notification_type', 'is_sent']
    search_fields = ['title', 'application__student_name']
    readonly_fields = ['created_at', 'sent_at']