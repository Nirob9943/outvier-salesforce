from django.contrib import admin
from .models import StudentApplication, SyncLog


@admin.register(StudentApplication)
class StudentApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'student_name',
        'student_email',
        'course_name',
        'application_status',
        'documents_verified',
        'last_synced'
    ]
    list_filter = ['application_status', 'documents_verified', 'intake_year']
    search_fields = ['student_name', 'student_email', 'student_id', 'salesforce_id']
    readonly_fields = ['created_at', 'updated_at', 'last_synced']
    ordering = ['-updated_at']


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['sync_status', 'records_synced', 'records_failed', 'synced_at']
    list_filter = ['sync_status']
    readonly_fields = ['synced_at']