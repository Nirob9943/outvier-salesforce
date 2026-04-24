from django.db import models


class StudentApplication(models.Model):

    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('conditional_offer', 'Conditional Offer'),
        ('unconditional_offer', 'Unconditional Offer'),
        ('enrolled', 'Enrolled'),
        ('rejected', 'Rejected'),
    ]

    # Salesforce reference
    salesforce_id = models.CharField(max_length=255, unique=True)

    # Student details
    student_name = models.CharField(max_length=255)
    student_email = models.EmailField()
    student_id = models.CharField(max_length=100)

    # Application details
    application_status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='submitted'
    )
    course_name = models.CharField(max_length=255)
    intake_year = models.IntegerField()
    intake_semester = models.CharField(max_length=50)

    # Offer details
    offer_details = models.TextField(blank=True, null=True)
    offer_deadline = models.DateField(blank=True, null=True)

    # Document verification
    documents_verified = models.BooleanField(default=False)
    missing_documents = models.TextField(blank=True, null=True)

    # Communication
    last_communication = models.TextField(blank=True, null=True)
    admission_officer_notes = models.TextField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Student Application'
        verbose_name_plural = 'Student Applications'

    def __str__(self):
        return f"{self.student_name} - {self.course_name} ({self.application_status})"


class SyncLog(models.Model):

    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('partial', 'Partial'),
    ]

    sync_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    records_synced = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    synced_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-synced_at']
        verbose_name = 'Sync Log'
        verbose_name_plural = 'Sync Logs'

    def __str__(self):
        return f"Sync {self.sync_status} at {self.synced_at} - {self.records_synced} records"