from django.db import models
from salesforce_integration.models import StudentApplication


class Notification(models.Model):

    TYPE_CHOICES = [
        ('status_change', 'Status Change'),
        ('document_request', 'Document Request'),
        ('offer_received', 'Offer Received'),
        ('deadline_reminder', 'Deadline Reminder'),
        ('general', 'General'),
    ]

    application = models.ForeignKey(
        StudentApplication,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"{self.notification_type} - {self.application.student_name}"